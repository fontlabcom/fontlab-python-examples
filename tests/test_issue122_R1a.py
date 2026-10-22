# this_file: tests/test_issue122_R1a.py
# SPDX-License-Identifier: Apache-2.0
"""Verify kerning recipes and undoable native stem blends without source execution."""

import ast
import importlib
import inspect
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any
from xml.etree import ElementTree as ET

import pytest

from historical_sources import recorded_sha256

ROOT = Path(__file__).resolve().parents[1]
PATHS = (
    ROOT / "Scripts/Tools/Kerning Copy Rules.py",
    ROOT / "Scripts/Drawing/Stem Blend.py",
)
NATIVE_NAMES = {
    "font",
    "layout",
    "size",
    "width",
    "height",
    "rect",
    "update",
    "render",
    "move",
    "statusBar",
    "children",
    "parent",
    "close",
    "accept",
    "reject",
}


def load(index: int) -> dict[str, Any]:
    return runpy.run_path(str(PATHS[index]))


def test_rules_when_explicit_sources_then_offsets_and_zero_preserved() -> None:
    expand = load(0)["expand_rules"]
    pairs = {("T", "o"): -60, ("@Left", "@Right"): 0}
    assert expand("A|V A|W = T|o @ -5\nX|Y = @Left|@Right # zero", pairs) == {
        ("A", "V"): -65,
        ("A", "W"): -65,
        ("X", "Y"): 0,
    }
    assert pairs[("T", "o")] == -60, "Recipe must not mutate the snapshot"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "A|V = X|Y",
        "A|V = T|o @ nan",
        "A|V = T|o @ 1.5",
        "A|V = T|o\nA|V = T|o",
        "A|V|W = T|o",
        "A|V = T|o\u00a0",
        "A|V = T|o\0",
        "A|V = T|o\u2028",
        "A|V = T|o\u2029",
    ],
)
def test_rules_when_invalid_then_refuse_entire_output(text: str) -> None:
    with pytest.raises(ValueError):
        load(0)["expand_rules"](text, {("T", "o"): -60})


def test_rules_when_chain_then_each_reads_original_snapshot() -> None:
    assert load(0)["expand_rules"](
        "A|V = T|o\nX|Y = A|V", {("T", "o"): -60, ("A", "V"): -10}
    ) == {("A", "V"): -60, ("X", "Y"): -10}


def test_blend_when_stems_differ_then_axes_blend_independently() -> None:
    module = load(1)
    a = [(True, [(0.0, 0.0, True), (20.0, 0.0, True), (20.0, 10.0, True)])]
    b = [(True, [(0.0, 0.0, True), (40.0, 0.0, True), (40.0, 20.0, True)])]
    result = module["blend_contours"](a, b, (20, 40, 10, 20), (75, 48), (2, 3), 0)
    assert result[0][1][2] == pytest.approx((75, 48, True))
    svg = module["svg_text"]("a<&", result)
    doc = ET.fromstring(svg)
    assert doc.find("{http://www.w3.org/2000/svg}title").text == "a<&"
    assert "Z" in svg and "scale(1 -1)" in svg
    assert a[0][1][2] == (20.0, 10.0, True), "Source nodes must remain unchanged"


def test_blend_when_italic_then_unslant_interpolate_and_reslant() -> None:
    a = [(False, [(100.0, 100.0, True), (200.0, 100.0, True)])]
    b = [(False, [(200.0, 200.0, True), (400.0, 200.0, True)])]
    result = load(1)["blend_contours"](a, b, (50, 100, 40, 80), (75, 48), (1, 1), 45)
    assert result[0][1][0][:2] == pytest.approx((120, 120))
    assert "Z" not in load(1)["svg_text"]("open", result)


@pytest.mark.parametrize(
    "stems,target,scales",
    [
        ((50, 50, 40, 80), (60, 60), (1, 1)),
        ((50, 100, 40, 80), (101, 60), (1, 1)),
        ((50, 100, 40, 80), (60, 60), (0, 1)),
        ((50, 100, 40, 80), (float("nan"), 60), (1, 1)),
    ],
)
def test_blend_when_invalid_numeric_input_then_refused(
    stems: tuple, target: tuple, scales: tuple
) -> None:
    shape = [(True, [(0.0, 0.0, True), (100.0, 100.0, True)])]
    with pytest.raises(ValueError):
        load(1)["blend_contours"](shape, shape, stems, target, scales, 0)


def test_blend_when_incompatible_or_empty_then_refused() -> None:
    blend = load(1)["blend_contours"]
    args = ((50, 100, 40, 80), (75, 60), (1, 1), 0)
    a = [(True, [(0.0, 0.0, True)])]
    for b in ([], [(False, [(0.0, 0.0, True)])], [(True, [(0.0, 0.0, False)])]):
        with pytest.raises(ValueError):
            blend(a, b, *args)
    with pytest.raises(ValueError):
        blend([], [], *args)


def test_svg_when_curves_then_controls_and_closure_retained() -> None:
    data = [
        (
            True,
            [
                (0.0, 0.0, True),
                (10.0, 0.0, False),
                (20.0, 30.0, False),
                (30.0, 30.0, True),
            ],
        ),
        (False, [(0.0, 0.0, True), (10.0, 20.0, False), (30.0, 30.0, True)]),
    ]
    text = load(1)["svg_text"]("curves", data)
    assert "C 10 0 20 30 30 30" in text and "Q 10 20 30 30" in text
    for bad in ([(False, [(1.0, 2.0, False)])], [(True, [(float("inf"), 0.0, True)])]):
        with pytest.raises(ValueError):
            load(1)["svg_text"]("bad", bad)


@pytest.mark.parametrize("index,suffix", [(0, ".txt"), (1, ".svg")])
def test_export_when_new_absolute_then_no_overwrite(
    index: int, suffix: str, tmp_path: Path
) -> None:
    save = load(index)["export_new"]
    path = tmp_path / ("output" + suffix)
    save(str(path), "payload")
    assert path.read_text() == "payload"
    with pytest.raises(FileExistsError):
        save(str(path), "changed")
    with pytest.raises(ValueError):
        save("relative" + suffix, "payload")


def app_names_used() -> dict[str, set[str]]:
    """Use the G1 alias/attribute inspection shape, without importing batch fixtures."""
    found: dict[str, set[str]] = {}
    for path in PATHS:
        tree = ast.parse(path.read_text())
        aliases = {
            a.asname: a.name
            for n in ast.walk(tree)
            if isinstance(n, ast.Import)
            for a in n.names
            if a.name.startswith("fly.ap.")
        }
        for alias, name in aliases.items():
            found.setdefault(name, set()).update(
                n.attr
                for n in ast.walk(tree)
                if isinstance(n, ast.Attribute)
                and isinstance(n.value, ast.Name)
                and n.value.id == alias
            )
    return found


def test_real_app_names_when_installed_then_fly_aliases_resolve() -> None:
    import fly

    assert fly.ALIASES["ap"] == "fontlabapp"
    used = app_names_used()
    assert {
        "fly.ap.scripting",
        "fly.ap.draft_signals",
        "fly.ap.qt_properties",
        "fly.ap.node_coordinates",
        "fly.ap.kerning_batch",
        "fly.ap.history",
        "fly.ap.layer_writer",
        "fly.ap.outline_writer",
    } <= used.keys()
    for name, attributes in used.items():
        module = importlib.import_module(name)
        assert module is importlib.import_module(name.replace("fly.ap.", "fontlabapp."))
        assert (
            not Path(module.__file__)
            .resolve()
            .is_relative_to(ROOT.parent / "fontlab-fontlabapp/src")
        ), "Gate must use installed App, not inject App src"
        for attribute in attributes:
            assert hasattr(module, attribute), f"{name}.{attribute}"


def fake_current_package(expected_id: int | None = None) -> Any | None:
    return None


def fake_current_glyph(package: Any) -> Any | None:
    return None


def test_app_fakes_when_compared_then_exact_signatures() -> None:
    for module, name, fake in (
        ("scripting", "current_package", fake_current_package),
        ("node_coordinates", "current_glyph", fake_current_glyph),
    ):
        real = getattr(importlib.import_module("fontlabapp." + module), name)
        assert inspect.signature(real) == inspect.signature(fake), (
            f"Wrong fake shape for {module}.{name}"
        )


class NativeNode:
    def __init__(self, point: Any, *, nodeType: str = "on") -> None:
        self.x, self.y = point
        self.kind = nodeType == "on"
        self.nodeType = nodeType

    def isOn(self) -> bool:
        return self.kind

    def getProperties(self) -> list:
        return []


class NativeContour:
    def __init__(self, nodes: list, *, closed: bool = True) -> None:
        self._nodes, self.closed = nodes, closed
        self.isTT = any(node.nodeType == "off" for node in nodes)

    def nodes(self) -> list:
        return self._nodes

    def getProperties(self) -> list:
        return []


def test_native_fakes_when_optional_positionals_then_rejected() -> None:
    with pytest.raises(TypeError):
        NativeNode((0, 0), "off")
    with pytest.raises(TypeError):
        NativeContour([], True)
    assert NativeNode((0, 0)).getProperties() == NativeContour([]).getProperties() == []


@pytest.mark.parametrize("index", [0, 1])
def test_source_when_parsed_then_typed_and_no_native_name_shadow(index: int) -> None:
    tree = ast.parse(PATHS[index].read_text(), feature_version=(3, 11))
    assert (
        PATHS[index]
        .read_text()
        .startswith("# this_file: " + str(PATHS[index].relative_to(ROOT)))
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assigned = {n.name for n in node.body if isinstance(n, ast.FunctionDef)}
            assigned |= {
                n.targets[0].id
                for n in node.body
                if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
            }
            assigned |= {
                n.targets[0].attr
                for n in ast.walk(node)
                if isinstance(n, ast.Assign)
                and isinstance(n.targets[0], ast.Attribute)
                and isinstance(n.targets[0].value, ast.Name)
                and n.targets[0].value.id == "self"
            }
            assert not assigned & NATIVE_NAMES, (
                f"Native name collision: {assigned & NATIVE_NAMES}"
            )
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, node.name
            assert all(
                a.annotation is not None
                for a in node.args.args + node.args.kwonlyargs
                if a.arg not in {"self", "cls"}
            ), node.name
    assert not any(
        isinstance(n, ast.ImportFrom) and (n.module or "").startswith("fly.ap")
        for n in ast.walk(tree)
    )


def test_dispositions_when_checked_then_all_source_bytes_and_targets_match() -> None:
    import hashlib

    names = {
        "Anchor",
        "AutoMetrics",
        "CleanKerning",
        "Clipboard",
        "Contour",
        "CopyKerning",
        "Corner",
        "Delta",
        "DeltaNew",
        "Element",
    }
    panel = "rescued/part3/sources/kateliev_TypeRig/Scripts/TypeRig GUI/Panel/"
    shared = json.loads((ROOT / "menu-adaptations.json").read_text())
    rows = {
        section: [
            row
            for row in shared[section]
            if row["source"].startswith(panel) and Path(row["source"]).stem in names
        ]
        for section in ("adaptations", "retirements")
    }
    assert len(rows["adaptations"]) == 6 and len(rows["retirements"]) == 4
    assert {
        Path(row["source"]).stem for row in rows["adaptations"] + rows["retirements"]
    } == names, "Keep exactly the ten assigned source identities"
    census = {
        r["menu"]: r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    for row in rows["adaptations"] + rows["retirements"]:
        original = census[row["source_menu"]]
        assert row["source"] == original["target"]
        assert (
            row["source_sha256"]
            == original["target_sha256"]
            == recorded_sha256(row['source'])
        )
        if "menu" in row:
            destination = (
                ROOT.parent / row["menu"]
                if row["menu"].startswith("fontlab-python-scriptmix/")
                else ROOT / row["menu"]
            )
            assert destination.is_file(), row["menu"]
            assert (
                hashlib.sha256(destination.read_bytes()).hexdigest()
                == row["destination_sha256"]
            ), row["menu"]
        assert row["source_body_redistributed"] is False


STATE: dict[str, Any] = {}


@pytest.fixture
def world(monkeypatch: Any) -> Any:
    """Patch only context acquisition; all other App calls stay real."""
    scripting = importlib.import_module("fly.ap.scripting")
    coordinates = importlib.import_module("fly.ap.node_coordinates")
    package = NS(
        id=9, master="Light", upm=1000, masters=("Light", "Bold"), italicAngle_value=-12
    )
    layers = {}
    for index, name in enumerate(package.masters):
        contour = NativeContour(
            [NativeNode((0, 0)), NativeNode((100 * (index + 1), 100 * (index + 1)))]
        )
        shape = NS(
            isComponent=False,
            contours=[contour],
            transform=NS(isIdentity=lambda: True),
            shapeData=NS(referenceCount=1),
        )
        layers[name] = NS(
            id=index,
            name=name,
            isNull=False,
            shapes=[shape],
            isMasterLayer=True,
            autoLayer=False,
            advanceWidth=500,
        )
    glyph = NS(
        id=20,
        name="a",
        package=package,
        findLayer=layers.get,
        layers=list(layers.values()),
    )
    STATE.clear()
    STATE.update(package=package, glyph=glyph)

    def context(expected_id: int | None = None) -> Any | None:
        item = STATE.get("package")
        return item if item is not None and expected_id in (None, item.id) else None

    def active(package: Any) -> Any | None:
        return STATE.get("glyph")

    assert inspect.signature(context) == inspect.signature(scripting.current_package)
    assert inspect.signature(active) == inspect.signature(coordinates.current_glyph)
    monkeypatch.setattr(scripting, "current_package", context)
    monkeypatch.setattr(coordinates, "current_glyph", active)
    package.findName = lambda name: (
        NS(isNull=False) if name in {"a", "A", "V", "T", "o"} else None
    )
    package.kerning = lambda master: NS(groups={})
    return NS(package=package, glyph=glyph, layers=layers)


def test_capture_when_native_shapes_then_detached_and_no_font_write(world: Any) -> None:
    label, first, second = load(1)["capture_pair"]("Light", "Bold")
    assert label == "a" and first[0][1][-1] == (100.0, 100.0, True)
    assert second[0][1][-1] == (200.0, 200.0, True)
    first[0][1].clear()
    assert len(world.layers["Light"].shapes[0].contours[0].nodes()) == 2
    world.layers["Light"].shapes[0].isComponent = True
    with pytest.raises(ValueError, match="plain contour"):
        load(1)["capture_pair"]("Light", "Bold")


def test_capture_when_no_font_glyph_or_layer_then_clear_refusal(world: Any) -> None:
    capture = load(1)["capture_pair"]
    with pytest.raises(ValueError, match="Both named"):
        capture("Light", "Missing")
    STATE["glyph"] = None
    with pytest.raises(ValueError, match="Open a glyph"):
        capture("Light", "Bold")
    STATE["package"] = None
    with pytest.raises(ValueError, match="Open a font"):
        capture("Light", "Bold")


def test_capture_when_changed_or_timed_out_then_no_artifact(world: Any) -> None:
    module = load(1)
    nodes = world.layers["Light"].shapes[0].contours[0]._nodes
    before = nodes[0].isOn

    def changing() -> bool:
        nodes[1].x += 1
        return before()

    nodes[0].isOn = changing
    with pytest.raises(ValueError, match="changed"):
        module["capture_pair"]("Light", "Bold")
    with pytest.raises(TimeoutError):
        module["read_contours"](world.layers["Light"], 0)


def test_pair_list_when_snapshot_then_real_app_validation_and_exact_text(
    world: Any, monkeypatch: Any
) -> None:
    batch = importlib.import_module("fly.ap.kerning_batch")
    scripting = importlib.import_module("fontlabapp.scripting")
    # kerning_batch binds current_package and kerning_pairs at module import.
    monkeypatch.setattr(batch, "current_package", scripting.current_package)

    def pairs(package: Any, master: str, *, typed: bool = False) -> dict:
        return {("T", "o"): -50, ("A", "V"): -10}

    real = scripting.kerning_pairs
    assert inspect.signature(pairs) == inspect.signature(real)
    monkeypatch.setattr(batch, "kerning_pairs", pairs)
    text = load(0)["build_pair_list"]("A|V = T|o @ -5")
    assert text == "# Master: Light\nA V -55\n"
    importer = runpy.run_path(str(ROOT / "Scripts/Tools/Import Kerning Pair List.py"))
    rows = importer["parse_pairs"](text)
    assert len(rows) == 1 and rows[0]["value"] == -55 and not rows[0]["error"]
    with pytest.raises(ValueError, match="Unknown glyph"):
        load(0)["build_pair_list"]("missing|V = T|o")
    with pytest.raises(ValueError, match="range"):
        load(0)["build_pair_list"]("A|V = T|o @ 10000")
    STATE["package"] = None
    with pytest.raises(ValueError, match="Open a font"):
        load(0)["build_pair_list"]("A|V = T|o")


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.fail = False

    def connect(self, call: Any) -> None:
        self.slots.append(call)

    def disconnect(self, call: Any) -> bool:
        if self.fail:
            return False
        self.slots.remove(call)
        return True

    def emit(self) -> None:
        for call in list(self.slots):
            call()


class Widget:
    """Reject native-member shadowing, while keeping Qt properties as attributes."""

    def __init__(self, *args: Any) -> None:
        self.text = ""
        self.clicked, self.textChanged, self.destroyed = Signal(), Signal(), Signal()
        self.currentIndexChanged = Signal()
        self.options: list[str] = []
        self.currentText = ""
        self.deleted = False
        self.contents: list[Any] = []
        self.readonly = False
        self.visible = False

    def __setattr__(self, name: str, value: Any) -> None:
        if name in NATIVE_NAMES:
            raise AttributeError(f"Native slot cannot be overwritten: {name}")
        object.__setattr__(self, name, value)

    def setWindowTitle(self, title: str) -> None:
        self.title = title

    def setAttribute(self, attribute: Any, value: Any) -> None:
        pass

    def resize(self, width: int, height: int) -> None:
        pass

    def addWidget(self, widget: Any) -> None:
        self.contents.append(widget)

    def addLayout(self, widget: Any) -> None:
        self.contents.append(widget)

    def addRow(self, label: str, widget: Any) -> None:
        self.contents.append((label, widget))

    def addItems(self, items: list[str]) -> None:
        self.options.extend(items)
        if items:
            self.currentText = items[0]

    def setCurrentIndex(self, index: int) -> None:
        self.currentText = self.options[index]
        self.currentIndexChanged.emit()

    def clear(self) -> None:
        self.options.clear()
        self.currentText = ""

    def setReadOnly(self, value: bool) -> None:
        self.readonly = value

    def setText(self, text: str) -> None:
        self.text = text
        self.textChanged.emit()

    def setPlainText(self, text: str) -> None:
        self.setText(text)

    def toPlainText(self) -> str:
        return self.text

    def show(self) -> None:
        self.visible = True

    def deleteLater(self) -> None:
        self.deleted = True


def fake_qt() -> Any:
    gui = NS(
        **dict.fromkeys(
            (
                "QWidget",
                "QVBoxLayout",
                "QFormLayout",
                "QLabel",
                "QPlainTextEdit",
                "QLineEdit",
                "QComboBox",
                "QPushButton",
            ),
            Widget,
        )
    )
    gui.QApplication = NS(clipboard=lambda: CLIPBOARD)
    return NS(QtGui=gui, QtCore=NS(Qt=NS(WindowFlags=int, Tool=1, WA_QuitOnClose=2)))


@pytest.mark.parametrize("index", [0, 1])
def test_panel_when_closed_then_disconnect_before_deletion_and_retry(
    index: int,
) -> None:
    panel = load(index)["show"](fake_qt(), None)
    assert panel.visible and panel.result_field.readonly
    with pytest.raises(AttributeError, match="Native slot"):
        panel.render = "bad"
    records = list(panel.scope.records)
    signal = records[-1][0]
    signal.fail = True
    event = NS(ignore=lambda: None, accept=lambda: None)
    panel.closeEvent(event)
    assert not panel.deleted and panel.scope.records, "Keep failed disconnections owned"
    signal.fail = False
    panel.closeEvent(event)
    assert panel.deleted and not panel.scope.records
    assert all(not signal.slots for signal, _, _ in records)


@pytest.mark.parametrize("index", [0, 1])
def test_panel_when_parent_destroyed_then_owner_released(index: int) -> None:
    panel = load(index)["show"](fake_qt(), None)
    panel.destroyed.emit()
    assert panel.scope.dead and not panel.scope.records


@pytest.mark.parametrize("index", [0, 1])
def test_panel_when_bad_build_then_clear_old_output(index: int) -> None:
    panel = load(index)["show"](fake_qt(), None)
    panel.content = "old"
    panel.build_result()
    assert panel.content == "" and panel.result_field.text == ""
    assert panel.status_line.text
    panel.release_owner()


@pytest.mark.parametrize("text,count", [("", 2), ("1 nan", 2), ("1 2 3", 2), ("a", 1)])
def test_numbers_when_invalid_then_user_error(text: str, count: int) -> None:
    with pytest.raises(ValueError):
        load(1)["numbers"](text, count)


@pytest.mark.parametrize(
    "first,second,target,expected",
    [(50, 100, 50, 0), (50, 100, 100, 100), (100, 50, 75, 50)],
)
def test_blend_when_endpoints_or_descending_stems_then_exact(
    first: float, second: float, target: float, expected: float
) -> None:
    a = [(False, [(0.0, 0.0, True), (10.0, 10.0, True)])]
    b = [(False, [(100.0, 100.0, True), (110.0, 110.0, True)])]
    result = load(1)["blend_contours"](
        a, b, (first, second, first, second), (target, target), (1, 1), 0
    )
    assert result[0][1][0][:2] == (expected, expected)


def test_svg_when_precision_or_invalid_xml_then_preserve_or_refuse() -> None:
    module = load(1)
    number = 0.12345678901234567
    text = module["svg_text"]("a", [(False, [(number, 1.0, True), (1.0, 1.0, True)])])
    path = ET.fromstring(text).find(".//{http://www.w3.org/2000/svg}path").attrib["d"]
    assert float(path.split()[1]) == number, "Keep full double precision in SVG"
    with pytest.raises(ValueError, match="controls"):
        module["path_text"](
            True,
            [
                (0.0, 0.0, True),
                (1.0, 1.0, False),
                (2.0, 2.0, False),
                (3.0, 3.0, False),
                (4.0, 4.0, True),
            ],
        )
    for label in ("a\0", "a\ud800", "a\uffff"):
        with pytest.raises(ValueError):
            module["svg_text"](label, [(False, [(0.0, 0.0, True)])])
    with pytest.raises(ValueError, match="frame"):
        module["svg_text"]("wide", [(False, [(-1e308, 0.0, True), (1e308, 1.0, True)])])


def test_svg_panel_when_built_then_exports_exact_visible_artifact(
    world: Any, tmp_path: Path
) -> None:
    panel = load(1)["show"](fake_qt(), None)
    for field, value in zip(
        panel.fields,
        (
            "Light",
            "Bold",
            "50 100",
            "40 80",
            "75 60",
            "1 1",
            "0",
            str(tmp_path / "blend.svg"),
        ),
        strict=True,
    ):
        if field.options:
            field.setCurrentIndex(field.options.index(value))
        else:
            field.setText(value)
    panel.build_result()
    assert panel.content == panel.result_field.text and "<svg" in panel.content
    panel.save_result()
    assert (tmp_path / "blend.svg").read_text() == panel.content
    panel.fields[5].setText("2 2")
    assert panel.content == panel.result_field.text == "", (
        "Editing controls invalidates the artifact"
    )
    panel.release_owner()


@pytest.mark.parametrize("error_type", [ValueError, RuntimeError, TimeoutError])
@pytest.mark.parametrize("index", [0, 1])
def test_panel_when_capture_fails_then_error_stays_inside_slot(
    index: int, error_type: type[Exception], monkeypatch: Any
) -> None:
    module = load(index)
    panel = module["show"](fake_qt(), None)
    if index == 1:
        for field in panel.fields[2:5]:
            field.setText("50 100")
    name = "build_pair_list" if index == 0 else "prepare_blend"

    def fail(*args: Any) -> Any:
        raise error_type("capture failed")

    # Patch the actual globals used by functions returned by runpy.
    monkeypatch.setitem(panel.build_result.__func__.__globals__, name, fail)
    buttons = [
        w for w in panel.box.contents if isinstance(w, Widget) and w.clicked.slots
    ]
    buttons[0].clicked.emit()
    assert panel.content == "" and "capture failed" in panel.status_line.text
    panel.release_owner()


def test_new_scripts_when_read_only_then_no_font_writer() -> None:
    prohibited = {
        "commit",
        "notifyChangesApplied",
        "write_kerning",
        "set_glyph",
        "applyTransform",
        "addLayer",
        "addShape",
    }
    for path in PATHS[:1]:
        tree = ast.parse(path.read_text())
        calls = {
            n.func.attr
            for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        }
        assert not calls & prohibited, f"Unexpected font write in {path.name}"


@pytest.mark.parametrize("rule", ["A|V=T|o@-5", "A|V = T|o @-5", "A|V = T|o @ -5"])
def test_rules_accept_compact_adjustment(rule: str) -> None:
    assert load(0)["expand_rules"](rule, {("T", "o"): -50}) == {("A", "V"): -55}


def test_rules_multiple_equals_has_actionable_message() -> None:
    with pytest.raises(ValueError, match="Use exactly one ="):
        load(0)["expand_rules"]("A|V = T|o = X|Y", {})


def test_tt_consecutive_controls_are_quadratics() -> None:
    data = [
        (0.0, 0.0, True),
        (20.0, 40.0, False),
        (60.0, 40.0, False),
        (80.0, 0.0, True),
    ]
    path = load(1)["path_text"](False, data, True)
    assert path == "M 0 0 Q 20 40 40 40 Q 60 40 80 0"
    assert "C " not in path


def test_kerning_tool_lives_next_to_importer() -> None:
    assert (ROOT / "Scripts/Tools/Kerning Copy Rules.py").is_file()
    assert not (ROOT / "Scripts/Kerning/Kerning Copy Rules.py").exists()


CLIPBOARD = NS(text="")
CLIPBOARD.setText = lambda text: setattr(CLIPBOARD, "text", text)


@pytest.mark.parametrize("index", [0, 1])
def test_copy_button_uses_existing_application(index: int) -> None:
    panel = load(index)["show"](fake_qt(), None)
    panel.content = "exact result"
    panel.copy_result()
    assert CLIPBOARD.text == "exact result"
    assert (
        "Import Kerning Pair List" in panel.status_line.text
        if index == 0
        else "may change" in panel.status_line.text
    )
    panel.release_owner()


def test_layer_choices_and_angle_prefill(world: Any) -> None:
    panel = load(1)["show"](fake_qt(), None)
    assert panel.fields[0].options == ["Light", "Bold"]
    assert (
        panel.fields[0].currentText == "Light" and panel.fields[1].currentText == "Bold"
    )
    assert panel.fields[6].text == "12", "Rightward slant is minus native italic angle"
    panel.release_owner()


def test_tt_read_and_blend_keep_native_kind(world: Any) -> None:
    contour = NativeContour(
        [
            NativeNode((0, 0)),
            NativeNode((20, 40), nodeType="off"),
            NativeNode((60, 40), nodeType="off"),
            NativeNode((80, 0)),
        ],
        closed=False,
    )
    world.layers["Light"].shapes[0].contours = [contour]
    data = load(1)["read_contours"](world.layers["Light"], float("inf"))
    assert data[0][2] is True
    blended = load(1)["blend_contours"](
        data, data, (20, 40, 10, 20), (30, 15), (1, 1), 0
    )
    assert blended[0][2] is True
    assert "Q 20 40 40 40 Q 60 40 80 0" in load(1)["svg_text"]("TT", blended)


@pytest.fixture
def native_world(world: Any, monkeypatch: Any) -> Any:
    """Run the real App history commit over native-shape fakes; never fake commit."""
    history = importlib.import_module("fly.ap.history")
    native = ModuleType("fontlab")
    notifications: list = []
    snapshots: list = []
    world.pending = ()
    world.facts = history.auto_facts((("a", False, ()),))
    world.fail_settle = False
    world.refuse_add = False
    world.fail_after_attach = False
    world.fail_readback = False

    class Shape:
        def __init__(self) -> None:
            self.contours: list = []
            self.isComponent = False
            self.transform = NS(isIdentity=lambda: True)
            self.shapeData = NS(referenceCount=1)

        def addContour(
            self, contour: Any, check_duplicate: bool = False, validate: bool = True
        ) -> None:
            self.contours.append(contour)

    class Layer:
        def __init__(self) -> None:
            self.name, self.advanceWidth = "", 0.0
            self.isNull, self.autoLayer = False, False
            self.shapes: list = []
            self.id = 77

        def addShape(self, shape: Any) -> None:
            self.shapes.append(shape)

        def changed(self) -> None:
            if world.fail_settle:
                raise RuntimeError("settle failed")

        def update(self) -> bool:
            if world.fail_readback:
                self.shapes[0].contours[0].nodes()[0].x += 1
            return True

    def add_layer(layer: Any) -> None:
        if not world.refuse_add:
            world.layers[layer.name] = layer
            world.glyph.layers.append(layer)
        if world.fail_after_attach:
            raise RuntimeError("add failed after attach")

    def auto_facts(package: Any) -> history.AutoFacts:
        return world.facts

    assert inspect.signature(auto_facts) == inspect.signature(history.scan_auto_facts)
    monkeypatch.setattr(history, "scan_auto_facts", auto_facts)
    world.glyph.addLayer = add_layer
    world.glyph.bindDependencies = lambda: None
    world.glyph.checkInitHistoryState = lambda code: snapshots.append(code)
    native.flNode, native.flContour, native.flLayer, native.flShape = (
        NativeNode,
        NativeContour,
        Layer,
        Shape,
    )
    native.flGlyph = NS(updatedFgGlyphs=lambda: world.pending)
    native.flItems = lambda: NS(
        notifyChangesApplied=lambda title, items: notifications.append(
            (title, list(items))
        )
    )
    qt = fake_qt()
    qt.QtCore.QPointF = lambda x, y: (x, y)
    qt.QtCore.QDateTime = NS(currentDateTimeUtc=lambda: "STAMP")
    monkeypatch.setitem(sys.modules, "fontlab", native)
    monkeypatch.setitem(sys.modules, "PythonQt", qt)
    fly = importlib.import_module("fly")
    monkeypatch.setitem(fly.__dict__, "fl", native)
    monkeypatch.setitem(fly.__dict__, "qt", qt)
    world.notifications, world.snapshots = notifications, snapshots
    return world


def bound_plan(module: dict[str, Any]) -> dict[str, Any]:
    return module["prepare_blend"](
        "Light", "Bold", (50, 100, 40, 80), (75, 60), (1, 1), 0
    )


def test_blend_creates_one_layer_and_one_history_notification(
    native_world: Any,
) -> None:
    module = load(1)
    plan = bound_plan(module)
    assert "Stem 75x60 (Light)" == plan["name"]
    result = module["create_layer"](plan)
    world = native_world
    created = world.layers[plan["name"]]
    assert "one Undo step" in result
    assert len(world.notifications) == 1 and world.notifications[0][1] == [
        created,
        world.glyph,
    ]
    assert world.snapshots == [0], (
        "Only owner glyph history starts; source layers stay untouched"
    )
    assert (
        created.advanceWidth == 500
        and created.shapes[0].contours[0].nodes()[-1].x == 150
    )
    assert len(world.glyph.layers) == 3
    assert world.layers["Light"].shapes[0].contours[0].nodes()[-1].x == 100
    with pytest.raises(ValueError, match="already exists"):
        module["create_layer"](plan)
    assert len(world.notifications) == 1


def test_tt_native_layer_preserves_controls_and_is_tt(native_world: Any) -> None:
    for layer in native_world.layers.values():
        layer.shapes[0].contours = [
            NativeContour(
                [
                    NativeNode((0, 0)),
                    NativeNode((20, 40), nodeType="off"),
                    NativeNode((60, 40), nodeType="off"),
                    NativeNode((80, 0)),
                ],
                closed=False,
            )
        ]
    module = load(1)
    plan = bound_plan(module)
    module["create_layer"](plan)
    contour = native_world.layers[plan["name"]].shapes[0].contours[0]
    assert contour.isTT and not contour.closed
    assert [node.nodeType for node in contour.nodes()] == ["on", "off", "off", "on"]


@pytest.mark.parametrize("kind", ["stale", "auto-owner", "auto-base", "pending"])
def test_unsafe_layer_writes_refused_before_history(
    native_world: Any, kind: str
) -> None:
    module = load(1)
    plan = bound_plan(module)
    world = native_world
    history = importlib.import_module("fly.ap.history")
    if kind == "stale":
        world.layers["Light"].shapes[0].contours[0].nodes()[0].x += 1
    elif kind == "auto-owner":
        world.facts = history.auto_facts((("a", True, ()),))
    elif kind == "auto-base":
        world.facts = history.auto_facts((("aacute", True, ("a",)), ("a", False, ())))
    else:
        world.pending = (1,)
    with pytest.raises(ValueError):
        module["create_layer"](plan)
    assert (
        world.snapshots == []
        and world.notifications == []
        and len(world.glyph.layers) == 2
    )


@pytest.mark.parametrize(
    "kind", ["fail_settle", "refuse_add", "fail_after_attach", "fail_readback"]
)
def test_native_failure_retains_undo_hint_and_created_notification(
    native_world: Any, kind: str
) -> None:
    module = load(1)
    plan = bound_plan(module)
    setattr(native_world, kind, True)
    with pytest.raises(RuntimeError, match="Undo"):
        module["create_layer"](plan)
    assert len(native_world.notifications) == 1
    if kind != "refuse_add":
        assert native_world.layers[plan["name"]] in native_world.notifications[0][1], (
            "Attached new layers must remain in partial-write notification"
        )


@pytest.mark.parametrize(
    "name", ["Stem 75@60 (Light)", "Stem 75#60 (Light)", "|temp|Stem 75x60 (Light)"]
)
def test_reserved_layer_names_are_refused(name: str) -> None:
    with pytest.raises(ValueError, match="Layer name must not"):
        load(1)["checked_layer_name"](name, ("Light", "Bold"))


@pytest.mark.parametrize("master", ["Li@ght", "Li#ght"])
def test_reserved_master_text_refused_before_history(
    native_world: Any, master: str
) -> None:
    native_world.package.master = master
    with pytest.raises(ValueError, match="Layer name must not"):
        bound_plan(load(1))
    assert native_world.notifications == native_world.snapshots == []


def test_generated_layer_name_is_not_native_master_syntax(native_world: Any) -> None:
    module = load(1)
    plan = bound_plan(module)
    trimmed = plan["name"].split("@", 1)[0].split("#", 1)[0]
    assert trimmed.casefold() not in {
        name.casefold() for name in native_world.package.masters
    }
    assert not plan["name"].startswith("|temp|")
    result = module["create_layer"](plan)
    assert "becomes the active layer" in result


def test_literal_master_name_collision_is_refused(native_world: Any) -> None:
    native_world.package.masters += ("Stem 75x60 (Light)",)
    with pytest.raises(ValueError, match="master name"):
        bound_plan(load(1))
    assert native_world.notifications == native_world.snapshots == []


def test_writer_does_not_repeat_native_dependency_binding(native_world: Any) -> None:
    def forbidden() -> None:
        raise AssertionError("addLayer already binds dependencies")

    native_world.glyph.bindDependencies = forbidden
    module = load(1)
    module["create_layer"](bound_plan(module))
    assert len(native_world.notifications) == 1


@pytest.mark.parametrize("scale", [0.7, 0.8])
@pytest.mark.parametrize("rounding", [True, False])
def test_blend_readback_accepts_native_rounding_and_snapping(native_world: Any, scale: float, rounding: bool) -> None:
    module = load(1)
    world = native_world
    world.layers["Light"].advanceWidth = 523.4
    from fly import fl

    class StoredLayer(fl.flLayer):
        @property
        def advanceWidth(self) -> float:
            return self.stored_width

        @advanceWidth.setter
        def advanceWidth(self, value: float) -> None:
            self.stored_width = float(round(value)) if rounding else value

    fl.flLayer = StoredLayer
    original = world.glyph.addLayer

    def rounded_add(layer: Any) -> None:
        for shape in layer.shapes:
            for contour in shape.contours:
                for node in contour.nodes():
                    for axis in ("x", "y"):
                        value = getattr(node, axis)
                        if abs(value - round(value)) < 1e-5:
                            setattr(node, axis, float(round(value)))
        original(layer)

    world.glyph.addLayer = rounded_add
    plan = module["prepare_blend"]("Light", "Bold", (50, 100, 40, 80),
                                   (50 * scale, 40 * scale), (scale, scale), 0)
    assert "one Undo step" in module["create_layer"](plan)
    assert world.layers[plan["name"]].advanceWidth == (523 if rounding else 523.4)
