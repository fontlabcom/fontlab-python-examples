# this_file: tests/test_issue122_E7.py
"""Check the independent Designer polygon rewrite without running preserved code."""

import ast
import copy
import hashlib
import importlib
import importlib.util
import json
import math
import os
import re
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any
from xml.etree import ElementTree as ET

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "Scripts/Designer/Em Star Polygon.py"
FAMILIES = {
    "analogclock",
    "bubbleswidget",
    "calculatorform",
    "counterlabel",
    "datetimeedit",
    "helloglwidget",
    "multipagewidget",
    "plugins",
    "polygonwidget",
    "pydemo",
    "pythonconsolewidget",
    "main",
    "compile-on-the-fly",
    "load-ui1",
    "load-ui2",
}
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
    "data",
}


@pytest.fixture
def script() -> Any:
    spec = importlib.util.spec_from_file_location("e7_star", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_real_app_names_exist(monkeypatch: Any) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp/src"))
    scripting = importlib.import_module("fontlabapp.scripting")
    properties = importlib.import_module("fontlabapp.qt_properties")
    assert all(
        callable(getattr(scripting, name))
        for name in ("current_package", "names_dialog_type", "show_script_dialog")
    )
    assert callable(properties.value)
    history = importlib.import_module("fontlabapp.history")
    assert callable(history.commit) and callable(history.scan_auto_facts)
    masters = importlib.import_module("fontlabapp.masters")
    assert masters.associated_master("Regular@backup", ["Regular"]) == "Regular"


def test_exact_star_vertices_and_svg(script: Any) -> None:
    document = ET.fromstring(script.polygon_svg(1000, 4, 0.5, 0.25, 0))
    assert document.attrib["viewBox"] == "0 0 1000 1000"
    polygon = document.find("{http://www.w3.org/2000/svg}polygon")
    points = [
        tuple(map(float, pair.split(","))) for pair in polygon.attrib["points"].split()
    ]
    assert len(points) == 8
    assert points[0] == (1000, 500)
    assert points[1] == pytest.approx((676.776695, 323.223305))
    assert points[2] == (500, 0)
    assert points[4] == (0, 500)
    assert polygon.attrib["fill"] == "black"
    assert not list(document.iter("{http://www.w3.org/2000/svg}script"))


def test_rotation_scaling_and_maximum_points(script: Any) -> None:
    document = ET.fromstring(script.polygon_svg(2000, 128, 0.5, 0.1, 90))
    points = document[0].attrib["points"].split()
    assert len(points) == 256
    assert tuple(map(float, points[0].split(","))) == (1000, 0)
    assert script.polygon_svg(1000, 5, 0.5, 0.25, 360) == script.polygon_svg(
        1000, 5, 0.5, 0.25, 0
    )


@pytest.mark.parametrize(
    "arguments",
    [
        (0, 5, 0.5, 0.25, 0),
        (-1, 5, 0.5, 0.25, 0),
        (math.nan, 5, 0.5, 0.25, 0),
        (math.inf, 5, 0.5, 0.25, 0),
        (1000, 2, 0.5, 0.25, 0),
        (1000, 129, 0.5, 0.25, 0),
        (1000, 3.5, 0.5, 0.25, 0),
        (1000, True, 0.5, 0.25, 0),
        (1000, 5, 0.51, 0.25, 0),
        (1000, 5, 0.5, 0, 0),
        (1000, 5, 0.1, 0.2, 0),
        (1000, 5, 0.5, math.nan, 0),
        (1000, 5, 0.5, 0.25, math.inf),
        (1000, 5, 0.5, 0.25, -1),
        (1000, 5, 0.5, 0.25, 361),
        (None, 5, 0.5, 0.25, 0),
        (1e100, 5, 0.5, 0.25, 0),
        (1000, 5, 0.5, 1e-100, 0),
        (10**400, 5, 0.5, 0.25, 0),
    ],
)
def test_invalid_geometry_refused(script: Any, arguments: tuple) -> None:
    with pytest.raises(ValueError):
        script.polygon_svg(*arguments)


def test_export_is_exact_and_never_overwrites(script: Any, tmp_path: Path) -> None:
    path = tmp_path / "star.svg"
    text = script.polygon_svg(1000, 5, 0.45, 0.2, 90)
    script.save_svg(str(path), text)
    assert path.read_bytes() == text.encode("utf-8")
    with pytest.raises(FileExistsError):
        script.save_svg(str(path), "replacement")
    assert path.read_text() == text
    with pytest.raises(ValueError, match="absolute.*svg"):
        script.save_svg("relative.svg", text)
    with pytest.raises(ValueError):
        script.save_svg(str(tmp_path / "wrong.txt"), text)
    link = tmp_path / "link.svg"
    link.symlink_to(path)
    with pytest.raises(FileExistsError):
        script.save_svg(str(link), text)


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, callback: Any) -> None:
        self.slots.append(callback)

    def emit(self, *args: Any) -> None:
        for callback in self.slots:
            callback(*args)


class Widget:
    """Reject native-name collisions; expose numeric/text properties as values."""

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        assert not NATIVE_NAMES.intersection(cls.__dict__), "native class collision"

    def __setattr__(self, name: str, value: Any) -> None:
        assert name not in NATIVE_NAMES, f"native instance collision: {name}"
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.clicked = Signal()
        self.text = args[0] if args else ""
        self.value = 0
        self.items: list[Any] = []

    def setText(self, text: str) -> None:
        self.text = text

    def setPlainText(self, text: str) -> None:
        self.text = text

    def toPlainText(self) -> str:
        return self.text

    def setRange(self, low: float, high: float) -> None:
        self.range_values = (low, high)

    def setDecimals(self, count: int) -> None:
        self.decimal_count = count

    def setValue(self, value: float) -> None:
        self.value = value

    def setReadOnly(self, enabled: bool) -> None:
        self.read_only = enabled

    def setPlaceholderText(self, text: str) -> None:
        self.placeholder = text

    def setTextFormat(self, value: int) -> None:
        self.text_format = value

    def setWordWrap(self, value: bool) -> None:
        self.word_wrap = value

    def addWidget(self, widget: Any) -> None:
        self.items.append(widget)

    def resize(self, *args: Any) -> None:
        self.dimensions = args

    def close(self) -> None:
        self.did_close = True

    def setMinimumHeight(self, height: int) -> None:
        self.minimum_height = height

    def setInteractive(self, enabled: bool) -> None:
        self.interactive = enabled

    def setBackgroundBrush(self, brush: Any) -> None:
        self.background_brush = brush

    def clear(self) -> None:
        self.items.clear()

    def addPolygon(self, polygon: Any, pen: Any, brush: Any) -> None:
        self.items.append(polygon)

    def setSceneRect(self, *args: Any) -> None:
        self.scene_bounds = args

    def fitInView(self, *args: Any) -> None:
        self.fitted = args


class Base(Widget):
    def __init__(self, parent: Any, title: str, key: str) -> None:
        super().__init__()
        self.root, self.subtitle = Widget(), Widget()
        self.key = key

    def _connect(self, signal: Any, callback: Any) -> None:
        signal.connect(callback)


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    state = SimpleNamespace(package=SimpleNamespace(id=7, upm=1000), reads=0)
    app = ModuleType("fly.ap.scripting")

    def current_package(expected_id: int | None = None) -> Any:
        state.reads += 1
        if getattr(state, "error", None):
            raise state.error
        package = state.package
        return (
            package
            if expected_id is None
            or (package is not None and package.id == expected_id)
            else None
        )

    app.current_package = current_package
    app.names_dialog_type = lambda: Base
    app.show_script_dialog = lambda kind, key: kind(None)
    properties = ModuleType("fly.ap.qt_properties")
    properties.value = lambda obj, name: getattr(obj, name)
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QLabel",
                "QSpinBox",
                "QDoubleSpinBox",
                "QPlainTextEdit",
                "QLineEdit",
                "QPushButton",
                "QGraphicsScene",
                "QGraphicsView",
            )
        }
    )
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(
            Qt=SimpleNamespace(
                PlainText=0,
                KeepAspectRatio=1,
                black=2,
                white=3,
                NoPen=0,
                PenStyle=int,
                GlobalColor=int,
            )
        ),
    )
    gui.QPolygonF = lambda points: points
    gui.QPen = lambda style: style
    gui.QBrush = lambda color: color
    qt.QtCore.QPointF = lambda x, y: SimpleNamespace(x=lambda: x, y=lambda: y)
    qt.QtCore.QRectF = lambda *args: args
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.ap, fly.qt, ap.scripting, ap.qt_properties = ap, qt, app, properties
    for name, module in {
        "fly": fly,
        "fly.ap": ap,
        "fly.ap.scripting": app,
        "fly.ap.qt_properties": properties,
    }.items():
        monkeypatch.setitem(sys.modules, name, module)
    state.qt, state.scripting = qt, app
    return state


@pytest.fixture
def drawing(host: Any, monkeypatch: Any) -> Any:
    """Use real history.commit; fake only native objects and dependency reads."""
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp/src"))
    history = importlib.import_module("fontlabapp.history")
    masters = importlib.import_module("fontlabapp.masters")
    host.events, host.notifications, host.records = [], [], [("A", False, ())]
    host.corrupt, host.pending, host.glyph_missing = False, False, False
    host.fail_attach = False
    host.offset, host.alter_existing, host.extra_contour = 0.0, False, False
    host.rehandle_existing = False

    class Node:
        def __init__(self, point: Any, *, nodeType: str) -> None:
            assert nodeType == "on"
            self.x, self.y = point.x(), point.y()

        def isOn(self) -> bool:
            return True

    class Contour:
        def __init__(self, nodes: list[Any], *, closed: bool) -> None:
            self._nodes, self.closed = nodes, closed

        def nodes(self) -> list[Any]:
            host.events.append("read nodes")
            return self._nodes

    class Shape:
        def __init__(self) -> None:
            self.id, self.contours = 20, []
            self.transform = SimpleNamespace(map=lambda point: point)

        def addContour(self, contour: Any) -> None:
            self.contours.append(contour)

    class Layer:
        def __init__(self) -> None:
            self.id, self.name, self.advanceWidth = 12, "Regular", 600
            self.autoLayer, self.isNull = False, False
            self.shapes: list[Any] = []

        def checkInitHistoryState(self, number: int) -> None:
            host.events.append(("layer history", number))

        def addShape(self, shape: Any) -> Any:
            if host.fail_attach:
                raise RuntimeError("attach failed")
            attached = copy.deepcopy(shape)
            attached.id = 200 + len(self.shapes)
            host.staged, host.attached = shape, attached
            if host.rehandle_existing:
                self.shapes = copy.deepcopy(self.shapes)
                for existing in self.shapes:
                    existing.id += 1000
            if host.alter_existing:
                self.shapes[0].contours[0]._nodes[0].x += 0.1
            self.shapes.append(attached)
            attached.contours[0]._nodes[0].x += host.offset
            if host.corrupt:
                attached.contours[0]._nodes[0].x += 1
            if host.extra_contour:
                attached.contours.append(copy.deepcopy(attached.contours[0]))
            return attached

    class Glyph:
        def __init__(self) -> None:
            self.name, self.id = "A", 9
            self.isNull = False
            self.package = host.package
            self.activeLayer = Layer()
            self.layers = [self.activeLayer]

        def checkInitHistoryState(self, number: int) -> None:
            host.events.append(("glyph history", number))

    host.glyph = Glyph()
    host.package.master = "Regular"
    host.package.masters = ["Regular"]
    host.cap_height = 700

    def metrics(package: Any, layer_name: str) -> Any:
        assert package is host.package and layer_name == "Regular"
        host.events.append("FontMetrics")
        return SimpleNamespace(capsHeight=host.cap_height)

    def notify(title: str, objects: list[Any]) -> None:
        host.notifications.append((title, objects))
        host.events.append("notify")

    native = SimpleNamespace(
        CurrentGlyph=lambda: None if host.glyph_missing else host.glyph,
        FontMetrics=metrics,
        flNode=Node,
        flContour=Contour,
        flShape=Shape,
        flItems=lambda: SimpleNamespace(notifyChangesApplied=notify),
        flGlyph=SimpleNamespace(updatedFgGlyphs=lambda: [9] if host.pending else []),
    )
    host.qt.QtCore.QDateTime = SimpleNamespace(currentDateTimeUtc=lambda: "stamp")
    monkeypatch.setattr(
        history, "_native", lambda name: native if name == "fontlab" else host.qt
    )
    monkeypatch.setattr(
        history, "scan_auto_facts", lambda package: history.auto_facts(host.records)
    )
    monkeypatch.setitem(sys.modules, "fly.ap.history", history)
    monkeypatch.setitem(sys.modules, "fly.ap.masters", masters)
    sys.modules["fly.ap"].history = history
    sys.modules["fly.ap"].masters = masters
    sys.modules["fly"].fl = native
    host.native, host.history = native, history
    return host


def test_draw_exact_coordinates_one_undo_and_readback(
    script: Any, drawing: Any
) -> None:
    script.draw_current(4, 0.5, 0.25, 0)
    layer, glyph = drawing.glyph.activeLayer, drawing.glyph
    assert drawing.notifications == [("Draw Em Star Polygon", [layer, glyph])]
    assert drawing.events[:2] == ["FontMetrics", "FontMetrics"]
    assert ("layer history", 0) in drawing.events
    assert ("glyph history", 0) in drawing.events
    assert drawing.events.index("notify") < len(drawing.events) - 1
    assert "read nodes" in drawing.events[drawing.events.index("notify") + 1 :]
    assert len(layer.shapes) == 1 and len(layer.shapes[0].contours) == 1
    contour = layer.shapes[0].contours[0]
    assert contour.closed
    coordinates = [(n.x, n.y) for n in contour.nodes()]
    assert coordinates[0] == (800, 350)
    assert coordinates[1] == (477, 527)
    assert coordinates[2] == pytest.approx((300, 850))
    assert len(coordinates) == 8
    assert drawing.attached is not drawing.staged
    assert drawing.attached.id != drawing.staged.id


@pytest.mark.parametrize(
    "fault,match",
    [
        ("font", "Open a font"),
        ("glyph", "Open a glyph"),
        ("layer", "active layer"),
        ("foreign", "another font"),
        ("auto", "auto layer"),
        ("owner", "auto layers"),
        ("base", "base of auto"),
        ("pending", "pending"),
        ("cap", "cap height"),
        ("width", "advance"),
    ],
)
def test_draw_refusals_write_nothing(
    script: Any, drawing: Any, fault: str, match: str
) -> None:
    layer = drawing.glyph.activeLayer
    if fault == "font":
        drawing.package = None
    elif fault == "glyph":
        drawing.glyph_missing = True
    elif fault == "layer":
        drawing.glyph.activeLayer = None
    elif fault == "foreign":
        drawing.glyph.package = SimpleNamespace(id=8)
    elif fault == "auto":
        layer.autoLayer = True
    elif fault == "owner":
        drawing.records = [("A", True, ())]
    elif fault == "base":
        drawing.records += [("Aacute", True, ("A",))]
    elif fault == "pending":
        drawing.pending = True
    elif fault == "cap":
        drawing.cap_height = math.nan
    else:
        layer.advanceWidth = math.inf
    with pytest.raises(ValueError, match=match):
        script.draw_current(4, 0.5, 0.25, 0)
    assert not layer.shapes and not drawing.notifications
    assert not any(isinstance(e, tuple) for e in drawing.events)


@pytest.mark.parametrize("fault", ["corrupt", "fail_attach"])
def test_draw_late_failure_has_undo_hint(script: Any, drawing: Any, fault: str) -> None:
    setattr(drawing, fault, True)
    with pytest.raises(RuntimeError, match="use Edit > Undo"):
        script.draw_current(4, 0.5, 0.25, 0)
    assert len(drawing.notifications) == 1


def test_draw_button_preview_and_error_status(script: Any, drawing: Any) -> None:
    panel = script.main()
    panel.generate_button.clicked.emit()
    assert panel.preview_scene.items and not panel.preview_view.interactive
    panel.draw_button.clicked.emit(False)
    assert len(drawing.notifications) == 1 and "Drawn" in panel.status.text
    drawing.glyph.activeLayer.autoLayer = True
    panel.draw_button.clicked.emit(False)
    assert "auto layer" in panel.status.text
    assert len(drawing.notifications) == 1


def test_ui_generates_and_saves_from_fresh_font(
    script: Any,
    host: Any,
    tmp_path: Path,
) -> None:
    panel = script.main()
    panel.generate_button.clicked.emit(False)
    assert 'viewBox="0 0 1000 1000"' in panel.output.toPlainText()
    host.package = SimpleNamespace(id=8, upm=2000)
    path = tmp_path / "fresh.svg"
    panel.destination.setText(str(path))
    panel.save_button.clicked.emit(False)
    assert 'viewBox="0 0 2000 2000"' in path.read_text()
    assert path.read_text() == panel.output.toPlainText()
    assert "Saved" in panel.status.text
    assert host.reads == 4, "each action must fence the current font and UPM"
    panel.close_button.clicked.emit(False)
    assert panel.did_close


@pytest.mark.parametrize(
    "error", [ValueError("no font"), RuntimeError("native"), TimeoutError("deadline")]
)
def test_slot_errors_clear_output_and_create_no_file(
    script: Any,
    host: Any,
    tmp_path: Path,
    error: Exception,
) -> None:
    panel = script.main()
    panel.generate_button.clicked.emit()
    host.error = error
    path = tmp_path / "absent.svg"
    panel.destination.setText(str(path))
    panel.save_button.clicked.emit()
    assert not path.exists()
    assert panel.output.toPlainText() == ""
    assert str(error) in panel.status.text


def test_missing_and_changed_font_refused(script: Any, host: Any) -> None:
    host.package = None
    with pytest.raises(ValueError, match="Open a font"):
        script.current_svg(5, 0.45, 0.2, 90)
    host.package = SimpleNamespace(id=7, upm=1000)
    original = host.scripting.current_package

    def changed(expected_id: int | None = None) -> Any:
        return original() if expected_id is None else None

    host.scripting.current_package = changed
    with pytest.raises(ValueError, match="changed"):
        script.current_svg(5, 0.45, 0.2, 90)


def test_upm_change_during_capture_refused(script: Any, host: Any) -> None:
    original = host.scripting.current_package

    def changed(expected_id: int | None = None) -> Any:
        if expected_id is not None:
            host.package.upm = 2000
        return original(expected_id)

    host.scripting.current_package = changed
    with pytest.raises(ValueError, match="changed"):
        script.current_svg(5, 0.45, 0.2, 90)


def test_export_failures_and_invalid_ui_values(
    script: Any,
    host: Any,
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    panel = script.main()
    panel.inner.setValue(0.49)
    panel.outer.setValue(0.1)
    panel.generate_button.clicked.emit()
    assert "inner <= outer" in panel.status.text
    assert panel.output.toPlainText() == ""
    panel.inner.setValue(0.05)
    path = tmp_path / "kept.svg"
    path.write_text("original")
    panel.destination.setText(str(path))
    panel.save_button.clicked.emit()
    assert path.read_text() == "original"
    assert "<svg" in panel.output.toPlainText()
    monkeypatch.setattr(panel.output, "toPlainText", lambda: "changed text")
    panel.destination.setText(str(tmp_path / "new.svg"))
    panel.save_button.clicked.emit()
    assert "Qt changed" in panel.status.text
    assert not (tmp_path / "new.svg").exists()


def test_declared_preserved_sources_match_exact_bytes(script: Any) -> None:
    preserved = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", ROOT))
    matches = re.findall(
        r"# preserved-source: (.+)\n# preserved-source-sha256: ([a-f0-9]{64})",
        SCRIPT.read_text(),
    )
    assert len(matches) == 2, "both polygon identities need exact provenance"
    for path, digest in matches:
        assert hashlib.sha256((preserved / path).read_bytes()).hexdigest() == digest


def test_complete_source_denominator_and_duplicate_destinations() -> None:
    """Verify all identities read-only, including families that add no menu."""
    preserved = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", ROOT))
    rows = [
        row
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
        if any(
            f"/{group}/" in row["target"]
            for group in ("designer", "designer-ui", "pyuic")
        )
    ]
    assert len(rows) == 27, "classify all source identities, not only new menus"
    assert {Path(row["target"]).stem.rsplit("-", 1)[0] for row in rows} == FAMILIES
    for row in rows:
        assert (
            hashlib.sha256((preserved / row["target"]).read_bytes()).hexdigest()
            == (row["target_sha256"])
        ), row["menu"]
    for destination in (
        "Scripts/Widgets/Font Units Calculator.py",
        "Scripts/Dialogs/Font Glyph Inventory Tabs.py",
        "Scripts/Widgets/Glyph Modification Calendar with Formats.py",
        "Scripts/Forms/Glyph Metrics Form.py",
    ):
        assert (ROOT / destination).is_file(), destination


def test_uses_only_exposed_qt_names_and_shared_history_writer(
    script: Any, host: Any
) -> None:
    tree = ast.parse(SCRIPT.read_text())
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "gui"
        ):
            assert hasattr(host.qt.QtGui, node.attr), node.attr
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "qt"
        ):
            namespace = getattr(host.qt, node.value.attr)
            assert hasattr(namespace, node.attr), node.attr
    assert "QObject" not in vars(host.qt.QtCore)
    assert "QObject" not in vars(host.qt.QtGui)
    for forbidden in (
        "notifyChangesApplied",
        "exec(",
        "QApplication(",
        "QPainter(",
        "QtWidgets",
    ):
        assert forbidden not in SCRIPT.read_text()
    assert "773db5c24ae98ffb" in SCRIPT.read_text()
    assert "Source:" not in script.__doc__
    assert "GPL" not in script.__doc__
    assert "import the saved" not in script.__doc__.lower()
    assert "archived" not in script.__doc__.lower()


def test_draw_preserves_existing_shapes_and_refuses_changed_metrics(
    script: Any,
    drawing: Any,
    monkeypatch: Any,
) -> None:
    layer = drawing.glyph.activeLayer
    existing = drawing.native.flShape()
    existing.addContour(
        drawing.native.flContour(
            [
                drawing.native.flNode(drawing.qt.QtCore.QPointF(x, y), nodeType="on")
                for x, y in ((1, 2), (20, 2), (20, 30))
            ],
            closed=True,
        )
    )
    layer.shapes.append(existing)
    script.draw_current(4, 0.5, 0.25, 90)
    assert layer.shapes[0] is existing
    assert [(n.x, n.y) for n in existing.contours[0].nodes()] == [
        (1, 2),
        (20, 2),
        (20, 30),
    ]
    first = layer.shapes[-1].contours[0].nodes()[0]
    assert (first.x, first.y) == pytest.approx((300, 850))
    drawing.notifications.clear()

    def changed(package: Any) -> Any:
        layer.advanceWidth += 1
        return drawing.history.auto_facts(drawing.records)

    monkeypatch.setattr(drawing.history, "scan_auto_facts", changed)
    with pytest.raises(ValueError, match="changed"):
        script.draw_current(4, 0.5, 0.25, 90)
    assert not drawing.notifications and len(layer.shapes) == 2


@pytest.mark.parametrize(
    "error", [ValueError("refused"), RuntimeError("native"), TimeoutError("deadline")]
)
def test_draw_slot_contains_requested_errors(
    script: Any,
    drawing: Any,
    monkeypatch: Any,
    error: Exception,
) -> None:
    def fail(*args: Any) -> None:
        raise error

    monkeypatch.setattr(script, "draw_current", fail)
    panel = script.main()
    panel.draw_button.clicked.emit(False)
    assert panel.status.text == str(error)
    assert not drawing.notifications


def fragment_records() -> tuple[list[dict], list[dict]]:
    """Build complete integration rows from frozen identities and current targets."""
    destinations = {
        "polygonwidget": (
            "Scripts/Designer/Em Star Polygon.py",
            "Draw one closed star contour using geometry history; round translated coordinates half-up to whole units. Centre on half advance and half the associated master's FontMetrics cap height; refuse unassociated layers. Read-back permits 0.5 units per new-node coordinate and checks all pre-existing shape geometry without shape identities. Read-only preview; secondary SVG for an external vector editor.",
        ),
        "calculatorform": (
            "Scripts/Widgets/Font Units Calculator.py",
            "Current-font UPM arithmetic with font-unit, em and point results; consolidates the two-input calculation lesson.",
        ),
        "datetimeedit": (
            "Scripts/Widgets/Glyph Modification Calendar with Formats.py",
            "Current-font modification dates with popup date editors, week starts, grid, header formats and calendar navigation.",
        ),
        "multipagewidget": (
            "Scripts/Dialogs/Font Glyph Inventory Tabs.py",
            "Multi-page current-font inventory: counts, glyph names and Unicode assignments, with selectable text output.",
        ),
        "main": (
            "Scripts/Forms/Glyph Metrics Form.py",
            "Packaged Designer form loaded through PythonQt QUiLoader; current-glyph advance and sidebearing comparison.",
        ),
        "compile-on-the-fly": (
            "Scripts/Forms/Glyph Metrics Form.py",
            "Consolidate the runtime form-loading workflow into the packaged current-glyph metrics form using QUiLoader. Does not compile Python or claim pyuic feature parity.",
        ),
        "load-ui1": (
            "Scripts/Forms/Glyph Metrics Form.py",
            "Load a packaged Designer form with QUiLoader and inspect current-glyph metrics; consolidate the form-loading lesson.",
        ),
        "load-ui2": (
            "Scripts/Forms/Glyph Metrics Form.py",
            "Load and connect a packaged Designer form with QUiLoader for current-glyph metrics comparisons; consolidate the connected-form lesson.",
        ),
    }
    reasons = {
        "counterlabel": "Decorative numeric counter display; no font input or reusable FontLab output",
        "analogclock": "Wall-clock decoration has no font action or reusable FontLab output.",
        "bubbleswidget": "Animated bubble decoration has no font action or reusable FontLab output.",
        "helloglwidget": "QOpenGLContext.versionFunctions and version-specific OpenGL function wrappers are absent from FontLab PythonQt; the example also has no font purpose.",
        "plugins": "QtDesigner custom-widget interfaces and the PyQt Designer plugin loader are absent from FontLab PythonQt.",
        "pydemo": "Generic rich-text viewer has no font input or reusable font output; author and zoom controls add no distinct FontLab action.",
        "pythonconsolewidget": "Embedded interpreter duplicates FontLab's built-in Python scripting panel; a Designer console adds no distinct font action.",
    }
    licences = {name: "GPL-3.0-only" for name in reasons}
    licences.update(
        {
            "analogclock": "BSD-3-Clause AND GPL-3.0-only",
            "plugins": "BSD-3-Clause AND GPL-3.0-only",
            "pydemo": "BSD-3-Clause AND GPL-3.0-only",
        }
    )
    adaptations: list[dict] = []
    retirements: list[dict] = []
    for row in sorted(
        json.loads((ROOT / "rescue-index.json").read_text())["menus"],
        key=lambda r: r["target"],
    ):
        source = row["target"]
        if not any(
            f"/{group}/" in source for group in ("designer", "designer-ui", "pyuic")
        ):
            continue
        family = Path(source).stem.rsplit("-", 1)[0]
        item = {
            "source_menu": row["menu"],
            "source": source,
            "source_sha256": row["target_sha256"],
        }
        if family in reasons:
            item.update(
                license=licences[family], disposition="retired", reason=reasons[family]
            )
            retirements.append(item)
            continue
        destination, scope = destinations[family]
        item.update(
            menu=destination,
            family=f"designer-{family}-{'part2' if '/part2/' in source else 'part3'}",
            destination_sha256=hashlib.sha256(
                (ROOT / destination).read_bytes()
            ).hexdigest(),
            entry_point="glyph-metrics-form" if "/Forms/" in destination else "main",
            license="Apache-2.0 (independent rewrite; source Apache-2.0)",
            scope=scope,
            assets=[],
            disposition="ported" if family == "polygonwidget" else "duplicate-of",
            source_body_redistributed=False,
            native_acceptance="pending",
            original_workflow_accepted=False,
        )
        adaptations.append(item)
    return adaptations, retirements


@pytest.mark.parametrize(
    "value,expected",
    [(0.5, 1), (-0.5, -1), (1.5, 2), (-1.5, -2), (0.499999, 0), (-0.499999, 0)],
)
def test_whole_unit_rounding_is_half_up(
    script: Any, value: float, expected: int
) -> None:
    assert script.round_unit(value) == expected


@pytest.mark.parametrize("offset,accept", [(0.5, True), (-0.5, True), (0.501, False)])
def test_geometry_readback_tolerance(
    script: Any, drawing: Any, offset: float, accept: bool
) -> None:
    drawing.offset = offset
    if accept:
        script.draw_current(4, 0.5, 0.25, 0)
    else:
        with pytest.raises(RuntimeError, match="use Edit > Undo"):
            script.draw_current(4, 0.5, 0.25, 0)


def test_existing_geometry_and_extra_contour_changes_are_detected(
    script: Any, drawing: Any
) -> None:
    script.draw_current(4, 0.5, 0.25, 0)
    drawing.alter_existing = True
    with pytest.raises(RuntimeError, match="use Edit > Undo"):
        script.draw_current(4, 0.5, 0.25, 0)
    drawing.alter_existing = False
    drawing.extra_contour = True
    with pytest.raises(RuntimeError, match="use Edit > Undo"):
        script.draw_current(4, 0.5, 0.25, 0)


@pytest.mark.parametrize("layer_name", ["Regular@backup", "Regular#bracket"])
def test_layer_master_is_resolved_before_fontmetrics(
    script: Any, drawing: Any, layer_name: str
) -> None:
    drawing.glyph.activeLayer.name = layer_name
    script.draw_current(4, 0.5, 0.25, 0)
    assert len(drawing.notifications) == 1


def test_unassociated_layer_refused_before_history(script: Any, drawing: Any) -> None:
    drawing.glyph.activeLayer.name = "mask.Regular"
    with pytest.raises(ValueError, match="no associated master"):
        script.draw_current(4, 0.5, 0.25, 0)
    assert not drawing.notifications and not drawing.glyph.activeLayer.shapes
    assert "FontMetrics" not in drawing.events


def test_readback_ignores_changed_preexisting_shape_handles(
    script: Any, drawing: Any
) -> None:
    script.draw_current(4, 0.5, 0.25, 0)
    old = drawing.glyph.activeLayer.shapes[0]
    drawing.rehandle_existing = True
    script.draw_current(4, 0.5, 0.25, 0)
    current = drawing.glyph.activeLayer.shapes[0]
    assert current is not old and current.id != old.id
    assert len(drawing.notifications) == 2


def test_fragment_complete_schema_current_hashes_and_controller_dispositions() -> None:
    adaptations, retirements = fragment_records()
    assert len(adaptations) == 15 and len(retirements) == 12
    assert sum(r["disposition"] == "ported" for r in adaptations) == 2
    for row in adaptations:
        assert set(row) == {
            "source_menu",
            "source",
            "source_sha256",
            "menu",
            "family",
            "destination_sha256",
            "entry_point",
            "license",
            "scope",
            "assets",
            "disposition",
            "source_body_redistributed",
            "native_acceptance",
            "original_workflow_accepted",
        }
        assert row["scope"] and "archived" not in row["scope"].lower()
        assert row["license"] == "Apache-2.0 (independent rewrite; source Apache-2.0)"
        assert (
            row["destination_sha256"]
            == hashlib.sha256((ROOT / row["menu"]).read_bytes()).hexdigest()
        )
    counter = [r for r in retirements if "counterlabel" in r["source"]]
    assert len(counter) == 2 and all(
        r["reason"]
        == (
            "Decorative numeric counter display; no font input or reusable FontLab output"
        )
        for r in counter
    )
    assert all("license" in r and "reason" in r for r in retirements)
    assert all(
        r["menu"].endswith("Glyph Modification Calendar with Formats.py")
        for r in adaptations
        if "datetimeedit" in r["source"]
    )
