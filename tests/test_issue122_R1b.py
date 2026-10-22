# this_file: tests/test_issue122_R1b.py
"""Check independent reference workflows without executing preserved sources."""

import ast
import hashlib
import importlib
import importlib.util
import inspect
import json
import math
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest
from fontlabapp.layer_selection import LayerSelection

from historical_sources import recorded_sha256

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Symbol Tag Search", "Pair Proof Generator", "Layer Metric Comparison")
NATIVE_NAMES = {
    "render",
    "size",
    "layout",
    "update",
    "font",
    "move",
    "statusBar",
    "parent",
    "children",
    "window",
    "geometry",
    "width",
    "height",
    "data",
    "close",
    "show",
    "setLayout",
    "destroyed",
}


def script_path(title: str) -> Path:
    return (
        ROOT
        / "Scripts"
        / ("Contours" if title == "Node Table" else "Tools")
        / f"{title}.py"
    )


def load(title: str) -> Any:
    """Load only the new script, with lazy native imports left untouched."""
    path = script_path(title)
    spec = importlib.util.spec_from_file_location(title.replace(" ", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def app_names_used() -> dict[str, set[str]]:
    """Collect every qualified App attribute, as in the G1 name gate."""
    result: dict[str, set[str]] = {}
    for title in (*TITLES, "Node Table"):
        tree = ast.parse(script_path(title).read_text())
        aliases = {
            alias.asname: alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
            if alias.name.startswith("fly.ap.")
        }
        for alias in aliases.values():
            result.setdefault(alias, set())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                result[aliases[node.value.id]].add(node.attr)
    return result


def test_real_app_names_from_installed_app() -> None:
    """Use real Fly aliases and the gate-installed App, never an App src override."""
    used = app_names_used()
    assert used, "Scripts must use public App helpers."
    app = importlib.import_module("fontlabapp")
    app_root = Path(app.__file__).resolve().parent
    assert "site-packages" in app_root.parts, app_root
    fly = importlib.import_module("fly")
    assert fly.ALIASES["ap"] == "fontlabapp"
    for name, attributes in used.items():
        module = importlib.import_module(name)
        assert module is importlib.import_module(
            name.replace("fly.ap", "fontlabapp", 1)
        )
        assert Path(module.__file__).resolve().is_relative_to(app_root)
        for attribute in attributes:
            assert hasattr(module, attribute), f"{name}.{attribute}"


def fake_catalog_capture(*, deadline: float | None = None) -> Any:
    return NS(
        rows=(
            ("A", "U+0041", ""),
            ("V", "U+0056", ""),
            ("A.alt", "", ""),
            ("V.alt", "", ""),
        )
    )


def fake_selection_capture(deadline: float) -> LayerSelection:
    return NS(context=(1, "Regular"), occurrences=())


def test_faked_app_signatures_match_real() -> None:
    for name, fake in (
        ("glyph_catalog.capture", fake_catalog_capture),
        ("layer_selection.capture", fake_selection_capture),
    ):
        module, attribute = name.split(".")
        real = getattr(importlib.import_module("fontlabapp." + module), attribute)
        assert inspect.signature(fake) == inspect.signature(real), name


def patch_reader(monkeypatch: Any, name: str, result: Any) -> None:
    """Verify the signature of each fake actually installed by a test."""

    def read() -> Any:
        if isinstance(result, Exception):
            raise result
        return result() if callable(result) else result

    def catalog(*, deadline: float | None = None) -> Any:
        return read()

    def selection(deadline: float) -> LayerSelection:
        return read()

    fakes = {
        "glyph_catalog": ("capture", catalog),
        "layer_selection": ("capture", selection),
    }
    attribute, fake = fakes[name]
    module = importlib.import_module("fly.ap." + name)
    assert inspect.signature(fake) == inspect.signature(getattr(module, attribute)), (
        name
    )
    monkeypatch.setattr(module, attribute, fake)


class PointF:
    """Match the QPointF coordinate-method shape used by flNode constructors."""

    def __init__(self, x: float, y: float) -> None:
        self._x, self._y = float(x), float(y)

    def x(self) -> float:
        return self._x

    def y(self) -> float:
        return self._y


class Node:
    """Optional constructor arguments are keyword-only in the native host."""

    def __init__(self, point: Any, *, nodeType: str = "on") -> None:
        self.point, self.nodeType = point, nodeType
        if not isinstance(point, PointF):
            raise TypeError("QPointF expected")
        self.x, self.y = point.x(), point.y()
        self.type, self.selected = nodeType, False

    def getProperty(self, name: str) -> Any:
        return getattr(self, "_properties", {}).get(name)

    def setProperty(self, name: str, value: Any) -> None:
        if not hasattr(self, "_properties"):
            self._properties: dict[str, Any] = {}
        self._properties[name] = value

    def getProperties(self) -> list:
        return []


class Contour:
    def __init__(self, nodes: list, *, closed: bool = False) -> None:
        self._nodes, self.closed = nodes, closed

    def nodes(self) -> list[Any]:
        return self._nodes

    def getProperties(self) -> list:
        return []


def test_native_constructor_template_guard_rejects_positional_options() -> None:
    with pytest.raises(TypeError):
        Node(PointF(0, 0), "off")
    with pytest.raises(TypeError):
        Contour([], True)
    assert Node(PointF(0, 0), nodeType="off").getProperties() == []
    assert Contour([], closed=True).getProperties() == []


@pytest.mark.parametrize("title", (*TITLES, "Node Table"))
def test_class_attributes_do_not_shadow_qwidget_names(title: str) -> None:
    path = script_path(title)
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ClassDef):
            for member in node.body:
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    assert member.name not in NATIVE_NAMES, member.name
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        ):
            assert node.attr not in NATIVE_NAMES, node.attr


def test_pair_products_suffixes_zip_fillers_and_missing_names(monkeypatch: Any) -> None:
    module = load(TITLES[1])
    patch_reader(monkeypatch, "glyph_catalog", fake_catalog_capture())
    assert module.build_output(("A V", "V A", "", "", "Product", "", "")) == (
        "/A/V\n/A/A\n/V/V\n/V/A"
    )
    assert module.build_output(("A V", "V A", ".alt", ".alt", "Zip", "A", "V")) == (
        "/A/A.alt/V.alt/V\n/A/V.alt/A.alt/V"
    )
    for fields in (
        ("", "V", "", "", "Product", "", ""),
        ("A V", "V", "", "", "Zip", "", ""),
        ("A", "missing", "", "", "Product", "", ""),
        ("A", "V", "", "", "invalid", "", ""),
    ):
        with pytest.raises(ValueError):
            module.build_output(fields)


class TagGlyph:
    def __init__(self, name: str, tags: list[str]) -> None:
        self.name, self.tags, self.isNull = name, tags, False

    @property
    def layers(self) -> Any:
        raise AssertionError("Tag search must not read layers")

    @property
    def shapes(self) -> Any:
        raise AssertionError("Tag search must not read shapes")

    @property
    def fgGlyph(self) -> Any:
        raise AssertionError("Never read flGlyph.fgGlyph")


def tag_native(glyphs: list[TagGlyph]) -> tuple[Any, list[int]]:
    reads: list[int] = []

    def find(identity: int) -> Any:
        reads.append(identity)
        return glyphs[identity]

    package = NS(id=7, fgId=99, isNull=False, findFgId=find)
    font = NS(id=99, glyphs=[NS(id=i) for i in range(len(glyphs))])
    return NS(
        flWorkspace=NS(instance=lambda: NS(currentPackage=package)),
        CurrentFont=lambda: font,
    ), reads


def test_tag_search_single_pass_no_geometry_and_skipped_names(monkeypatch: Any) -> None:
    module = load(TITLES[0])
    native, reads = tag_native(
        [
            TagGlyph("arrow_left", ["arrow", "direction"]),
            TagGlyph("bad/name", ["arrow"]),
            TagGlyph("arrow_right", ["arrow"]),
        ]
    )
    real_capture = module.capture_tags
    monkeypatch.setattr(module, "capture_tags", lambda: real_capture(native))
    text, skipped = module.search_result(("arrow direction",))
    assert text == "/arrow_left"
    assert len(skipped) == 1 and "bad/name" in skipped[0]
    assert reads == [0, 1, 2], "Resolve every glyph only once per refresh"
    reads.clear()
    assert module.build_output(("",)) == "" and reads == []


def test_tag_deadline_stops_before_next_glyph(monkeypatch: Any) -> None:
    module = load(TITLES[0])
    native, reads = tag_native(
        [TagGlyph("A", []), TagGlyph("B", []), TagGlyph("C", [])]
    )
    ticks = iter([0.0, 2.0])
    monkeypatch.setattr(module, "monotonic", lambda: next(ticks))
    with pytest.raises(TimeoutError):
        module.capture_tags(native, deadline=1.0)
    assert reads == [0], "Deadline must stop the glyph walk early"


def box(x: float = 20, y: float = 0, w: float = 400, h: float = 700) -> Any:
    return NS(
        x=lambda: x,
        y=lambda: y,
        width=lambda: w,
        height=lambda: h,
        isNull=lambda: w == 0 and h == 0,
        isEmpty=lambda: w <= 0 or h <= 0,
    )


def occurrence(name: str, layer: str, advance: float, ink: Any, shapes: int = 1) -> Any:
    return NS(
        glyph_name=name,
        layer_name=layer,
        package_id=1,
        glyph_id=2,
        layer_id=3 if layer == "Regular" else 4,
        layer=NS(advanceWidth=advance, boundingBox=ink, shapesCount=shapes),
    )


def test_metric_capture_ratios_zero_missing_ink_and_nonfinite(monkeypatch: Any) -> None:
    module = load(TITLES[2])
    selected = NS(
        context=(1, "Regular"),
        occurrences=(
            occurrence("A", "Regular", 500, box()),
            occurrence("B", "Bold", 600, box(w=450, h=750)),
        ),
    )
    patch_reader(monkeypatch, "layer_selection", selected)
    assert module.build_output(("Advance", "A", "Regular", "Percent")) == (
        "Glyph\tLayer\tValue\tCompared\nA\tRegular\t500\t100\nB\tBold\t600\t120"
    )
    assert module.build_output(("Height", "A", "Regular", "Difference")).endswith(
        "B\tBold\t750\t50"
    )
    selected.occurrences = (occurrence("space", "Regular", 0, box(), 0),)
    assert module.build_output(("Width", "space", "Regular", "Percent")).endswith(
        "space\tRegular\tUnavailable\tUnavailable"
    )
    assert module.build_output(("Advance", "space", "Regular", "Percent")).endswith(
        "space\tRegular\t0\tUndefined (zero reference)"
    )
    selected.occurrences = (occurrence("A", "Regular", math.inf, box()),)
    with pytest.raises(ValueError, match="finite"):
        module.build_output(("Advance", "A", "Regular", "Difference"))


@pytest.mark.parametrize("title", TITLES)
def test_capture_errors_propagate_without_an_output(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    if title == TITLES[0]:

        def fail_capture(native: Any = None, *, deadline: float | None = None) -> Any:
            raise TimeoutError("Capture expired")

        monkeypatch.setattr(module, "capture_tags", fail_capture)
        fields = ("arrow",)
    else:
        patch_reader(
            monkeypatch,
            "glyph_catalog" if title == TITLES[1] else "layer_selection",
            TimeoutError("Capture expired"),
        )
        fields = tuple(field[1] for field in module.FIELDS)
    with pytest.raises(TimeoutError):
        module.build_output(fields)


class Signal:
    def __init__(self) -> None:
        self.slots: list = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)


class Widget:
    """Refuse writes over native names, including writes done during setup."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in NATIVE_NAMES:
            raise AttributeError(f"Native member collision: {name}")
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        object.__setattr__(self, "destroyed", Signal())
        self.clicked = Signal()
        self.text = ""
        self.plainText = ""
        self.deleted = False

    def setWindowTitle(self, text: str) -> None:
        pass

    def resize(self, x: int, y: int) -> None:
        pass

    def setAttribute(self, *args: Any) -> None:
        pass

    def setReadOnly(self, flag: bool) -> None:
        pass

    def addItems(self, items: list[str]) -> None:
        self._options = items

    def setCurrentIndex(self, index: int) -> None:
        self.currentText = self._options[index]

    def setText(self, text: str) -> None:
        self.text = text

    def setPlainText(self, text: str) -> None:
        self.plainText = text

    def addWidget(self, widget: Any) -> None:
        pass

    def show(self) -> None:
        pass

    def deleteLater(self) -> None:
        self.deleted = True


@pytest.mark.parametrize("title", TITLES)
def test_panel_error_clears_output_copy_recaptures_and_close_drains(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    clipboard = Widget()
    qt = NS(
        QtGui=NS(
            QWidget=Widget,
            QVBoxLayout=Widget,
            QLabel=Widget,
            QLineEdit=Widget,
            QComboBox=Widget,
            QPlainTextEdit=Widget,
            QPushButton=Widget,
            QApplication=NS(clipboard=lambda: clipboard),
        ),
        QtCore=NS(Qt=NS(Tool=1, WindowFlags=int, WA_QuitOnClose=2)),
    )
    if title == TITLES[0]:
        monkeypatch.setattr(module, "search_result", lambda fields: ("/A/V", ()))
    else:
        monkeypatch.setattr(module, "build_output", lambda fields: "/A/V")
    panel = module.show(qt, None)
    panel.refresh_output()
    assert panel.output_box.plainText == "/A/V"
    panel.copy_output()
    assert clipboard.text == "/A/V", "Copy must publish the fresh proof."
    clipboard.setText("Existing clipboard")

    def fail(fields: tuple[str, ...]) -> str:
        raise TimeoutError("Expired")

    monkeypatch.setattr(
        module, "search_result" if title == TITLES[0] else "build_output", fail
    )
    panel.copy_output()
    assert panel.output_box.plainText == "", "A failed recapture must clear stale text."
    assert clipboard.text == "Existing clipboard", (
        "A refusal must not replace the clipboard."
    )
    assert "Expired" in panel.status_line.text
    records = list(panel.signal_scope.records)
    event = NS(accept=lambda: None, ignore=lambda: pytest.fail("Close refused"))
    panel.closeEvent(event)
    assert panel.deleted
    assert all(not signal.slots for signal, _, _ in records)
    assert panel not in module._PANELS


def test_no_native_writes_or_foreign_source_imports() -> None:
    for title in TITLES:
        source = (ROOT / "Scripts" / "Tools" / f"{title}.py").read_text()
        ast.parse(source, feature_version=(3, 11))
        assert "typerig" not in "\n".join(
            line
            for line in source.splitlines()
            if line.startswith(("import ", "from "))
        )
        for forbidden in (
            "notifyChangesApplied",
            "history.commit",
            "addGlyph(",
            "applyTransform(",
        ):
            assert forbidden not in source, forbidden


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("bad", ["\0", "\u00a0", "\u2028", "\u2029", "\r", "\ud800"])
def test_bridge_refuses_lossy_text(title: str, bad: str) -> None:
    with pytest.raises(ValueError):
        load(title).checked("A" + bad)


def test_metrics_all_columns_and_changed_selection(monkeypatch: Any) -> None:
    module = load(TITLES[2])
    selected = NS(
        context=(1, "Regular"), occurrences=(occurrence("A", "Regular", 500, box()),)
    )
    patch_reader(monkeypatch, "layer_selection", selected)
    for column, value in (
        ("Advance", 500),
        ("Width", 400),
        ("Height", 700),
        ("Left", 20),
        ("Right", 80),
    ):
        assert module.build_output((column, "", "", "Difference")).endswith(
            f"A\tRegular\t{value}\t0"
        )
    for fields in (
        ("bad", "", "", "Difference"),
        ("Advance", "", "", "bad"),
        ("Advance", "missing", "Regular", "Difference"),
        ("Advance", "A", "", "Difference"),
    ):
        with pytest.raises(ValueError):
            module.build_output(fields)
    changed = NS(context=(2, "Regular"), occurrences=selected.occurrences)
    reads = iter((selected, changed, changed))
    patch_reader(monkeypatch, "layer_selection", lambda: next(reads))
    with pytest.raises(ValueError, match="changed"):
        module.capture_metrics()
    patch_reader(monkeypatch, "layer_selection", fake_selection_capture(0))
    with pytest.raises(ValueError, match="Select"):
        module.capture_metrics()


SOURCE_PREFIX = "rescued/part3/sources/kateliev_TypeRig/Scripts/TypeRig GUI/Panel/"
SOURCE_HASHES = {
    "Explorer": "537e4542754d0d7d0fe34ed6c0e142d23e81eb5c757a7da97ffa592c9e85a03d",
    "Glyph": "2e70ecb44861dc04db8a7a6a20ac64bce0d7b3bc4cb89b4e2c7ce2731537ff32",
    "Guide": "148191f7064a60b9ba2fcd18bcc220ab42ceccb25b97869ba7a054a8fda46954",
    "Layer": "c9c6aa0893b5f8dc19ca9b1461a0914a553c3c8e680e29db3d0e3208b9fb52c8",
    "Metrics": "c1925f3c9e3816f35dc66b9c259af290489b963a503379a9de5c9291cf00c83d",
    "Node": "9bc60008420a1a73c6ae2ece46ec74f6dcd2d32dbf0b2bfb40ffc92a8ca7f6c5",
    "Outline": "70b82b583b6f25e7125d303785eedce7ed84fd92b3c839acbfe667e5ea4bddc0",
    "Pairs": "2724ed38c94fe57880ebce9491f58175944cd26dbfe931097e1bf51f9ef53508",
    "Stats": "097d10d3cab764f9f780f3404d1da11cabb2c32c8685ede80084b1c3ea08ee12",
}
DESTINATIONS = {
    "Explorer": "Scripts/Tools/Symbol Tag Search.py",
    "Glyph": "fontlab-python-scriptmix/Scripts/Names/Batch Rename.py",
    "Guide": "fontlab-python-scriptmix/Scripts/Guides/Guide List Editor.py",
    "Layer": "fontlab-python-scriptmix/Scripts/Masters/Duplicate Current Layer.py",
    "Metrics": "fontlab-python-scriptmix/Scripts/Metrics/Copy Metrics From Reference.py",
    "Node": "fontlab-python-scriptmix/Scripts/Contours/Align And Distribute.py",
    "Outline": "Scripts/Contours/Node Table.py",
    "Pairs": "Scripts/Tools/Pair Proof Generator.py",
    "Stats": "Scripts/Tools/Layer Metric Comparison.py",
}
SCOPES = {
    "Explorer": "The native Font window sidebar > Tags filters glyph tags. This tool adds an AND search of several substring terms over names and tags together and copies an ordered slash proof. Read names and tags once with per-glyph deadlines; list unusable names as skipped rows. Native tags replace external textproto categories; similarity previews and contour-part assembly are not reproduced. Native Edit > Copy and Edit > Paste cover manual contour transfer.",
    "Glyph": "duplicate-of fontlab-python-scriptmix:Scripts/Names/Batch Rename.py for naming; Glyph Tags, Mark Color Palette and Unicode From Names cover metadata. Native Glyph > Duplicate Glyph... covers duplication. Difference: separate tools replace the combined panel; numbered/selective copies, inserting source glyph contents into the current glyph or mask, and measuring selected-node stems into font stem values are not reproduced. Font Info accepts manual stem values only.",
    "Guide": "duplicate-of fontlab-python-scriptmix:Scripts/Guides/Guide List Editor.py for guide coordinates, angles and names across masters. Native Tools > Guides > Add Guide creates a guide through two selected nodes; Perpendicular Guides covers its perpendicular variant. Metric Reference Lines and Glyph Tags cover related actions. Difference: no combined percentage-of-bounds/source-glyph placement, guide colour, guide tag, X/Y flip or node-naming controls.",
    "Layer": "duplicate-of fontlab-python-scriptmix:Scripts/Masters/Duplicate Current Layer.py for layer duplication. Copy Layer Between Masters, Copy Outline To Mask, Layer Cleanup, Transform and Interpolation Preview cover related actions; native Window > Panels > Layers & Masters controls visibility. Difference: no TypeRig combined layer table, delta-scaling commit or matching options.",
    "Metrics": "duplicate-of fontlab-python-scriptmix:Scripts/Metrics/Copy Metrics From Reference.py for cross-master sidebearing and advance copying. Sidebearings Tuner and Scale Advances cover adjustments; native View > Metrics Table edits expressions. Difference: no combined bounds-copy, auto-expression or font-metrics-from-node controls.",
    "Node": "duplicate-of fontlab-python-scriptmix:Scripts/Contours/Align And Distribute.py for alignment. Add Extremes, Round Coordinates, Curve All Straights, Straighten All Curves, Retract Handles and native Contour > Nodes cover basic editing; native Contour > Nodes > Ink Trap... covers the ink-trap operation. Difference: no combined Mitre/Round/Loop/Rebuild corners, round/square/normalize caps, font-metric or measurement-line alignment, italic/slope walkers, paste-aligned node memory, stored Hobby/slope/node banks, per-master collinear/monoline targets or fake-stroke controls.",
    "Outline": "Editable all-own-node table for the current glyph layer: X, Y, type and two-way selection sync. Refresh caches one auto-fact scan; Apply scans once again, and geometry deadlines start after the scan. Selection reads current-layer geometry only, works independently of edit refusals, verifies native and smart-selection flags and reports unsynced rows. Numeric edits use the App outline writer and history.commit as one Undo step; only attempted refused edits enter the kept count. A failed display refresh preserves the completed write report. Window > Panels > Node edits canvas-selected points; Node Coordinates Panel is a read-only companion. Difference: shape-local coordinates, read-only types, and no distance/angle columns or arbitrary layer selector.",
    "Pairs": "Generate Cartesian or zipped current-font name pairs with suffixes and fillers as slash proofs. Kerning/Missing Pairs also builds left-by-right combinations, filtered to missing kerning; this tool retains every requested pair and adds Zip, suffix and filler controls. Native File > Export > Metrics supplies AFM output; Classes Browser supplies class inspection. Existing-kerning String/Unicode/AFM/KRN extraction, Unicode proof strings and KRN/OpenType class-file output are not reproduced.",
    "Stats": "Compare five selected-layer measurements with a named reference as differences or percentages; copy TSV. Null or empty bounds remain unavailable and zero-reference percentages are undefined. Native View > Metrics Table edits metrics. Difference: selected layers replace arbitrary named-glyph/master matrices; row/column-relative modes and the selected-node part/whole calculator are not reproduced.",
}


def fragment_records() -> dict[str, list[dict[str, Any]]]:
    """Return the expected R1b rows with hashes of current destinations."""
    index = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    by_source = {row["target"]: row for row in index}
    records = []
    for name, digest in SOURCE_HASHES.items():
        source = SOURCE_PREFIX + name + ".py"
        row = by_source[source]
        assert row["target_sha256"] == digest, source
        destination = DESTINATIONS[name]
        path = (
            ROOT.parent / destination
            if destination.startswith("fontlab-python-scriptmix/")
            else ROOT / destination
        )
        records.append(
            {
                "family": "typerig-panel-" + name.lower(),
                "source_menu": row["menu"],
                "source": source,
                "source_sha256": digest,
                "menu": destination,
                "destination_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "entry_point": "main",
                "license": "Apache-2.0 (independent rewrite; source MPL-2.0)",
                "scope": SCOPES[name],
                "disposition": "ported"
                if name in ("Explorer", "Outline", "Pairs", "Stats")
                else "duplicate-of",
                "assets": [],
                "source_body_redistributed": False,
                "native_acceptance": "pending",
                "original_workflow_accepted": False,
            }
        )
    return {"adaptations": records, "retirements": []}


def test_every_source_has_a_hash_checked_complete_disposition() -> None:
    records = fragment_records()
    assert len(records["adaptations"]) == 9
    assert sum(row["disposition"] == "ported" for row in records["adaptations"]) == 4
    shared = json.loads((ROOT / "menu-adaptations.json").read_text())
    folded = [
        row
        for kind in ("adaptations", "retirements")
        for row in shared[kind]
        if row["source"] in {r["source"] for r in records["adaptations"]}
    ]
    by_source = sorted(records["adaptations"], key=lambda row: row["source"])
    assert sorted(folded, key=lambda row: row["source"]) == by_source, (
        "Map each source identity once, with the expected record."
    )
    for row in records["adaptations"]:
        assert (
            recorded_sha256(row['source'])
            == row["source_sha256"]
        )
        if row["disposition"] == "ported":
            script = (ROOT / row["menu"]).read_text()
            assert "App>=0.2.150.dev0" in script, "State the App floor in Setup"
        assert not row["source_body_redistributed"]
        assert "archived" not in row["scope"].lower()


def test_null_and_empty_bounds_are_unavailable(monkeypatch: Any) -> None:
    module = load(TITLES[2])
    for bounds in (box(w=0, h=0), box(w=0, h=400)):
        selected = NS(
            context=(1, "Regular"),
            occurrences=(occurrence("empty", "Regular", 500, bounds),),
        )
        patch_reader(monkeypatch, "layer_selection", selected)
        for name in ("Width", "Height", "Left", "Right"):
            assert module.build_output((name, "", "", "Difference")).endswith(
                "empty\tRegular\tUnavailable\tUnavailable"
            )


class Shape:
    """Use native property/method shapes; never construct new outlines in a port."""

    def __init__(
        self, identity: int, nodes: list[Node], *, shared: bool = False
    ) -> None:
        self.id = identity
        self.contours = [Contour(nodes, closed=True)]
        self.isComponent, self.contentLocked = False, False
        self.shapeData = NS(referenceCount=2 if shared else 1)
        self.transform = NS(
            m11=lambda: 1,
            m22=lambda: 1,
            m12=lambda: 0,
            m21=lambda: 0,
            dx=lambda: 0,
            dy=lambda: 0,
        )


@pytest.fixture
def node_world(monkeypatch: Any) -> Any:
    """Run the real outline writer and history.commit on owned native-shaped fakes."""
    history = importlib.import_module("fly.ap.history")
    module = load("Node Table")
    points = [
        Node(PointF(10, 20)),
        Node(PointF(30, 40), nodeType="off"),
        Node(PointF(50, 60)),
    ]
    shape = Shape(100, points)
    shared = Shape(101, [Node(PointF(70, 80))], shared=True)
    events: list[Any] = []
    layer = NS(
        id=51,
        name="Regular",
        isNull=False,
        autoLayer=False,
        isLocked=False,
        isLockedI=False,
        shapes=[shape, shared],
        changed=lambda: events.append("changed"),
        update=lambda: True,
        checkInitHistoryState=lambda index: events.append(("layer", index)),
    )
    package = NS(id=7, fgId=99, isNull=False)
    glyph = NS(
        id=42,
        name="A",
        package=package,
        isNull=False,
        activeLayer=layer,
        checkInitHistoryState=lambda index: events.append(("glyph", index)),
        lastModified=None,
    )
    lookups: list[int] = []

    def find(identity: int) -> Any:
        lookups.append(identity)
        assert identity == 1234, "Map the FontGate glyph id, never the package id"
        return glyph

    package.findFgId = find
    canvas = NS(isNull=False, refreshAll=lambda: events.append("canvas"))
    workspace = NS(currentPackage=package, getActiveCanvas=lambda: canvas)
    notifications: list[Any] = []
    native = NS(
        flWorkspace=NS(instance=lambda: workspace),
        CurrentGlyph=lambda: NS(id=1234),
        CurrentFont=lambda: NS(id=99),
        flGlyph=NS(updatedFgGlyphs=list),
        flItems=lambda: NS(
            notifyChangesApplied=lambda *args: notifications.append(args)
        ),
    )
    world = NS(
        module=module,
        points=points,
        shape=shape,
        shared=shared,
        layer=layer,
        package=package,
        glyph=glyph,
        native=native,
        events=events,
        lookups=lookups,
        notifications=notifications,
        facts=history.auto_facts([]),
        scans=0,
        scan_side_effect=None,
        canvas=canvas,
    )
    from fontlabapp.history import AutoFacts

    def scan_auto_facts(package: Any) -> AutoFacts:
        assert package is world.package
        world.scans += 1
        if world.scan_side_effect is not None:
            world.scan_side_effect()
        return world.facts

    assert inspect.signature(scan_auto_facts) == inspect.signature(
        history.scan_auto_facts
    )
    monkeypatch.setattr(history, "scan_auto_facts", scan_auto_facts)
    monkeypatch.setattr(
        history,
        "_native",
        lambda name: (
            native
            if name == "fontlab"
            else NS(QtCore=NS(QDateTime=NS(currentDateTimeUtc=lambda: "stamp")))
        ),
    )
    return world


def test_node_table_native_shapes_single_undo_and_kept_rows(node_world: Any) -> None:
    world = node_world
    snapshot = world.module.capture_nodes(world.native)
    assert [(r.x, r.y, r.kind) for r in snapshot.rows] == [
        (10, 20, "on"),
        (30, 40, "off"),
        (50, 60, "on"),
        (70, 80, "on"),
    ]
    assert snapshot.rows[-1].kept == "shared outline"
    result = world.module.apply_edits(
        snapshot,
        {
            (0, 0, 0): ("11.5", "-21"),
            (0, 0, 1): ("nan", "42"),
            (0, 0, 2): ("51", "61"),
            (1, 0, 0): ("100", "100"),
        },
        world.native,
    )
    assert result.changed == 2 and len(result.kept) == 2
    assert (
        "finite" in result.kept[(0, 0, 1)]
        and result.kept[(1, 0, 0)] == "shared outline"
    )
    assert (world.points[0].x, world.points[0].y) == (11.5, -21)
    assert (world.points[1].x, world.points[1].y) == (30, 40)
    assert world.notifications == [("Node Table", [world.layer, world.glyph])]
    assert world.events[:2] == [("layer", 0), ("glyph", 0)]
    assert world.glyph.lastModified == "stamp"


def test_node_table_auto_locked_stale_and_noop_refusals(node_world: Any) -> None:
    world = node_world
    snap = world.module.capture_nodes(world.native)
    world.layer.autoLayer = True
    result = world.module.apply_edits(snap, {(0, 0, 0): ("99", "99")}, world.native)
    assert result.changed == 0 and result.kept[(0, 0, 0)] == "auto layer"
    assert world.notifications == [], "Never notify an auto layer"
    world.layer.autoLayer = False
    world.layer.isLocked = True
    assert all(
        row.kept == "locked layer"
        for row in world.module.capture_nodes(world.native).rows
    )
    world.layer.isLocked = False
    world.points[0].x = 12
    result = world.module.apply_edits(
        snap, {(0, 0, 0): ("99", "99"), (0, 0, 1): ("31", "41")}, world.native
    )
    assert (
        result.changed == 1 and result.kept[(0, 0, 0)] == "node changed since Refresh"
    )
    assert world.points[0].x == 12
    snap = world.module.capture_nodes(world.native)
    before = len(world.notifications)
    result = world.module.apply_edits(snap, {(0, 0, 1): ("31", "41")}, world.native)
    assert result.changed == 0 and result.kept == {}
    assert len(world.notifications) == before
    world.layer.id = 52
    with pytest.raises(ValueError, match="changed"):
        world.module.apply_edits(snap, {}, world.native)


def test_node_selection_sync_includes_shared_own_nodes_without_history(
    node_world: Any,
) -> None:
    world = node_world
    world.shared.contours[0].nodes()[0].selected = True
    snap = world.module.capture_nodes(world.native)
    world.module.select_nodes(snap, {(0, 0, 1)}, world.native)
    assert [p.selected for p in world.points] == [False, True, False]
    assert not world.shared.contours[0].nodes()[0].selected
    assert world.events == ["canvas"] and world.notifications == []


def test_node_partial_failure_gets_undo_hint_and_one_notification(
    node_world: Any,
) -> None:
    world = node_world
    world.layer.update = lambda: False
    snap = world.module.capture_nodes(world.native)
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        world.module.apply_edits(snap, {(0, 0, 0): ("90", "80")}, world.native)
    assert world.points[0].x == 90
    assert world.notifications == [("Node Table", [world.layer, world.glyph])]


@pytest.mark.parametrize("title", TITLES)
def test_choices_are_fixed_and_failed_show_drains_signals(
    title: str, monkeypatch: Any
) -> None:
    module = load(title)
    created: list[Any] = []

    class FailingWidget(Widget):
        def __init__(self, *args: Any) -> None:
            super().__init__(*args)
            created.append(self)

        def show(self) -> None:
            raise RuntimeError("Cannot show")

    gui = NS(
        QWidget=FailingWidget,
        QVBoxLayout=Widget,
        QLabel=Widget,
        QLineEdit=Widget,
        QPlainTextEdit=Widget,
        QPushButton=Widget,
        QComboBox=Widget,
    )
    qt = NS(QtGui=gui, QtCore=NS(Qt=NS(Tool=1, WindowFlags=int, WA_QuitOnClose=2)))
    if title == TITLES[0]:
        monkeypatch.setattr(module, "search_result", lambda fields: ("/A", ()))
    else:
        monkeypatch.setattr(module, "build_output", lambda fields: "/A")
    with pytest.raises(RuntimeError, match="Cannot show"):
        module.show(qt, None)
    panel = created[0]
    assert panel.deleted and panel.signal_scope.dead and not module._PANELS
    for index in module.CHOICES:
        assert panel.input_boxes[index].currentText == module.FIELDS[index][1]


class TableItem:
    """Native items keep text/flags, not arbitrary Python row metadata."""

    def __init__(self, text: str) -> None:
        self._text, self._flags = text, 0

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text

    def setFlags(self, flags: int) -> None:
        self._flags = flags


class TableRange:
    """Match the four-required-int QTableWidgetSelectionRange constructor."""

    def __init__(self, top: int, left: int, bottom: int, right: int) -> None:
        assert all(type(value) is int for value in (top, left, bottom, right))
        self.top, self.bottom = top, bottom


class TableWidget(Widget):
    def __init__(self, rows: int, columns: int, parent: Any = None) -> None:
        super().__init__(parent)
        assert type(rows) is int and type(columns) is int
        self._cells: dict[tuple[int, int], TableItem] = {}
        self._selected: set[int] = set()
        self._blocked = False
        self.itemSelectionChanged = Signal()

    def setHorizontalHeaderLabels(self, labels: list[str]) -> None:
        assert len(labels) == 7

    def setSelectionBehavior(self, mode: int) -> None:
        pass

    def setSelectionMode(self, mode: int) -> None:
        pass

    def blockSignals(self, blocked: bool) -> None:
        self._blocked = blocked

    def setRowCount(self, count: int) -> None:
        self._cells.clear()
        self._selected.clear()

    def setItem(self, row: int, column: int, item: TableItem) -> None:
        self._cells[row, column] = item

    def item(self, row: int, column: int) -> TableItem:
        return self._cells[row, column]

    def setRangeSelected(self, area: TableRange, selected: bool) -> None:
        for row in range(area.top, area.bottom + 1):
            if selected:
                self._selected.add(row)
            else:
                self._selected.discard(row)

    def selectionModel(self) -> Any:
        return NS(
            selectedIndexes=[NS(row=lambda row=row: row) for row in self._selected]
        )


def node_qt(widget: type = Widget, button: type = Widget) -> Any:
    return NS(
        QtGui=NS(
            QWidget=widget,
            QVBoxLayout=Widget,
            QLabel=Widget,
            QPushButton=button,
            QTableWidget=TableWidget,
            QTableWidgetItem=TableItem,
            QTableWidgetSelectionRange=TableRange,
            QAbstractItemView=NS(SelectRows=1, ExtendedSelection=2),
        ),
        QtCore=NS(
            Qt=NS(
                Tool=1,
                WindowFlags=int,
                WA_QuitOnClose=2,
                ItemIsEnabled=1,
                ItemIsSelectable=2,
                ItemIsEditable=4,
            )
        ),
    )


def test_node_panel_real_shape_rows_edits_selection_and_close(
    node_world: Any, monkeypatch: Any
) -> None:
    world, module = node_world, node_world.module
    monkeypatch.setattr(module, "native_module", lambda native=None: world.native)
    panel = module.show(node_qt(), None)
    table = panel.node_table
    assert len(table._cells) == 28, "Render every node, including the shared kept row"
    assert table.item(1, 5).text() == "off"
    assert table.item(3, 6).text() == "Kept: shared outline"
    assert not table.item(3, 3)._flags & 4 and table.item(0, 3)._flags & 4
    table.item(0, 3).setText("15.5")
    world.points[1].selected = True
    panel.read_selection()
    assert table._selected == {1}
    assert table.item(0, 3).text() == "15.5", "Canvas sync must preserve staged cells"
    table._selected = {2}
    panel.write_selection()
    assert [node.selected for node in world.points] == [False, False, True]
    panel.write_cells()
    assert world.points[0].x == 15.5 and len(world.notifications) == 1
    assert len(table._cells) == 28 and "Kept" in table.item(3, 6).text()
    panel.closeEvent(
        NS(accept=lambda: None, ignore=lambda: pytest.fail("Close refused"))
    )
    assert panel.deleted and panel.snapshot_data is None and panel.signal_scope.dead


@pytest.mark.parametrize("title", (*TITLES, "Node Table"))
def test_partial_control_construction_failure_cleans_owned_callbacks(
    title: str, monkeypatch: Any, node_world: Any
) -> None:
    module = node_world.module if title == "Node Table" else load(title)
    created: list[Any] = []

    class Owner(Widget):
        def __init__(self, *args: Any) -> None:
            super().__init__(*args)
            created.append(self)

    buttons: list[Any] = []

    class FailingButton(Widget):
        def __init__(self, *args: Any) -> None:
            if buttons:
                raise RuntimeError("Second control failed")
            super().__init__(*args)
            buttons.append(self)

    qt = node_qt(Owner, FailingButton)
    qt.QtGui.QLineEdit = Widget
    qt.QtGui.QComboBox = Widget
    qt.QtGui.QPlainTextEdit = Widget
    with pytest.raises(RuntimeError, match="Second control failed"):
        module.show(qt, None)
    assert created[0].deleted and created[0].signal_scope.dead
    assert not buttons[0].clicked.slots and not module._PANELS


def test_node_scan_count_refresh_apply_only(node_world: Any, monkeypatch: Any) -> None:
    world, module = node_world, node_world.module
    monkeypatch.setattr(module, "native_module", lambda native=None: world.native)
    panel = module.show(node_qt(), None)
    assert world.scans == 1, "Opening Refresh scans facts once"

    def forbidden_scan() -> None:
        pytest.fail("Selection sync must not scan auto-layer facts")

    world.scan_side_effect = forbidden_scan
    panel.node_table._selected = {0}
    panel.write_selection()
    panel.read_selection()
    assert world.scans == 1
    world.scan_side_effect = None
    panel.node_table.item(0, 3).setText("15.5")
    panel.write_cells()
    assert world.scans == 2, (
        "Apply scans once; its post-write display reuses fresh facts"
    )
    assert world.points[0].x == 15.5
    panel.refresh_nodes()
    assert world.scans == 3, "Explicit Refresh refreshes the cached facts once"


def test_node_deadline_starts_after_scan_and_stops_during_geometry(
    node_world: Any, monkeypatch: Any
) -> None:
    world, module = node_world, node_world.module
    now = [0.0]
    world.scan_side_effect = lambda: now.__setitem__(0, 50.0)
    monkeypatch.setattr(module, "monotonic", lambda: now[0])
    snapshot = module.capture_nodes(world.native)
    assert len(snapshot.rows) == 4 and world.scans == 1
    ticks = iter([0.0, 0.3, 1.0])
    monkeypatch.setattr(module, "monotonic", lambda: next(ticks))
    with pytest.raises(TimeoutError, match="Node scan expired"):
        module.read_rows(world.layer, 1.0)
    assert world.scans == 1, "Reading geometry must not scan the font"


@pytest.mark.parametrize("refusal", ["base", "owner", "auto", "locked"])
def test_node_refused_edits_still_sync_selection(
    refusal: str, node_world: Any, monkeypatch: Any
) -> None:
    world, module = node_world, node_world.module
    history = importlib.import_module("fly.ap.history")
    if refusal == "base":
        world.facts = history.auto_facts([("Aacute", True, ("A",))])
    elif refusal == "owner":
        world.facts = history.auto_facts([("A", True, ())])
    elif refusal == "auto":
        world.layer.autoLayer = True
    else:
        world.layer.isLocked = True
    snapshot = module.capture_nodes(world.native)
    assert all(row.kept for row in snapshot.rows)

    def forbidden_scan() -> None:
        pytest.fail("A click must use cached facts")

    world.scan_side_effect = forbidden_scan
    assert module.select_nodes(snapshot, {(0, 0, 1)}, world.native) == {}
    assert [node.selected for node in world.points] == [False, True, False]
    assert world.scans == 1 and world.notifications == []
    world.scan_side_effect = None
    result = module.apply_edits(snapshot, {(0, 0, 0): ("99", "99")}, world.native)
    assert result.changed == 0 and result.kept[(0, 0, 0)]
    assert world.notifications == []


def test_node_unchanged_kept_cells_do_not_inflate_result(node_world: Any) -> None:
    world, module = node_world, node_world.module
    snapshot = module.capture_nodes(world.native)
    cells = {row.key: (repr(row.x), repr(row.y)) for row in snapshot.rows}
    result = module.apply_edits(snapshot, cells, world.native)
    assert result.changed == 0 and result.kept == {}
    assert world.notifications == []


def test_node_locked_binding_method_is_read_as_value(node_world: Any) -> None:
    world = node_world
    world.layer.isLockedI = lambda: False
    assert not world.module.capture_nodes(world.native).rows[0].kept
    world.layer.isLockedI = lambda: True
    assert world.module.capture_nodes(world.native).rows[0].kept == "locked layer"


def test_node_post_apply_refresh_failure_preserves_write_report(
    node_world: Any, monkeypatch: Any
) -> None:
    world, module = node_world, node_world.module
    monkeypatch.setattr(module, "native_module", lambda native=None: world.native)
    panel = module.show(node_qt(), None)
    real_capture = module.capture_nodes

    def capture(native: Any = None, *, facts: Any = None) -> Any:
        if world.notifications:
            raise TimeoutError("Display read expired")
        return real_capture(native, facts=facts)

    monkeypatch.setattr(module, "capture_nodes", capture)
    panel.node_table.item(0, 3).setText("15.5")
    panel.write_cells()
    assert world.points[0].x == 15.5 and len(world.notifications) == 1
    assert "Changed 1 nodes" in panel.status_line.text
    assert "one Undo step" in panel.status_line.text
    assert "Display read expired" in panel.status_line.text
    assert panel.snapshot_data is None, (
        "Do not leave a stale table enabled after a write"
    )


def test_node_selection_verifies_native_flags_and_reports_unsynced_rows(
    node_world: Any, monkeypatch: Any
) -> None:
    world, module = node_world, node_world.module

    class IgnoredSelection(Node):
        @property
        def selected(self) -> bool:
            return False

        @selected.setter
        def selected(self, value: bool) -> None:
            pass

    world.shape.contours[0]._nodes[0] = IgnoredSelection(PointF(10, 20))
    component = NS(id=102, isComponent=True)
    world.layer.shapes.append(component)
    monkeypatch.setattr(module, "native_module", lambda native=None: world.native)
    panel = module.show(node_qt(), None)
    assert panel.node_table.item(4, 6).text() == "Kept: component; edit its base glyph"
    panel.node_table._selected = {0, 4}
    panel.write_selection()
    assert "Unsynced row (0, 0, 0)" in panel.status_line.text
    assert "requested state" in panel.status_line.text
    assert "Unsynced row (2, -1, -1)" in panel.status_line.text
    assert "edit its base glyph" in panel.status_line.text
    assert world.notifications == []


def test_node_selection_preserves_smart_flags_and_clears_on_deselection(
    node_world: Any,
) -> None:
    world, module = node_world, node_world.module
    world.points[0].selected = True
    world.points[0].setProperty("__smart_selected", True)
    world.points[1].setProperty("__smart_selected", True)
    snapshot = module.capture_nodes(world.native)
    assert module.select_nodes(snapshot, {(0, 0, 1)}, world.native) == {}
    assert not world.points[0].selected
    assert world.points[0].getProperty("__smart_selected") is False
    assert world.points[1].selected
    assert world.points[1].getProperty("__smart_selected") is True
    assert world.scans == 1


def test_node_selection_property_failure_is_reported_per_row(node_world: Any) -> None:
    world, module = node_world, node_world.module

    class UnreadableSmart(Node):
        def getProperty(self, name: str) -> Any:
            raise RuntimeError("Smart selection is unreadable")

    world.shape.contours[0]._nodes[0] = UnreadableSmart(PointF(10, 20))
    snapshot = module.capture_nodes(world.native)
    errors = module.select_nodes(snapshot, {(0, 0, 0), (0, 0, 1)}, world.native)
    assert errors == {(0, 0, 0): "Smart selection is unreadable"}
    assert world.points[1].selected, (
        "One refused row must not stop the remaining selection"
    )
    assert world.scans == 1 and not world.notifications


def test_node_selection_nonfinite_coordinates_remain_selectable(
    node_world: Any,
) -> None:
    world, module = node_world, node_world.module
    world.points[0].x = math.nan
    snapshot = module.capture_nodes(world.native)
    assert snapshot.rows[0].kept == "non-finite coordinates"
    assert module.select_nodes(snapshot, {(0, 0, 0)}, world.native) == {}
    assert world.points[0].selected and world.scans == 1


def test_node_apply_display_never_uses_cached_facts_for_a_different_context(
    node_world: Any, monkeypatch: Any
) -> None:
    world, module = node_world, node_world.module
    monkeypatch.setattr(module, "native_module", lambda native=None: world.native)
    panel = module.show(node_qt(), None)
    old_notify = world.native.flItems

    def notify(*args: Any) -> None:
        old_notify().notifyChangesApplied(*args)
        world.layer.id = 52

    world.native.flItems = lambda: NS(notifyChangesApplied=notify)
    panel.node_table.item(0, 3).setText("15.5")
    panel.write_cells()
    assert "Changed 1 nodes" in panel.status_line.text
    assert "Current glyph changed after Apply" in panel.status_line.text
    assert panel.snapshot_data is None and world.scans == 2
