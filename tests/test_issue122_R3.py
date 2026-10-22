# this_file: tests/test_issue122_R3.py
"""Check explicit encoding plans, real history, host shapes and source coverage."""

import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import os
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest
from fontlabapp.names_edit import Facts

from historical_sources import archived_source, recorded_sha256, recorded_sources

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Tools/Apply Unicode Map.py"
COPY = ROOT / "Scripts/Tools/Copy Layers From Font.py"
SCALE = ROOT / "Scripts/Drawing/Scale With Stem Compensation.py"
COLLISIONS = {
    "render",
    "size",
    "layout",
    "update",
    "font",
    "move",
    "statusBar",
    "geometry",
    "close",
    "width",
    "height",
    "data",
    "children",
}


def load(path: Path = SCRIPT) -> Any:
    spec = importlib.util.spec_from_file_location("r3_tool", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_panel_type() -> type:
    return object


def facts(codes: dict[str, list[int]], auto: tuple[str, ...] = ()) -> Any:
    from fontlabapp.history import auto_facts
    from fontlabapp.names_edit import Entry, Facts

    entries = {}
    for name, points in codes.items():
        layer = Owned("Regular")
        layer.autoLayer = name in auto
        glyph = Owned(name)
        glyph.layers = [layer]
        entries[name] = Entry(name, NS(unicodes=list(points)), glyph)
    return Facts(NS(id=9), 9, entries, auto_facts((n, n in auto, ()) for n in codes))


class Owned:
    def __init__(self, name: str) -> None:
        self.name, self.autoLayer, self.isNull = name, False, False
        self.histories: list[int] = []
        self.lastModified = None

    def checkInitHistoryState(self, index: int) -> None:
        self.histories.append(index)


@pytest.mark.parametrize("script", [SCRIPT, COPY, SCALE])
def test_real_app_names_when_installed_then_all_used_names_exist(script: Path) -> None:
    tree = ast.parse(script.read_text())
    aliases = {
        a.asname: a.name
        for n in ast.walk(tree)
        if isinstance(n, ast.Import)
        for a in n.names
        if a.name.startswith("fly.ap.")
    }
    if script == SCRIPT:
        assert set(aliases.values()) == {
            "fly.ap.names_edit",
            "fly.ap.selection_panel",
            "fly.ap.scripting",
        }
    app_root = Path(importlib.import_module("fontlabapp").__file__).resolve().parent
    assert "site-packages" in str(app_root), "Use a non-editable installed App"
    assert importlib.import_module("fly").ALIASES["ap"] == "fontlabapp"
    for alias, name in aliases.items():
        real = importlib.import_module(name)
        assert real is importlib.import_module(name.replace("fly.ap.", "fontlabapp."))
        assert Path(real.__file__).resolve().is_relative_to(app_root)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == alias
            ):
                assert hasattr(real, node.attr), f"Missing {name}.{node.attr}"


def test_fake_signatures_when_used_then_match_real_app() -> None:
    from fontlabapp.selection_panel import panel_type

    assert inspect.signature(fake_panel_type) == inspect.signature(panel_type)


def test_script_when_parsed_then_no_native_class_member_shadowing() -> None:
    tree = ast.parse(SCRIPT.read_text(), feature_version=(3, 11))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert not (
                {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                & COLLISIONS
            )
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            assert node.attr not in COLLISIONS


@pytest.mark.parametrize(
    "text, expected",
    [
        ('{"A":"0041"}', {"A": (65,)}),
        ('{"a":[97,"0062",97]}', {"a": (97, 98)}),
        ('{"smile":"1F600"}', {"smile": (0x1F600,)}),
    ],
)
def test_map_when_valid_then_normalized(text: str, expected: dict) -> None:
    assert load().parse_map(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        "[]",
        "{}",
        '{"A":true}',
        '{"A":-1}',
        '{"A":1114112}',
        '{"A":"D800"}',
        '{"A":[]}',
        '{"A":1.5}',
        '{"A":1,"A":2}',
        '{"A B":65}',
        '{"A":"xyz"}',
        '{"A":null}',
        '{"A\\u00a0":65}',
    ],
)
def test_map_when_invalid_then_refused(text: str) -> None:
    with pytest.raises(ValueError):
        load().parse_map(text)


def test_plan_when_refused_or_unknown_then_kept_and_other_glyph_writes() -> None:
    rows = load().plan_map(
        facts({"A": [65], "B": [], "C": []}, ("C",)),
        ["A", "B", "C"],
        {"A": (66,), "B": (67,), "C": (68,), "D": (69,)},
    )
    assert [(r["name"], r["after"], bool(r["note"])) for r in rows] == [
        ("A", (65, 66), False),
        ("B", (67,), False),
        ("C", (), True),
        ("D", (), True),
    ]


def test_plan_when_unicode_claimed_then_keep_conflicting_rows() -> None:
    rows = load().plan_map(
        facts({"A": [65], "B": [], "C": []}), ["B", "C"], {"B": (65,), "C": (65,)}
    )
    assert all(r["note"] and not r["after"] for r in rows)


@pytest.mark.parametrize("failure", ["", "pending", "notify", "readback"])
def test_write_when_valid_then_real_history_one_notification(
    monkeypatch: Any, failure: str
) -> None:
    import fontlabapp.edit_guards as guards
    import fontlabapp.history as history  # noqa: PLR0402 - preserve module import
    import fontlabapp.names_edit as names

    f = facts({"A": [], "B": []}, ("B",))
    calls = []

    class Unstored:
        @property
        def unicodes(self) -> list[int]:
            return []

        @unicodes.setter
        def unicodes(self, values: list[int]) -> None:
            pass

    if failure == "readback":
        object.__setattr__(f.entries["A"], "record", Unstored())

    def notify(*args: Any) -> None:
        calls.append(args)
        if failure == "notify":
            raise RuntimeError("Injected notification failure")

    native = NS(
        flGlyph=NS(updatedFgGlyphs=lambda: [7] if failure == "pending" else []),
        flItems=lambda: NS(notifyChangesApplied=notify),
    )
    monkeypatch.setattr(
        history,
        "_native",
        lambda name: (
            native
            if name == "fontlab"
            else NS(QtCore=NS(QDateTime=NS(currentDateTimeUtc=lambda: "stamp")))
        ),
    )

    def selection_window(package_id: int) -> None:
        assert package_id == 9

    def no_editors(*, qt: Any = None, deadline: float | None = None) -> None:
        pass

    def fresh_facts(package_id: int, *, native: Any = None) -> Facts:
        assert package_id == 9
        return f

    for real, fake in (
        (guards.require_selection_window, selection_window),
        (guards.require_no_editors, no_editors),
        (names.fresh_facts, fresh_facts),
    ):
        assert inspect.signature(real) == inspect.signature(fake)
    monkeypatch.setattr(guards, "require_selection_window", selection_window)
    monkeypatch.setattr(guards, "require_no_editors", no_editors)
    monkeypatch.setattr(names, "fresh_facts", fresh_facts)
    module = load()
    rows = module.plan_map(f, ["A", "B"], {"A": (65,), "B": (66,)})
    if failure and failure != "pending":
        error_type = RuntimeError
        with pytest.raises(error_type) as caught:
            module.write_map(9, ["A", "B"], {"A": (65,), "B": (66,)}, rows)
        if failure == "pending":
            assert not calls
            assert f.entries["A"].glyph.histories == []
        else:
            assert "use Edit > Undo" in str(caught.value)
            assert len(calls) == 1
        return
    result = module.write_map(9, ["A", "B"], {"A": (65,), "B": (66,)}, rows)
    assert result["changed"] == 1
    assert result["pending_updates"] == ((7,) if failure == "pending" else ())
    assert native.flGlyph.updatedFgGlyphs() == ([7] if failure == "pending" else [])
    assert f.entries["A"].record.unicodes == [65]
    assert f.entries["B"].record.unicodes == []
    assert len(calls) == 1
    assert calls[0][1] == [f.entries["A"].glyph.layers[0], f.entries["A"].glyph]
    assert f.entries["A"].glyph.histories == [0]


TYPERIG = "rescued/part3/sources/kateliev_TypeRig/"
R1B_PORTS = {
    TYPERIG + "Scripts/TypeRig GUI/Panel/Pairs.py": "Scripts/Tools/Pair Proof Generator.py",
    TYPERIG + "Scripts/TypeRig GUI/Panel/Stats.py": "Scripts/Tools/Layer Metric Comparison.py",
}


def typerig_records() -> list[dict[str, Any]]:
    """Return every TypeRig record of menu-adaptations.json."""
    shared = json.loads((ROOT / "menu-adaptations.json").read_text())
    return [
        row
        for section in ("adaptations", "retirements")
        for row in shared[section]
        if row["source"].startswith(TYPERIG)
    ]


def test_dispositions_when_loaded_then_cover_exact_source_identities() -> None:
    files = {source for source in recorded_sources() if source.startswith(TYPERIG)}
    rows = typerig_records()
    sources = [row["source"] for row in rows]
    assert len(sources) == len(set(sources)) == len(files) == 78, (
        "Record every rescued TypeRig Python file exactly once"
    )
    assert set(sources) == files
    source_only = [row for row in rows if "source_menu" not in row]
    assert len(source_only) == 42, "Files without a menu identity"
    for source, menu in R1B_PORTS.items():
        row = next(r for r in rows if r["source"] == source)
        assert row["menu"] == menu and row["disposition"] == "ported"
    for row in rows:
        assert (
            recorded_sha256(row['source'])
            == row["source_sha256"]
        ), row["source"]
        if row.get("menu"):
            target = (
                ROOT.parent / row["menu"]
                if row["menu"].startswith("fontlab-python-")
                else ROOT / row["menu"]
            )
            assert (
                hashlib.sha256(target.read_bytes()).hexdigest()
                == row["destination_sha256"]
            ), row["menu"]


def test_panel_when_built_then_controls_and_preview_use_real_hooks(
    monkeypatch: Any,
) -> None:
    import fly
    import fontlabapp.selection_panel as selection

    class StrictPanel:
        def __setattr__(self, name: str, value: Any) -> None:
            assert name not in COLLISIONS, f"Native widget member: {name}"
            object.__setattr__(self, name, value)

        def add_row(self, label: str, *widgets: Any) -> None:
            self.added_row = (label, widgets)

        def watch(
            self, signal: Any, callback: Callable[..., Any] | None = None
        ) -> None:
            self.watched_signal = signal

    class Text:
        textChanged = object()

        def setPlainText(self, text: str) -> None:
            self.text_value = text

        def toPlainText(self) -> str:
            return self.text_value

    def fake_panel_type() -> type:
        return StrictPanel

    assert inspect.signature(fake_panel_type) == inspect.signature(selection.panel_type)
    monkeypatch.setattr(selection, "panel_type", fake_panel_type)
    monkeypatch.setitem(fly.__dict__, "qt", NS(QtGui=NS(QPlainTextEdit=Text)))
    from fontlabapp import names_edit

    scans = []
    f = facts({"A": []})

    def scan(native: Any = None) -> Facts:
        scans.append("scan")
        return f

    def fresh_facts(package_id: int, *, native: Any = None) -> Facts:
        raise AssertionError("Typing must not run fresh_facts")

    assert inspect.signature(scan) == inspect.signature(names_edit.scan)
    assert inspect.signature(fresh_facts) == inspect.signature(names_edit.fresh_facts)
    monkeypatch.setattr(names_edit, "scan", scan)
    monkeypatch.setattr(names_edit, "fresh_facts", fresh_facts)
    tool = load()
    panel = tool.panel_type()()
    panel.build_controls()
    assert panel.added_row[0] == "JSON map"
    assert panel.watched_signal is panel.map_input.textChanged
    assert panel.map_input.toPlainText() == '{"A": "0041"}'
    panel.names = ["A"]
    panel.map_input.setPlainText("{")
    with pytest.raises(ValueError):
        panel.plan_rows(NS(id=9), [])
    assert scans == [], "Parse invalid JSON before any font access"
    panel.map_input.setPlainText('{"A": "0041"}')
    panel.rows = panel.plan_rows(NS(id=9), [])
    panel.map_input.setPlainText('{"A": "U+0042"}')
    panel.plan_rows(NS(id=9), [])
    panel.map_input.setPlainText('{"A": "0x43"}')
    panel.plan_rows(NS(id=9), [])
    assert scans == ["scan"], "Open scans once; typing twice performs no new scan"
    panel.on_reselect()
    assert scans == ["scan", "scan"], "Use Selection explicitly reloads once"
    panel.on_result({"facts": load().snapshot_facts(f)})
    assert scans == ["scan", "scan"], "After Apply reuse the write facts"

    received = []

    def write_map(
        package_id: int, selected: list[str], mapping: dict, preview: list[dict]
    ) -> dict:
        received.append(preview)
        return {"changed": 0}

    monkeypatch.setattr(tool, "write_map", write_map)
    panel.write(NS(id=9), [{"replacement": "not displayed"}])
    assert received[0] is panel.rows, (
        "Compare with the displayed table, not the Apply-time plan"
    )

    changed_facts = facts({"A": [66]})

    def stale_write(*args: Any) -> dict:
        raise tool.StalePreviewError(changed_facts)

    monkeypatch.setattr(tool, "write_map", stale_write)
    with pytest.raises(tool.StalePreviewError):
        panel.write(NS(id=9), [])
    assert panel.rows == [], "Discard the obsolete displayed plan"
    assert panel.facts_cache.entries["A"].record.unicodes == (66,)
    assert scans == ["scan", "scan"], "Reuse facts from inside Apply; no extra scan"

    # Match the real base hook's AST signature without importing native Qt.
    import textwrap

    app_root = Path(importlib.import_module("fontlabapp").__file__).parent
    real_watch = next(
        n
        for n in ast.walk(ast.parse((app_root / "_selection_panel.py").read_text()))
        if isinstance(n, ast.FunctionDef) and n.name == "watch"
    )
    fake_watch = ast.parse(textwrap.dedent(inspect.getsource(StrictPanel.watch))).body[
        0
    ]
    assert ast.dump(real_watch.args) == ast.dump(fake_watch.args)
    row = {"name": "A", "before": (), "after": (65,), "note": ""}
    assert panel.cells(row) == ["A", "", "U+0041", "Add codes"]
    assert panel.is_ready(row)
    row["note"] = "not selected"
    assert not panel.is_ready(row)
    assert panel.cells(row)[-1] == "Kept: not selected"
    assert "1 glyphs" in panel.result_text({"changed": 1})


def test_write_when_preview_stale_then_no_history(monkeypatch: Any) -> None:
    import fontlabapp.names_edit as names

    f = facts({"A": [66]})

    def fresh_facts(package_id: int, *, native: Any = None) -> Facts:
        return f

    assert inspect.signature(fresh_facts) == inspect.signature(names.fresh_facts)
    monkeypatch.setattr(names, "fresh_facts", fresh_facts)
    module = load()
    old = module.plan_map(facts({"A": []}), ["A"], {"A": (65,)})
    with pytest.raises(ValueError, match="font changed"):
        module.write_map(9, ["A"], {"A": (65,)}, old)
    assert f.entries["A"].glyph.histories == []


def test_plan_when_empty_selection_then_all_rows_kept() -> None:
    rows = load().plan_map(facts({"A": []}), [], {"A": (65,)})
    assert rows[0]["note"] == "not selected"
    assert rows[0]["after"] == ()


def test_integration_objects_when_loaded_then_all_schema_keys_and_exact_hashes() -> (
    None
):
    rows = [row for row in typerig_records() if "source_menu" not in row]
    common = {"source", "source_sha256", "license"}
    adapt = common | {
        "menu",
        "destination_sha256",
        "entry_point",
        "family",
        "scope",
        "disposition",
        "assets",
        "source_body_redistributed",
        "native_acceptance",
        "original_workflow_accepted",
    }
    assert len(rows) == len({r["source"] for r in rows}) == 42
    assert sum("menu" in row for row in rows) == 9
    for row in rows:
        if "menu" in row:
            assert set(row) == adapt
            assert row["license"] == "Apache-2.0 (independent rewrite; source MPL-2.0)"
            assert row["native_acceptance"] == "pending"
            assert row["original_workflow_accepted"] is False
        else:
            assert set(row) == common | {"disposition", "reason"}
            assert row["license"] == "MPL-2.0"
            assert row["disposition"] == "retired"


@pytest.mark.parametrize("value", ["U+0041", "0x41", "0041"])
def test_hex_when_explicit_prefix_then_accept(value: str) -> None:
    assert load().parse_map(json.dumps({"A": value})) == {"A": (65,)}


@pytest.mark.parametrize("value", ["+41", "4_1", " 41", "41 ", "U+nope", "0x"])
def test_hex_when_unsupported_then_clear_refusal(value: str) -> None:
    with pytest.raises(ValueError, match="hexadecimal"):
        load().parse_map(json.dumps({"A": value}))


def test_encoding_cache_when_font_changes_then_preview_stays_detached() -> None:
    f = facts({"A": []})
    tool = load()
    cached = tool.snapshot_facts(f)
    f.entries["A"].record.unicodes = [66]
    assert tool.plan_map(cached, ["A"], {"A": (65,)})[0]["before"] == ()


@pytest.mark.parametrize("name", ["Bad@Name", "Bad#Name", "|temp|Bad", ""])
@pytest.mark.parametrize("script", [COPY, SCALE])
def test_new_layer_name_when_reserved_then_refused(script: Path, name: str) -> None:
    with pytest.raises(ValueError):
        load(script).checked_name(name)


def test_crossfont_collision_when_chosen_then_suffix_or_mask_or_overwrite() -> None:
    tool = load(COPY)
    assert tool.collision("Regular", ".copy", "Incoming + suffix", True) == (
        "Regular.copy",
        None,
    )
    assert tool.collision("Regular", ".old", "Destination + suffix", True) == (
        "Regular",
        "Regular.old",
    )
    assert tool.collision("Regular", "", "Overwrite", True) == ("Regular", None)
    assert tool.collision("Regular", "", "Mask", True) == ("Regular", None)


def test_stem_scaling_when_tt_then_scales_every_control_without_cubic_conversion() -> (
    None
):
    tool = load(SCALE)
    first = [
        (
            True,
            [
                (0.0, 0.0, True),
                (50.0, 100.0, False),
                (100.0, 100.0, False),
                (150.0, 0.0, True),
            ],
            True,
        )
    ]
    second = [
        (
            True,
            [
                (0.0, 0.0, True),
                (100.0, 200.0, False),
                (200.0, 200.0, False),
                (300.0, 0.0, True),
            ],
            True,
        )
    ]
    result = tool.blend_contours(first, second, (50, 100, 50, 100), (75, 75), (1, 1), 0)
    assert result == [
        (
            True,
            [
                (0.0, 0.0, True),
                (75.0, 150.0, False),
                (150.0, 150.0, False),
                (225.0, 0.0, True),
            ],
            True,
        )
    ]
    assert first[0][1][1] == (50.0, 100.0, False), "Input stays unchanged"


@pytest.mark.parametrize("script", [COPY, SCALE])
def test_new_tools_when_parsed_then_python311_and_no_native_member_shadowing(
    script: Path,
) -> None:
    tree = ast.parse(script.read_text(), feature_version=(3, 11))
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            assert node.attr not in COLLISIONS
        if isinstance(node, ast.ClassDef):
            assert not (
                {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
                & COLLISIONS
            )


class Point:
    def __init__(self, x: float, y: float) -> None:
        self._x, self._y = x, y

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y


class Transform:
    def isIdentity(self) -> bool:
        return True

    def __getattr__(self, name: str) -> Any:
        if name in {f"m{i}{j}" for i in (1, 2, 3) for j in (1, 2, 3)}:
            return lambda: float(name[1] == name[2])
        raise AttributeError(name)


class HostNode:
    """Fresh wrappers share storage, so coordinate writes reach the native record."""

    def __init__(self, point: Point, *, nodeType: str = "on") -> None:
        self.record = NS(
            x=point.x(),
            y=point.y(),
            kind=nodeType,
            nodeState=0x11 if nodeType == "on" else 0x42,
            name="node",
        )

    @property
    def x(self) -> float:
        return self.record.x

    @x.setter
    def x(self, value: float) -> None:
        self.record.x = value

    @property
    def y(self) -> float:
        return self.record.y

    @y.setter
    def y(self, value: float) -> None:
        self.record.y = value

    @property
    def name(self) -> str:
        return self.record.name

    @name.setter
    def name(self, value: str) -> None:
        self.record.name = value

    @property
    def nodeState(self) -> int:
        return self.record.nodeState

    @nodeState.setter
    def nodeState(self, value: int) -> None:
        self.record.nodeState = value

    def isOn(self) -> bool:
        return self.record.kind == "on"

    def getProperties(self) -> list:
        return []

    def getProperty(self, name: str) -> Any:
        return getattr(self.record, name, None)


class HostContour:
    def __init__(self, nodes: list[HostNode], *, closed: bool = False) -> None:
        self.stored_nodes, self.closed, self.name = nodes, closed, "contour"
        self.isTT = any(n.record.kind == "off" for n in nodes)

    def nodes(self) -> list[HostNode]:
        wrappers = []
        for old in self.stored_nodes:
            new = object.__new__(HostNode)
            new.record = old.record
            wrappers.append(new)
        return wrappers

    def getProperties(self) -> list:
        return []

    def cloneMapped(self, transform: Transform) -> Any:
        # Deliberately drop raw flags and names, as native copying can do.
        return HostContour(
            [HostNode(Point(n.x, n.y), nodeType=n.record.kind) for n in self.nodes()],
            closed=self.closed,
        )


class HostShape:
    def __init__(self) -> None:
        self.contours: list[HostContour] = []
        self.isComponent, self.name = False, "element"
        self.shapeData = NS(name="shape", note="keep this note", referenceCount=1)
        self.transform = Transform()
        self.active = self.selected = False

    def addContour(self, contour: HostContour, a: bool, b: bool) -> None:
        self.contours.append(contour)

    def clone(self) -> Any:
        shape = HostShape()
        shape.contours = [c.cloneMapped(self.transform) for c in self.contours]
        shape.shapeData.note = ""
        return shape


class HostPin:
    def __init__(self, point: Point) -> None:
        self.point, self.name, self.anchor, self.appearance = point, "", True, 0


class HostLayer(Owned):
    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.shapes: list[HostShape] = []
        self.anchors: list[HostPin] = []
        self.isLocked = self.isService = self.isMaskLayer = False
        self.isMasterLayer = name in ("Regular", "Bold")
        self.hasHints = self.hasTTH = False
        self.guidelines: list = []
        self.metricsLeft = self.metricsRight = self.metricsWidth = ""
        self.advanceWidth = 500.0
        self.mask_body: Any = None
        self.owner: Any = None
        self.fail_update = False

    def addShape(self, shape: HostShape) -> HostShape:
        self.shapes.append(shape)
        return shape

    def removeShape(self, shape: HostShape) -> None:
        self.shapes.remove(shape)

    def addAnchor(self, pin: HostPin) -> None:
        self.anchors.append(pin)

    def removeAnchor(self, pin: HostPin) -> None:
        self.anchors.remove(pin)

    def changed(self) -> None:
        pass

    def update(self) -> bool:
        return not self.fail_update

    def getMaskLayer(self, create: bool) -> Any:
        exact = self.owner.findLayer("mask." + self.name)
        if exact is not None:
            return exact
        if not create:
            return self.owner.findLayer("mask." + self.name.split(".")[0])
        if self.mask_body is None and create:
            self.mask_body = HostLayer("mask." + self.name)
            self.mask_body.isMaskLayer = True
            self.mask_body.owner = self.owner
            self.owner.layers.append(self.mask_body)
        return self.mask_body


class HostGlyph(Owned):
    def __init__(self, name: str, layers: list[HostLayer]) -> None:
        super().__init__(name)
        self.layers = layers
        for layer in layers:
            layer.owner = self

    def findLayer(self, name: str) -> Any:
        return next((layer for layer in self.layers if layer.name == name), None)

    def addLayer(self, layer: HostLayer, *, back: bool = False) -> None:
        layer.owner = self
        self.layers.append(layer)


class HostPackage:
    def __init__(self, fg_id: int, glyphs: list[HostGlyph]) -> None:
        self.fgId, self.id = fg_id, fg_id + 1000
        self.glyphs = {g.name: g for g in glyphs}
        self.master, self.masters = "Regular", ["Regular", "Bold"]
        self.info = NS(unitsPerEm=1000)
        self.italicAngle_value = 0
        self.isNull = False

    def setMaster(self, name: str) -> None:
        self.master = name
        self.italicAngle_value = 0 if name == "Regular" else -12

    def findName(self, name: str) -> Any:
        return self.glyphs.get(name)


def host_layer(
    name: str = "Regular", factor: float = 1.0, tt: bool = True
) -> HostLayer:
    layer = HostLayer(name)
    shape = HostShape()
    shape.contours = [
        HostContour(
            [
                HostNode(Point(x * factor, y * factor), nodeType=kind)
                for x, y, kind in [
                    (0, 0, "on"),
                    (50, 100, "off" if tt else "curve"),
                    (100, 100, "off" if tt else "curve"),
                    (150, 0, "on"),
                ]
            ],
            closed=True,
        )
    ]
    layer.shapes = [shape]
    layer.advanceWidth *= factor
    return layer


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    import sys

    import fly
    import fontlabapp.edit_guards as guards

    source = HostPackage(
        11, [HostGlyph("A", [host_layer()]), HostGlyph("B", [host_layer()])]
    )
    destination = HostPackage(
        22,
        [
            HostGlyph("A", [host_layer(), host_layer("Bold", 2)]),
            HostGlyph("B", [host_layer(), host_layer("Bold", 2)]),
        ],
    )
    destination.glyphs["B"].layers[0].autoLayer = True
    pin = HostPin(Point(50, 100))
    pin.name = "top"
    source.findName("A").layers[0].anchors = [pin]
    source.findName("A").layers[0].advanceWidth = 700
    source.findName("A").layers[0].shapes[0].name = "source element"
    source.findName("A").layers[0].shapes[0].shapeData.name = "source shape"
    source.findName("A").layers[0].shapes[0].contours[0].name = "source contour"
    source.findName("A").layers[0].shapes[0].contours[0].nodes()[0].name = "source node"
    source.findName("A").layers[0].shapes[0].contours[0].nodes()[0].nodeState = 0x91
    calls = []
    def font_records(p):
        return NS(
            id=p.fgId,
            path=f"Font-{p.fgId}.vfj",
            glyphs=[NS(name=n, unicodes=[]) for n in p.glyphs],
        )
    workspace = NS(currentPackage=destination, packages=lambda: [source, destination])
    native = NS(
        flWorkspace=NS(instance=lambda: workspace),
        flPackage=lambda p: p,
        AllFonts=lambda: [font_records(source), font_records(destination)],
        CurrentFont=lambda: font_records(workspace.currentPackage),
        flGlyph=NS(updatedFgGlyphs=list),
        flItems=lambda: NS(notifyChangesApplied=lambda *args: calls.append(args)),
        flNode=HostNode,
        flContour=HostContour,
        flLayer=HostLayer,
        flShape=HostShape,
        flPinPoint=HostPin,
    )
    qt = NS(
        QtCore=NS(QPointF=Point, QDateTime=NS(currentDateTimeUtc=lambda: "stamp")),
        QtGui=NS(QTransform=Transform),
    )
    monkeypatch.setitem(sys.modules, "fontlab", native)
    monkeypatch.setitem(sys.modules, "PythonQt", qt)
    monkeypatch.setitem(fly.__dict__, "fl", native)
    monkeypatch.setitem(fly.__dict__, "qt", qt)

    def selection_window(package_id: int) -> None:
        assert package_id == destination.id

    def no_editors(*, qt: Any = None, deadline: float | None = None) -> None:
        pass

    assert inspect.signature(selection_window) == inspect.signature(
        guards.require_selection_window
    )
    assert inspect.signature(no_editors) == inspect.signature(guards.require_no_editors)
    monkeypatch.setattr(guards, "require_selection_window", selection_window)
    monkeypatch.setattr(guards, "require_no_editors", no_editors)
    return NS(
        source=source,
        destination=destination,
        calls=calls,
        native=native,
        qt=qt,
        workspace=workspace,
    )


@pytest.mark.parametrize(
    "mode", ["Overwrite", "Incoming + suffix", "Destination + suffix", "Mask"]
)
def test_crossfont_when_applied_then_one_destination_undo_and_source_unchanged(
    host: Any, mode: str
) -> None:
    tool = load(COPY)
    source_layer = host.source.findName("A").findLayer("Regular")
    from time import monotonic

    before = tool.layer_data(source_layer, monotonic() + 3)
    target = "Aux" if mode == "Destination + suffix" else "Regular"
    if target == "Aux":
        host.destination.findName("A").addLayer(host_layer("Aux", 3))
    plan = tool.make_plan(11, 22, ["A", "B"], [("Regular", target)], mode, ".copy")
    assert plan["rows"][1]["note"], "Unavailable glyph is a kept row"
    result = tool.apply_plan(plan, True)
    assert result == {"pending_note": "", "changed": 1, "kept": 1, "pending_updates": ()}
    assert len(host.calls) == 1
    assert host.calls[0][1][-1] is host.destination.findName("A")
    assert all(item is not host.source.findName("A") for item in host.calls[0][1])
    assert source_layer.histories == host.source.findName("A").histories == []
    assert tool.layer_data(source_layer, monotonic() + 3) == before
    actual_name = "Regular.copy" if mode == "Incoming + suffix" else target
    output = host.destination.findName("A").findLayer(actual_name)
    if mode == "Mask":
        output = output.getMaskLayer(False)
    assert tool.layer_data(output, monotonic() + 3) == before
    if mode == "Destination + suffix":
        assert host.destination.findName("A").findLayer("Aux.copy").advanceWidth == 1500


@pytest.mark.parametrize("failure", ["confirmation", "stale", "closed", "units"])
def test_crossfont_when_context_refused_then_no_history(
    host: Any, failure: str
) -> None:
    tool = load(COPY)
    plan = tool.make_plan(11, 22, ["A"], [("Regular", "Regular")], "Overwrite", "")
    if failure == "stale":
        host.source.findName("A").layers[0].advanceWidth += 10
    if failure == "closed":
        host.native.AllFonts = list
    if failure == "units":
        host.source.info.unitsPerEm = 2000
    with pytest.raises(ValueError):
        tool.apply_plan(plan, failure != "confirmation")
    assert not host.calls


def scale_config(master: str = "Regular") -> dict[str, Any]:
    return {
        "master": master,
        "first": "Regular",
        "second": "Bold",
        "stems": (50, 100, 50, 100),
        "target": (75, 75),
        "scales": (1, 1),
        "angle": 0,
    }


@pytest.mark.parametrize("tt", [True, False])
def test_batch_scale_when_applied_then_checked_masters_and_kept_glyphs_one_undo(
    host: Any,
    tt: bool,
) -> None:
    tool = load(SCALE)
    glyph = host.destination.findName("A")
    if not tt:
        for layer in glyph.layers:
            for contour in layer.shapes[0].contours:
                contour.isTT = False
                for node in contour.nodes():
                    if not node.isOn():
                        node.record.kind = "curve"
    before = [tool.read_contours(layer, float("inf")) for layer in glyph.layers]
    plan = tool.make_plan(
        22, ["A", "B"], [scale_config(), scale_config("Bold")], ".scaled"
    )
    assert len(plan["rows"]) == 4
    result = tool.apply_plan(plan, True)
    assert result == {"pending_note": "", "changed": 2, "kept": 2, "pending_updates": ()}
    assert len(host.calls) == 1
    assert host.calls[0][1] == [
        glyph.findLayer("Regular.scaled"),
        glyph.findLayer("Bold.scaled"),
        glyph,
    ]
    assert glyph.histories == [0]
    assert [tool.read_contours(layer, float("inf")) for layer in glyph.layers[:2]] == before
    for name in ("Regular.scaled", "Bold.scaled"):
        layer = glyph.findLayer(name)
        contour = layer.shapes[0].contours[0]
        assert contour.isTT is tt
        assert [n.isOn() for n in contour.nodes()] == [True, False, False, True]
        assert [(n.x, n.y) for n in contour.nodes()] == [
            (0, 0),
            (75, 150),
            (150, 150),
            (225, 0),
        ]
        assert contour.nodes()[1] is not contour.nodes()[1], (
            "Native getters return fresh wrappers"
        )


@pytest.mark.parametrize("failure", ["confirmation", "stale", "existing"])
def test_batch_scale_when_refused_then_no_history(host: Any, failure: str) -> None:
    tool = load(SCALE)
    plan = tool.make_plan(22, ["A"], [scale_config()], ".scaled")
    if failure == "stale":
        host.destination.findName("A").findLayer("Bold").shapes[0].contours[0].nodes()[
            0
        ].x += 1
    if failure == "existing":
        host.destination.findName("A").addLayer(HostLayer("Regular.scaled"))
    with pytest.raises(ValueError):
        tool.apply_plan(plan, failure != "confirmation")
    assert not host.calls


class Signal:
    def __init__(self) -> None:
        self.callbacks: list = []

    def connect(self, callback: Any) -> None:
        self.callbacks.append(callback)

    def disconnect(self, callback: Any) -> None:
        self.callbacks.remove(callback)

    def emit(self, *args: Any) -> None:
        for call in list(self.callbacks):
            call(*args)


class Widget:
    """Strict Qt shape with real property-style value reads and owned signals."""

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in COLLISIONS, f"Native member collision: {name}"
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.raw_text = str(args[0]) if args and isinstance(args[0], str) else ""
        self.items: dict = {}
        self.cells: dict = {}
        self.options: list[str] = []
        self.currentIndex, self.rowCount = (
            0,
            args[0] if args and type(args[0]) is int else 0,
        )
        self.checked_flag = False
        (
            self.textChanged,
            self.currentIndexChanged,
            self.cellChanged,
            self.clicked,
            self.toggled,
        ) = [Signal() for _ in range(5)]

    @property
    def text(self) -> str:
        return self.raw_text

    @property
    def currentText(self) -> str:
        return self.options[self.currentIndex] if self.options else ""

    def setText(self, value: str) -> None:
        self.raw_text = value
        self.textChanged.emit(value)

    def setPlainText(self, value: str) -> None:
        self.raw_text = value

    def toPlainText(self) -> str:
        return self.raw_text

    def addItem(self, value: str) -> None:
        self.options.append(value)

    def addItems(self, values: list[str]) -> None:
        self.options.extend(values)

    def clear(self) -> None:
        self.options.clear()

    def setChecked(self, value: bool) -> None:
        self.checked_flag = value

    def isChecked(self) -> bool:
        return self.checked_flag

    def setRowCount(self, count: int) -> None:
        self.rowCount = count

    def setItem(self, row: int, col: int, item: Any) -> None:
        self.items[row, col] = item

    def item(self, row: int, col: int) -> Any:
        return self.items.get((row, col))

    def setCellWidget(self, row: int, col: int, widget: Any) -> None:
        self.cells[row, col] = widget

    def cellWidget(self, row: int, col: int) -> Any:
        return self.cells[row, col]

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        self.header_labels = labels

    def setReadOnly(self, value: bool) -> None:
        pass

    def addWidget(self, value: Any) -> None:
        pass

    def resize(self, x: int, y: int) -> None:
        pass

    def setWindowTitle(self, value: str) -> None:
        pass

    def closeEvent(self, event: Any) -> None:
        event.accept()

    def deleteLater(self) -> None:
        self.deleted_flag = True


class TableItem:
    def __init__(self, value: str) -> None:
        self.raw_text = value

    def text(self) -> str:
        return self.raw_text


@pytest.mark.parametrize("script", [COPY, SCALE])
def test_new_panel_when_constructed_then_real_controls_preview_and_owned_cleanup(
    host: Any,
    monkeypatch: Any,
    script: Path,
) -> None:
    from fontlabapp import scripting

    gui = host.qt.QtGui
    for name in (
        "QDialog",
        "QVBoxLayout",
        "QLabel",
        "QLineEdit",
        "QComboBox",
        "QCheckBox",
        "QPushButton",
        "QTableWidget",
        "QPlainTextEdit",
    ):
        setattr(gui, name, Widget)
    gui.QTableWidgetItem = TableItem

    def names_font_window_selection(
        *, expected_fg_id: int | None = None, deadline: float | None = None
    ) -> list[str]:
        assert expected_fg_id == 22
        return ["A", "B"]

    assert inspect.signature(names_font_window_selection) == inspect.signature(
        scripting.names_font_window_selection
    )
    monkeypatch.setattr(
        scripting, "names_font_window_selection", names_font_window_selection
    )
    panel = load(script).panel_type()()
    if script == COPY:
        panel.preview_copy()
    else:
        panel.preview_scale()
        before_connections = len(panel._connections)
        panel.reload_selection()
        assert len(panel._connections) == before_connections, (
            "Selection reload reuses checkbox widgets"
        )
        panel.preview_scale()
    if script == SCALE:
        assert float(panel.master_table.item(0, 12).text()) == 0
        assert panel.master_table.item(1, 12).text() == "12", "Use each master's slant"
    old_names = panel.names[:]
    old_identity = panel.destination_id if script == COPY else panel.identity
    old_sources = panel.source_ids[:] if script == COPY else panel.master_names[:]
    host.workspace.currentPackage = host.source
    monkeypatch.setattr(
        "fontlabapp.edit_guards.require_selection_window", lambda identity: None
    )

    # Fail after the candidate identity was read, before any state may be installed.
    def refused_selection(**kwargs: Any) -> list[str]:
        raise ValueError("selection unavailable")

    with monkeypatch.context() as scoped:
        scoped.setattr(scripting, "names_font_window_selection", refused_selection)
        with pytest.raises(ValueError, match="selection unavailable"):
            panel.reload_selection()
    host.workspace.currentPackage = host.destination
    assert panel.names == old_names
    assert (panel.destination_id if script == COPY else panel.identity) == old_identity
    assert (panel.source_ids if script == COPY else panel.master_names) == old_sources
    assert panel.plan_data is not None, "Refused reload preserves the panel's plan"
    assert "Kept:" in panel.preview_field.toPlainText()
    assert not panel.confirm_box.isChecked()
    panel.suffix_field.setText(".changed")
    assert panel.plan_data is None, (
        "Editing controls invalidates Preview without scanning"
    )
    signals = [signal for signal, _ in panel._connections]
    panel.closeEvent(NS(accept=lambda: None))
    assert panel._connections == []
    assert all(not signal.callbacks for signal in signals)
    assert panel.deleted_flag is True


@pytest.mark.parametrize("script", [COPY, SCALE])
def test_new_tools_when_native_attach_fails_after_add_then_partial_history_is_kept(
    host: Any, script: Path
) -> None:
    tool = load(script)
    glyph = host.destination.findName("A")
    original = glyph.addLayer

    def fail_after_attach(layer: HostLayer, *, back: bool = False) -> None:
        original(layer, back=back)
        raise RuntimeError("injected after attaching layer")

    if script == COPY:
        plan = tool.make_plan(
            11, 22, ["A"], [("Regular", "Regular")], "Incoming + suffix", ".new"
        )
        new_name = "Regular.new"
    else:
        plan = tool.make_plan(22, ["A"], [scale_config()], ".new")
        new_name = "Regular.new"
    glyph.addLayer = fail_after_attach
    with pytest.raises(RuntimeError, match="use Edit > Undo"):
        tool.apply_plan(plan, True)
    assert len(host.calls) == 1
    assert glyph.findLayer(new_name) in host.calls[0][1], (
        "New layer is enrolled even after a native exception"
    )
    assert host.calls[0][1][-1] is glyph


def test_crossfont_when_anchor_would_move_to_origin_then_kept_before_history(
    host: Any,
) -> None:
    tool = load(COPY)
    host.source.findName("A").layers[0].anchors[0].point = Point(0, 0)
    pin = HostPin(Point(1, 2))
    pin.name = "top"
    host.destination.findName("A").layers[0].anchors = [pin]
    plan = tool.make_plan(11, 22, ["A"], [("Regular", "Regular")], "Overwrite", "")
    assert "origin" in plan["rows"][0]["note"]
    assert tool.apply_plan(plan, True)["changed"] == 0
    assert not host.calls


def test_real_native_ctor_fakes_when_optional_positional_then_reject() -> None:
    with pytest.raises(TypeError):
        HostNode(Point(1, 2), "off")
    with pytest.raises(TypeError):
        HostContour([], True)


@pytest.mark.parametrize("script", [COPY, SCALE])
def test_new_tools_when_custom_corner_metadata_then_keep_source(
    host: Any, script: Path
) -> None:
    tool = load(script)
    if script == COPY:
        host.source.findName("A").layers[0].shapes[0].contours[0].nodes()[
            0
        ].record.corner_smooth = 12
        plan = tool.make_plan(11, 22, ["A"], [("Regular", "Regular")], "Overwrite", "")
    else:
        host.destination.findName("A").layers[0].shapes[0].contours[0].nodes()[
            0
        ].record.corner_smooth = 12
        plan = tool.make_plan(22, ["A"], [scale_config()], ".scaled")
    assert "custom node" in plan["rows"][0]["note"]
    assert tool.apply_plan(plan, True)["changed"] == 0
    assert not host.calls


def test_scaling_when_nonunit_then_compensates_stems_and_moves_handles() -> None:
    tool = load(SCALE)
    first = [
        (
            True,
            [
                (0.0, 0.0, True),
                (50.0, 100.0, False),
                (100.0, 100.0, False),
                (150.0, 0.0, True),
            ],
            False,
        )
    ]
    second = [
        (
            True,
            [
                (0.0, 0.0, True),
                (100.0, 200.0, False),
                (200.0, 200.0, False),
                (300.0, 0.0, True),
            ],
            False,
        )
    ]
    result = tool.blend_contours(
        first, second, (50, 100, 50, 100), (37.5, 56.25), (0.5, 0.75), 0
    )
    assert result[0][1] == [
        (0, 0, True),
        (37.5, 112.5, False),
        (75, 112.5, False),
        (112.5, 0, True),
    ]


@pytest.mark.parametrize("case", ["empty", "equal", "zero", "infinite", "type"])
def test_scaling_when_invalid_then_refused_before_native_work(case: str) -> None:
    tool = load(SCALE)
    first = [(True, [(0.0, 0.0, True), (100.0, 100.0, True)], False)]
    second = (
        first
        if case != "type"
        else [(True, [(0.0, 0.0, True), (100.0, 100.0, True)], True)]
    )
    stems = (50, 50, 50, 100) if case == "equal" else (50, 100, 50, 100)
    scales = (0, 1) if case == "zero" else (1, 1)
    target = (float("inf"), 75) if case == "infinite" else (75, 75)
    with pytest.raises(ValueError):
        tool.blend_contours(
            [] if case == "empty" else first, second, stems, target, scales, 0
        )


def test_crossfont_when_destination_base_of_auto_then_kept(host: Any) -> None:
    component = HostShape()
    component.isComponent = True
    component.shapeData.componentGlyph = "A"
    host.destination.findName("B").layers[0].shapes = [component]
    tool = load(COPY)
    plan = tool.make_plan(11, 22, ["A"], [("Regular", "Regular")], "Overwrite", "")
    assert "auto" in plan["rows"][0]["note"]
    assert tool.apply_plan(plan, True)["changed"] == 0
    assert not host.calls


@pytest.mark.parametrize("script", [COPY, SCALE])
@pytest.mark.parametrize("name", ["masking", "MASK.foo", "img.foo", "bw.foo"])
def test_reserved_layer_prefixes_are_refused(script: Path, name: str) -> None:
    with pytest.raises(ValueError):
        load(script).checked_name(name)


def test_mask_fallback_is_kept_and_exact_name_is_visible(host: Any) -> None:
    tool = load(COPY)
    glyph = host.destination.findName("A")
    glyph.addLayer(host_layer("Regular.alt"))
    mask = HostLayer("mask.Regular")
    mask.isMaskLayer = True
    glyph.addLayer(mask)
    body = glyph.findLayer("Regular.alt")
    assert body.getMaskLayer(False) is mask, "Model native dotted-prefix fallback"
    plan = tool.make_plan(11, 22, ["A"], [("Regular", "Regular.alt")], "Mask", "")
    assert plan["rows"][0]["mask_name"] == "mask.Regular.alt"
    assert "mask belongs to another layer" in plan["rows"][0]["note"]
    assert tool.apply_plan(plan, True) == {"changed": 0, "kept": 1, "pending_updates": (), "pending_note": ""}
    assert not host.calls and not mask.shapes


def test_mask_ignores_unwritten_body_content(host: Any) -> None:
    tool = load(COPY)
    body = host.destination.findName("A").findLayer("Regular")
    body.hasHints = True
    body.guidelines = [object()]
    body.metricsWidth = "=B"
    body.shapes[0].isComponent = True
    body.shapes[0].shapeData.componentGlyph = "B"
    plan = tool.make_plan(11, 22, ["A"], [("Regular", "Regular")], "Mask", "")
    assert not plan["rows"][0]["note"]
    assert tool.apply_plan(plan, True)["changed"] == 1
    assert host.destination.findName("A").findLayer("mask.Regular") is not None


def test_backup_cannot_take_missing_master_name(host: Any) -> None:
    tool = load(COPY)
    glyph = host.destination.findName("A")
    glyph.addLayer(host_layer("Bol"))
    glyph.layers.remove(glyph.findLayer("Bold"))
    plan = tool.make_plan(
        11, 22, ["A"], [("Regular", "Bol")], "Destination + suffix", "d"
    )
    assert "master" in plan["rows"][0]["note"]


@pytest.mark.parametrize("script", [COPY, SCALE])
def test_capture_timeout_refuses_whole_preview(
    host: Any, monkeypatch: Any, script: Path
) -> None:
    tool = load(script)
    ticks = iter([0, 1000, 1000, 1000, 1000])
    monkeypatch.setattr(tool, "monotonic", lambda: next(ticks, 1000))
    with pytest.raises(TimeoutError, match="fewer glyphs"):
        if script == COPY:
            tool.make_plan(11, 22, ["A"], [("Regular", "Regular")], "Overwrite", "")
        else:
            tool.make_plan(22, ["A"], [scale_config()], ".scaled")


@pytest.mark.parametrize("scale", [0.7, 0.8])
@pytest.mark.parametrize("rounding", [True, False])
def test_scale_accepts_native_snapping_and_metric_rounding(
    host: Any, monkeypatch: Any, scale: float, rounding: bool
) -> None:
    tool = load(SCALE)
    glyph = host.destination.findName("A")
    glyph.findLayer("Regular").advanceWidth = 523

    class StoredLayer(HostLayer):
        @property
        def advanceWidth(self) -> float:
            return self.stored_width

        @advanceWidth.setter
        def advanceWidth(self, value: float) -> None:
            self.stored_width = float(round(value)) if rounding else value

    host.native.flLayer = StoredLayer
    original = glyph.addLayer

    def add(layer: HostLayer, *, back: bool = False) -> None:
        for shape in layer.shapes:
            for contour in shape.contours:
                for node in contour.nodes():
                    for axis in ("x", "y"):
                        value = getattr(node, axis)
                        if abs(value - round(value)) < 1e-5:
                            setattr(node, axis, float(round(value)))
        original(layer, back=back)

    monkeypatch.setattr(glyph, "addLayer", add)
    config = scale_config()
    config.update(scales=(scale, scale), target=(50 * scale, 50 * scale))
    plan = tool.make_plan(22, ["A"], [config], ".scaled")
    assert tool.apply_plan(plan, True) == {"pending_note": "", "changed": 1, "kept": 0, "pending_updates": ()}
    assert glyph.findLayer("Regular.scaled").advanceWidth == (
        round(523 * scale) if rounding else 523 * scale
    )


def test_outline_tolerance_keeps_topology_and_large_errors_strict(host: Any) -> None:
    tool = load(SCALE)
    expected = [(True, [(70.00000000000001, 0, True)], True)]
    assert tool.stored_outline_matches([(True, [(70, 0, True)], True)], expected)
    assert not tool.stored_outline_matches([(True, [(70.01, 0, True)], True)], expected)
    assert not tool.stored_outline_matches([(True, [(70, 0, False)], True)], expected)
    assert not tool.stored_outline_matches([(True, [(70, 0, True)], False)], expected)


def test_scale_readback_refuses_advance_changed_after_staging(host: Any, monkeypatch: Any) -> None:
    tool = load(SCALE)
    glyph = host.destination.findName("A")
    original = glyph.addLayer

    def altered_add(layer: HostLayer, *, back: bool = False) -> None:
        layer.advanceWidth += 1
        original(layer, back=back)

    monkeypatch.setattr(glyph, "addLayer", altered_add)
    plan = tool.make_plan(22, ["A"], [scale_config()], ".scaled")
    with pytest.raises(RuntimeError, match="Undo"):
        tool.apply_plan(plan, True)
    assert len(host.calls) == 1, "Attached layer remains enrolled for Undo"


def test_external_typerig_inventory_when_available_then_matches_records() -> None:
    archived_source(next(iter(R1B_PORTS)))
    root = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
    files = {path.relative_to(root).as_posix() for path in (root / TYPERIG).rglob("*.py") if path.is_file()}
    assert files == {row["source"] for row in typerig_records()}
