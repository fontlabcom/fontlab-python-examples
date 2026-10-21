# this_file: tests/test_issue122_E2.py
"""Check independent widget tools, exact calculations and guarded UI actions."""

import ast
import hashlib
import importlib
import json
import math
import os
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
TITLES = (
    "Font Units Calculator",
    "Glyph Proof Groups",
    "Script Icon Browser",
    "Script Palette Roles",
    "Glyph Sketch Pad",
)
ROWS = (
    ("A", "U+0041", "2026-01-02"),
    ("A.alt", "", ""),
    ("B", "U+0042 U+0392", "2026-02-03"),
)


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts" / "Widgets" / f"{title}.py"))


def test_units_arithmetic_and_conversions() -> None:
    calculate = load(TITLES[0])["calculate"]
    assert calculate(500, "+", 20, 1000, 12) == (520, 0.52, 6.24)
    assert calculate(500, "*", 1.2, 1000, 10) == (600, 0.6, 6)
    assert calculate(500, "-", 600, 2000, 20) == (-100, -0.05, -1)
    assert calculate(600, "/", 2, 1000, 10) == (300, 0.3, 3)
    for args in (
        (1, "/", 0, 1000, 12),
        (1, "**", 2, 1000, 12),
        (1, "+", 2, 0, 12),
        (1, "+", 2, 1000, -1),
        (math.inf, "+", 1, 1000, 12),
        (1e308, "*", 1e308, 1000, 12),
    ):
        with pytest.raises(ValueError):
            calculate(*args)


def test_proof_groups_exact_filter_and_chunking() -> None:
    proof = load(TITLES[1])["proof_groups"]
    assert proof(ROWS, True, False, False, 2) == "/A/B"
    assert proof(ROWS, False, True, True, 2) == "/A.alt"
    assert proof(ROWS, True, True, True, 2) == "/A/A.alt\n/B"
    assert proof((("+", "", ""), *ROWS), True, True, True, 2) == "/A/A.alt\n/B"
    assert proof((("+", "", ""),), True, True, True, 2) == ""
    for args in (
        (ROWS, False, False, True, 2),
        ((), True, True, True, 2),
        (ROWS, True, True, True, 0),
        (ROWS, True, True, True, True),
    ):
        with pytest.raises(ValueError):
            proof(*args)


def test_svg_has_exact_coordinates_and_refuses_invalid_points() -> None:
    svg = load(TITLES[4])["sketch_svg"]
    output = svg("A&alt", [[(10.0, 20.0), (30.0, 40.0)]], (0, 0, 100, 200))
    assert 'viewBox="0 -200 100 200"' in output
    assert 'points="10,20 30,40"' in output
    assert "A&amp;alt" in output and "scale(1,-1)" in output
    for strokes, box in (
        ([], (0, 0, 100, 200)),
        ([[(math.nan, 0)]], (0, 0, 100, 200)),
        ([[(0, 0)]], (0, 0, 0, 200)),
    ):
        with pytest.raises(ValueError):
            svg("A", strokes, box)


class Signal:
    """Retain exact callbacks. Disallow implicit native-slot arity trimming."""

    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in self.slots[:]:
            slot(*args)


class Widget:
    """Expose only methods used by these tools; no generic method fallback."""

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.value, self.checked, self.currentIndex = 12, False, 0
        self.items: list[Any] = []
        self.clicked, self.toggled = Signal(), Signal()
        self.currentRowChanged, self.currentIndexChanged = Signal(), Signal()
        self.textChanged = Signal()
        self.currentText = ""
        self.deleted, self.visible = False, False
        self.css = ""
        self._flags: Any = None
        self.palette = FakePalette()

    def addWidget(self, item: Any) -> None:
        self.items.append(item)

    def addLayout(self, item: Any) -> None:
        self.items.append(item)

    def addItems(self, items: Any) -> None:
        self.items.extend(items)
        self.currentText = str(self.items[self.currentIndex]) if self.items else ""

    def addItem(self, item: Any) -> None:
        self.items.append(item)

    def clear(self) -> None:
        self.items.clear()
        self.text = ""

    def setText(self, value: str) -> None:
        self.text = value

    setPlainText = setText

    def toPlainText(self) -> str:
        return self.text

    def setValue(self, value: float) -> None:
        self.value = value

    def setChecked(self, value: bool) -> None:
        self.checked = value

    def setCurrentIndex(self, value: int) -> None:
        self.currentIndex = value
        self.currentText = str(self.items[value])

    def setStyleSheet(self, value: str) -> None:
        self.css = value

    def setObjectName(self, value: str) -> None:
        self.object_name = value

    def setStyle(self, value: Any) -> None:
        self.owned_style = value

    def style(self) -> Any:
        return SimpleNamespace(standardIcon=lambda enum: ("icon", enum))

    def setForegroundRole(self, role: Any) -> None:
        self.foreground_role = role

    def setToolTip(self, value: str) -> None:
        self.tooltip = value

    def setIcon(self, icon: Any) -> None:
        self.icon = icon

    def setParent(self, parent: Any) -> None:
        self.owner = parent

    def setWindowFlags(self, flags: Any) -> None:
        assert isinstance(flags, WindowFlags)
        self._flags = flags
        self.visible = False

    def setWindowTitle(self, title: str) -> None:
        self.window_title = title

    def show(self) -> None:
        self.visible = True

    def close(self) -> bool:
        event = SimpleNamespace(accepted=True)
        event.accept = lambda: setattr(event, "accepted", True)
        event.ignore = lambda: setattr(event, "accepted", False)
        if hasattr(self, "closeEvent"):
            self.closeEvent(event)
        return bool(event.accepted)

    def deleteLater(self) -> None:
        self.deleted = True

    def update(self) -> None:
        pass

    @property
    def width(self) -> int:
        return 500

    @property
    def height(self) -> int:
        return 500

    def setEnabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def setRange(self, *args: Any) -> None:
        pass

    def setDecimals(self, *args: Any) -> None:
        pass

    def setReadOnly(self, *args: Any) -> None:
        pass

    def setWordWrap(self, *args: Any) -> None:
        pass

    def setMinimumSize(self, *args: Any) -> None:
        pass

    def setMinimumWidth(self, *args: Any) -> None:
        pass

    def setAttribute(self, *args: Any) -> None:
        pass

    def setTextFormat(self, *args: Any) -> None:
        pass

    def setPlaceholderText(self, *args: Any) -> None:
        pass

    def setToolTipDuration(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass


RESERVED = {
    "rect",
    "render",
    "move",
    "statusBar",
    "size",
    "name",
    "text",
    "width",
    "height",
    "layout",
    "children",
    "parent",
    "font",
    "palette",
    "geometry",
    "windowTitle",
    "objectName",
    "style",
    "close",
    "show",
    "resize",
    "update",
    "deleteLater",
}


class FakeColor:
    """Expose QColor channel methods, distinct from QWidget properties."""

    def __init__(self, rgba: tuple[int, int, int, int]) -> None:
        self.rgba = rgba.rgba if isinstance(rgba, FakeColor) else rgba

    def setAlpha(self, alpha: int) -> None:
        self.rgba = (*self.rgba[:3], alpha)

    def red(self) -> int:
        return self.rgba[0]

    def green(self) -> int:
        return self.rgba[1]

    def blue(self) -> int:
        return self.rgba[2]

    def alpha(self) -> int:
        return self.rgba[3]


class FakePalette:
    """Simulate the host enum-name omission while preserving numeric role 20."""

    Active, Inactive, Disabled = 0, 1, 2
    WindowText, Button, Light, Midlight, Dark, Mid, Text = range(7)
    BrightText, ButtonText, Base, Window, Shadow, Highlight = range(7, 13)
    HighlightedText, Link, LinkVisited, AlternateBase = range(13, 17)
    ToolTipBase, ToolTipText = 18, 19

    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []
        self.error: Exception | None = None
        self.overrides: dict[int, tuple[int, int, int, int]] = {}

    def currentColorGroup(self) -> int:
        return self.Active

    def color(self, group: int, role: int) -> FakeColor:
        if self.error is not None:
            raise self.error
        self.calls.append((group, role))
        if role in self.overrides:
            return FakeColor(self.overrides[role])
        return FakeColor(
            (0, 0, 0, 128 if role == 20 else 255)
            if role in (0, 6, 8, 13, 19, 20)
            else (255, 255, 255, 255)
        )


class Panel(Widget):
    """Reject collisions with QWidget members after base initialization."""

    def __init__(self, parent: Any, title: str, key: str) -> None:
        object.__setattr__(self, "_initializing", True)
        super().__init__()
        object.__setattr__(self, "_initializing", False)
        self.root, self.subtitle, self.status = Widget(), Widget(), Widget()
        self._connections: list[Any] = []
        self._closed = False

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        assert not (set(cls.__dict__) & RESERVED), (
            "A class method shadows a native QWidget member"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if not getattr(self, "_initializing", True) and name in RESERVED:
            raise AttributeError(f"Native QWidget member: {name}")
        object.__setattr__(self, name, value)

    def _connect(self, signal: Signal, slot: Any) -> None:
        def guarded(*args: Any) -> None:
            if not self._closed:
                try:
                    slot(*args)
                except Exception as error:  # noqa: BLE001 - model the guarded App slot boundary
                    self.status.setText(str(error))

        signal.connect(guarded)
        self._connections.append((signal, guarded))

    def closeEvent(self, event: Any) -> None:
        for signal, slot in self._connections:
            signal.disconnect(slot)
        self._connections.clear()
        self._closed = True
        self.deleteLater()
        event.accept()


class WindowFlags(int):
    """Match the explicit native flags value type."""


@pytest.fixture
def host(monkeypatch: pytest.MonkeyPatch) -> Any:
    qt_flags = SimpleNamespace(
        WindowFlags=WindowFlags,
        Tool=1,
        Window=2,
        WindowStaysOnTopHint=4,
        WA_QuitOnClose=8,
        PlainText=0,
        LeftButton=1,
    )
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QPushButton",
                "QLineEdit",
                "QPlainTextEdit",
                "QComboBox",
                "QDoubleSpinBox",
                "QSpinBox",
                "QCheckBox",
                "QGroupBox",
                "QVBoxLayout",
                "QHBoxLayout",
                "QListWidget",
                "QListWidgetItem",
            )
        }
    )
    gui.QWidget = NativeWidget
    gui.QPalette = FakePalette
    gui.QStyle = SimpleNamespace(SP_DialogOkButton=1, SP_DirOpenIcon=2)
    gui.QStyleFactory = SimpleNamespace(
        keys=lambda: ("Fusion",), create=lambda name: Widget()
    )
    core = SimpleNamespace(Qt=qt_flags, QPointF=lambda x, y: (x, y))
    qt = SimpleNamespace(QtGui=gui, QtCore=core)
    package = SimpleNamespace(id=7, upm=1000, master="Regular")
    state = SimpleNamespace(
        error=None,
        rows=ROWS,
        package=package,
        panel=None,
        palette=FakePalette(),
        main_palette=FakePalette(),
    )

    def capture(**kwargs: Any) -> Any:
        if state.error:
            raise state.error
        return SimpleNamespace(rows=state.rows)

    def show(cls: Any, key: str) -> Any:
        state.panel = cls(None)
        object.__setattr__(state.panel, "palette", state.palette)
        return state.panel

    def value(widget: Any, name: str) -> Any:
        found = getattr(widget, name)
        return found() if callable(found) else found

    modules = {
        "fly": {
            "qt": qt,
            "fl": SimpleNamespace(
                MainWindow=lambda: SimpleNamespace(palette=state.main_palette)
            ),
        },
        "fly.ap": {},
        "fly.ap.scripting": {
            "names_dialog_type": lambda: Panel,
            "show_script_dialog": show,
            "current_package": lambda *a: state.package,
        },
        "fly.ap.glyph_catalog": {"capture": capture},
        "fly.ap.qt_properties": {"value": value},
    }
    for name, members in modules.items():
        module = ModuleType(name)
        module.__dict__.update(members)
        if name in ("fly", "fly.ap"):
            module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
        if "." in name:
            parent, child = name.rsplit(".", 1)
            setattr(sys.modules[parent], child, module)
    state.qt = qt
    return state


@pytest.mark.parametrize("title", TITLES)
def test_panel_launch_and_connections_close(title: str, host: Any) -> None:
    module = load(title)
    panel = module["main"]()
    assert panel is host.panel
    assert panel._connections, "Each panel must wire its owned buttons"
    assert panel.close()
    assert panel.deleted and not panel._connections


@pytest.mark.parametrize("title", TITLES[:2])
def test_refresh_clears_results_and_reports_no_font_or_timeout(
    title: str, host: Any
) -> None:
    panel = load(title)["main"]()
    for error in (
        ValueError("Open a font"),
        RuntimeError("Font changed"),
        TimeoutError("Expired"),
    ):
        host.error = error
        host.package = None
        panel.preview()
        assert panel.output.toPlainText() == "", (
            "A failed refresh must clear stale output"
        )
        assert panel.status.text, "The panel must explain a refused read"


def test_ui_previews_use_current_font_and_never_write(host: Any) -> None:
    units = load(TITLES[0])["main"]()
    units.amount.setValue(500)
    units.operand.setValue(20)
    units.preview()
    assert "520" in units.output.text and "1000" in units.output.text
    groups = load(TITLES[1])["main"]()
    groups.preview()
    assert groups.output.text == "/A/B"


def test_icon_browser_filters_names_and_emits_pasteable_code(host: Any) -> None:
    panel = load(TITLES[2])["main"]()
    panel.filter_text.setText("Dir")
    panel.preview()
    assert len(panel.icons.items) == 1
    panel.icons.currentRowChanged.emit(0)
    assert "SP_DirOpenIcon" in panel.output.text
    ast.parse(panel.output.text)
    panel.icons.currentRowChanged.emit(-1)
    assert panel.output.text == ""


def test_real_app_names_exist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp" / "src"))
    for name, symbols in {
        "scripting": ("names_dialog_type", "show_script_dialog", "current_package"),
        "glyph_catalog": ("capture",),
        "qt_properties": ("value",),
        "node_coordinates": ("current_glyph",),
        "inspectors": ("outline",),
    }.items():
        module = importlib.import_module(f"fontlabapp.{name}")
        assert all(callable(getattr(module, symbol)) for symbol in symbols)


@pytest.mark.parametrize("title", TITLES)
def test_source_contract_and_no_font_writer(title: str) -> None:
    path = ROOT / "Scripts" / "Widgets" / f"{title}.py"
    text = path.read_text()
    ast.parse(text, feature_version=(3, 11))
    assert text.startswith(f"# this_file: Scripts/Widgets/{title}.py")
    for banned in (
        "notifyChangesApplied",
        "UpdateAll(",
        "QApplication(",
        "exec_(",
        "from fly.ap import",
        "issue 122",
        "deleteAll",
    ):
        assert banned not in text
    assert "native acceptance" not in text.lower()
    assert "scope unresolved" not in text.lower()
    assert "Cmd+C" not in text
    for cls in (
        node for node in ast.walk(ast.parse(text)) if isinstance(node, ast.ClassDef)
    ):
        methods = {node.name for node in cls.body if isinstance(node, ast.FunctionDef)}
        assert not methods & RESERVED, f"Native method collision in {cls.name}"
    for word in ("What:", "How:", "Why:", "Usage:", "Benefit:", "Apache-2.0"):
        assert word in text


class NativeWidget(Widget):
    """Reject Canvas subclass attributes that would replace native members."""

    def __init__(self, *args: Any) -> None:
        object.__setattr__(self, "_initializing", True)
        super().__init__(*args)
        object.__setattr__(self, "_initializing", False)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        assert not (set(cls.__dict__) & RESERVED), (
            "A class method shadows a native QWidget member"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if not getattr(self, "_initializing", True) and name in RESERVED:
            raise AttributeError(f"Native QWidget member: {name}")
        object.__setattr__(self, name, value)

    @property
    def rect(self) -> Any:
        return (0, 0, 500, 500)


class Painter:
    """Inject paint failures and record mandatory native cleanup."""

    Antialiasing = 1
    last: Any = None
    fail = False

    def __init__(self, widget: Any) -> None:
        Painter.last = self
        self.ended = False
        self.lines: list[Any] = []

    def setRenderHint(self, *args: Any) -> None:
        if Painter.fail:
            raise RuntimeError("paint failed")

    def fillRect(self, rect: Any, color: Any) -> None:
        self.background = color

    def translate(self, *args: Any) -> None:
        pass

    def scale(self, *args: Any) -> None:
        pass

    def fillPath(self, path: Any, brush: Any) -> None:
        self.reference = brush

    def setPen(self, pen: Any) -> None:
        self.pen = pen

    def drawLine(self, *args: Any) -> None:
        self.lines.append(args)

    def end(self) -> None:
        self.ended = True


def mouse(x: int, y: int) -> Any:
    return SimpleNamespace(x=lambda: x, y=lambda: y, button=lambda: 1)


def test_canvas_events_mapping_paint_failure_and_point_limit(host: Any) -> None:
    module = load(TITLES[4])
    host.qt.QtGui.QWidget = NativeWidget
    host.qt.QtGui.QPainter = Painter
    host.qt.QtGui.QColor = FakeColor
    host.qt.QtGui.QBrush = lambda value: value
    host.qt.QtGui.QPen = lambda *values: values
    status = Widget()
    changes: list[int] = []
    canvas = module["canvas_type"](host.qt, status, lambda: changes.append(1))(None)
    assert canvas.point(mouse(100, 200)) == (200, 600)
    canvas.mousePressEvent(mouse(100, 200))
    assert not canvas.strokes, "Do not draw without a captured glyph"
    canvas.reference_path = object()
    canvas.mousePressEvent(mouse(100, 200))
    canvas.mouseMoveEvent(mouse(150, 250))
    canvas.mouseReleaseEvent(mouse(200, 300))
    assert canvas.strokes == [[(200, 600), (300, 500), (400, 400)]]
    assert canvas.point_count == 3 and not canvas.drawing and changes
    Painter.fail = False
    canvas.paintEvent(None)
    assert len(Painter.last.lines) == 2 and Painter.last.ended
    Painter.fail = True
    try:
        canvas.paintEvent(None)
        assert Painter.last.ended and "paint failed" in status.text
    finally:
        Painter.fail = False
    canvas.point_count = module["MAX_POINTS"]
    canvas.mousePressEvent(mouse(0, 0))
    assert not canvas.drawing and "limit" in status.text


def test_sketch_refresh_export_and_close_allow_quit(
    host: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load(TITLES[4])
    monkeypatch.setitem(
        module["main"].__globals__,
        "capture_outline",
        lambda: ("A / Regular", object(), (0, 0, 1000, 1000)),
    )
    panel = module["main"]()
    panel.preview()
    assert panel.glyph_label == "A / Regular"
    panel.canvas.strokes = [[(10, 20), (30, 40)]]
    panel.canvas.point_count = 2
    panel.svg_text()
    assert 'points="10,20 30,40"' in panel.output.text
    panel.preview()
    assert panel.canvas.strokes and "before capturing" in panel.status.text
    assert panel.close() and panel.deleted, (
        "Scratch strokes must not veto application quit"
    )
    panel = module["main"]()
    panel.preview()
    panel.canvas.strokes = [[(10, 20), (30, 40)]]
    panel.canvas.point_count = 2
    panel.undo_stroke()
    assert panel.canvas.point_count == 0 and not panel.output.text
    panel.canvas.strokes = [[(1, 2)]]
    panel.close()
    assert panel.deleted and not panel._connections


@pytest.mark.parametrize(
    "error", [ValueError("no glyph"), RuntimeError("changed"), TimeoutError("expired")]
)
def test_sketch_refuses_failed_capture(
    host: Any, monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    module = load(TITLES[4])

    def fail() -> Any:
        raise error

    monkeypatch.setitem(module["main"].__globals__, "capture_outline", fail)
    panel = module["main"]()
    panel.preview()
    assert panel.canvas.reference_path is None and not panel.glyph_label
    assert str(error) in panel.status.text


def test_real_capture_outline_checks_current_font_glyph_master_and_deadline(
    host: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = load(TITLES[4])
    bounds = SimpleNamespace(
        x=lambda: 10, y=lambda: -200, right=lambda: 600, bottom=lambda: 700
    )
    path = SimpleNamespace(boundingRect=lambda: bounds)
    layer = SimpleNamespace(isNull=False)
    glyph = SimpleNamespace(name="A", findLayer=lambda master: layer)
    inspector = ModuleType("fly.ap.inspectors")
    outline_calls: list[Any] = []

    def read_outline(layer: Any) -> Any:
        outline_calls.append(layer)
        return path

    inspector.outline = read_outline
    coordinates = ModuleType("fly.ap.node_coordinates")
    coordinates.current_glyph = lambda package: glyph
    for native in (inspector, coordinates):
        monkeypatch.setitem(sys.modules, native.__name__, native)
        monkeypatch.setattr(
            sys.modules["fly.ap"], native.__name__.split(".")[-1], native, raising=False
        )
    capture = module["capture_outline"]
    assert capture() == ("A / Regular", path, (-100, -300, 1200, 1400))
    assert len(outline_calls) == 1, "Capture must not depend on QPainterPath equality"
    coordinates.current_glyph = lambda package: None
    with pytest.raises(ValueError, match="Open a glyph"):
        capture()
    coordinates.current_glyph = lambda package: glyph
    glyph.findLayer = lambda master: None
    with pytest.raises(ValueError, match="no layer"):
        capture()
    glyph.findLayer = lambda master: layer
    samples = iter([glyph, None])
    coordinates.current_glyph = lambda package: next(samples)
    with pytest.raises(ValueError, match="changed"):
        capture()
    coordinates.current_glyph = lambda package: glyph
    times = iter([0, 3])
    monkeypatch.setitem(capture.__globals__, "monotonic", lambda: next(times))
    with pytest.raises(TimeoutError):
        capture()


@pytest.mark.parametrize("title", TITLES[:2])
def test_preview_button_is_wired_and_publication_rejects_lossy_text(
    title: str, host: Any
) -> None:
    panel = load(title)["main"]()
    panel.preview_button.clicked.emit(True)
    assert panel.output.text
    for bad in ("x\x00", "x\u00a0", "x\u2028", "x\u2029", "x\r"):
        with pytest.raises(ValueError):
            panel.publish(bad)
    panel.output.setPlainText = lambda text: setattr(
        panel.output, "text", text.replace("A", "?")
    )
    with pytest.raises(ValueError, match="changed"):
        panel.publish("A")
    assert panel.output.text == ""


def test_helper_filters_and_edge_cases(host: Any) -> None:
    names = load(TITLES[2])["icon_names"]
    assert names(SimpleNamespace(SP_A=1, SP_CustomBase=2, other=3), "") == ("SP_A",)
    assert (
        load(TITLES[1])["proof_groups"](((".notdef", "", ""),), False, True, False, 2)
        == "/.notdef"
    )
    with pytest.raises(ValueError, match="limit"):
        load(TITLES[4])["sketch_svg"]("A", [[(0, 0)] * 20001], (0, 0, 10, 10))


# Exact census identities. Do not turn unrelated widget examples into this scope.
OFFICIAL = {
    "analogclock-d6dc56a5318ffe71": (
        "retired",
        "Wall-clock painting has no font or scripting task.",
    ),
    "calculator-356e4e807f1e789f": ("ported", "Widgets/Font Units Calculator"),
    "digitalclock-3040b9f6b267a196": (
        "retired",
        "LCD wall clock has no font or scripting task.",
    ),
    "groupbox-f702b62aa47629ad": ("ported", "Widgets/Glyph Proof Groups"),
    "icons-505d60a757bbc177": ("ported", "Widgets/Script Icon Browser"),
    "lineedits-84cb59e07adfae2c": (
        "retired",
        "name check is covered by Names > Suffix Tool and Batch Rename previews in the scriptmix collection",
    ),
    "movie-a3b3cbe51c1506c6": (
        "retired",
        "Animated-image playback has no font task; static references already have an image viewer.",
    ),
    "scribble-8e5aa13798c2763c": ("ported", "Widgets/Glyph Sketch Pad"),
    "shapedclock-248e64416b9b218c": (
        "retired",
        "A masked draggable wall clock adds no font or scripting task.",
    ),
    "styles-9e21c6536fda7a23": ("ported", "Widgets/Script Palette Roles"),
    "stylesheet-876eab33b6a99e31": ("duplicate-of", "Widgets/Script Palette Roles"),
    "tetrix-e63bffc17abf2fde": (
        "retired",
        "Falling-block game mechanics do not support font work.",
    ),
    "tooltips-e62ce3eb648cfb4c": ("duplicate-of", "Models/Glyph Sorting and Filtering"),
    "wiggly-509e781f1267967f": (
        "retired",
        "Animated system-font text does not proof the edited FontLab font.",
    ),
    "windowflags-136c45cc9f97c218": (
        "retired",
        "window-flag demo; house script panels already fix the window type",
    ),
}
MAINS = {
    "79cc15680bc2cebb": ("retired", "hello-world widget tutorial; no font task"),
    "ce3e17a7a2a03a02": ("retired", "hello-world widget tutorial; no font task"),
    "f5ddfd0eaacbf845": ("retired", "hello-world widget tutorial; no font task"),
    "31fc7691c18d55f2": ("duplicate-of", "Models/Glyph Metrics Model"),
    "a601a41dc5a3c23a": ("duplicate-of", "Text/Script Snippet Notebook"),
    "2d8e8e07a6469499": ("retired", "widget gallery tutorial; no font task"),
    "a33bb8c2dce4e115": (
        "retired",
        "fixed dark-theme tutorial; use live palette roles in script panels",
    ),
    "1bf0ade33cd6bf12": ("duplicate-of", "Models/Glyph Name Filter"),
    "f5bf995791f1e87b": ("duplicate-of", "Tools/Find Font Source Files"),
}


def preserved_source_root() -> Path:
    """Explain the archive configuration before attempting a source-byte read."""
    root = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
    if not (root / "rescued").is_dir():
        pytest.fail(
            "Set FONTLAB_PRESERVED_ROOT to the preserved fontlab-python-examples archive root (containing rescued/)."
        )
    return root


def source_dispositions() -> dict[str, tuple[str, str]]:
    """Expand the exact census mapping without executing any preserved source."""
    dispositions: dict[str, tuple[str, str]] = {}
    for prefix in (
        "rescued/part2/ports/widgets/pyqt-official/",
        "rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/",
    ):
        for stem, disposition in OFFICIAL.items():
            kind, target = disposition
            dispositions[prefix + stem + ".py"] = (
                kind,
                "Scripts/" + target + ".py" if kind != "retired" else target,
            )
    for identity, (kind, target) in MAINS.items():
        dispositions[
            f"rescued/part2/ports/widgets/pyqt-examples/main-{identity}.py"
        ] = (kind, "Scripts/" + target + ".py" if kind != "retired" else target)
    return dispositions


def integration_rows() -> dict[str, list[dict[str, Any]]]:
    """Expose exact hash-bound JSON rows for the controller's integration."""
    indexed = {
        row["target"]: row
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    result: dict[str, list[dict[str, Any]]] = {"adaptations": [], "retirements": []}
    for source, (kind, target) in source_dispositions().items():
        row = indexed[source]
        license_name = (
            "BSD-3-Clause"
            if source.endswith("main-2d8e8e07a6469499.py")
            else "MIT"
            if "/pyqt-examples/" in source
            else "Apache-2.0 (archived replacement)"
        )
        record: dict[str, Any] = {
            "source_menu": row["menu"],
            "source": source,
            "source_sha256": row["target_sha256"],
            "license": license_name,
            "disposition": kind,
        }
        if kind == "retired":
            record["reason"] = target
            result["retirements"].append(record)
        else:
            record.update(
                menu=target,
                destination_sha256=hashlib.sha256(
                    (ROOT / target).read_bytes()
                ).hexdigest(),
                entry_point="main",
                family="widgets",
                scope="Independent FontLab workflow; consolidated variants, no original feature-parity claim.",
                native_acceptance="pending",
                original_workflow_accepted=False,
            )
            result["adaptations"].append(record)
    return result


def test_complete_source_dispositions_and_preserved_hashes() -> None:
    """Read source bytes only; never import or execute a rescued example."""
    dispositions = source_dispositions()
    assert len(dispositions) == 39
    assert sum(kind == "retired" for kind, _ in dispositions.values()) == 21
    assert sum(kind == "ported" for kind, _ in dispositions.values()) == 10
    assert sum(kind == "duplicate-of" for kind, _ in dispositions.values()) == 8
    rows = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    indexed = {row["target"]: row for row in rows}
    preserved = preserved_source_root()
    for source, (kind, target) in dispositions.items():
        assert source in indexed, f"Missing census identity: {source}"
        actual = hashlib.sha256((preserved / source).read_bytes()).hexdigest()
        assert actual == indexed[source]["target_sha256"], (
            f"Source bytes changed: {source}"
        )
        if kind == "retired":
            assert len(target) > 30, "Each retirement needs a concrete reason"
        else:
            assert (ROOT / target).is_file(), (
                f"Disposition points to a missing tool: {target}"
            )


@pytest.mark.parametrize("title", TITLES)
def test_menu_entry_point_runs_with_host_shaped_fakes(title: str, host: Any) -> None:
    runpy.run_path(
        str(ROOT / "Scripts" / "Widgets" / f"{title}.py"), run_name="__main__"
    )
    assert host.panel is not None
    assert host.panel.close()


def test_icon_failure_clears_python_row_state(host: Any) -> None:
    panel = load(TITLES[2])["main"]()
    panel.__class__.style = lambda self: SimpleNamespace(
        standardIcon=lambda enum: (_ for _ in ()).throw(RuntimeError("icon failed"))
    )
    panel.preview()
    assert not panel.enum_names and not panel.icons.items and not panel.output.text


def test_palette_exact_contrast_alpha_and_missing_role() -> None:
    module = load(TITLES[3])
    contrast = module["contrast"]
    assert contrast((0, 0, 0, 255), (255, 255, 255, 255)) == 21
    assert contrast((255, 255, 255, 255), (255, 255, 255, 255)) == 1
    assert contrast((0, 0, 0, 0), (255, 255, 255, 255)) == 1
    assert contrast((0, 0, 0, 128), (255, 255, 255, 255)) == pytest.approx(4.0041069566)
    assert contrast((0, 0, 0, 255), (255, 255, 255, 128)) is None
    with pytest.raises(ValueError):
        contrast((-1, 0, 0, 255), (255, 255, 255, 255))
    assert module["role_value"](FakePalette, "PlaceholderText") == 20
    assert module["role_value"](SimpleNamespace(), "WindowText") is None


def test_palette_reads_all_roles_groups_pairs_and_emits_role_code(host: Any) -> None:
    panel = load(TITLES[3])["main"]()
    panel.preview_button.clicked.emit(True)
    assert len(host.palette.calls) == 60
    assert len(set(host.palette.calls)) == 60
    assert sum(role == 20 for _, role in host.palette.calls) == 3
    assert panel.report.text.count("/Base:") == 6
    assert panel.report.text.count(":1") == 18
    code = panel.output.text
    assert "#ffffff" not in code and "self.palette" in code
    ast.parse(code)
    scope = {"self": panel}
    exec(code, scope)  # noqa: S102 - execute only this tool's generated snippet against fakes
    assert set(scope["colors"]) == {"Active", "Inactive", "Disabled"}
    assert len(scope["colors"]["Active"]) == 20
    assert panel.subtitle.foreground_role == FakePalette.WindowText
    assert code.count("PLACEHOLDER_TEXT = 20") == 1
    assert len(code.splitlines()) < 25
    assert not host.main_palette.calls, (
        "Report and snippet must both read the panel palette"
    )
    for error in (
        ValueError("bad palette"),
        RuntimeError("changed"),
        TimeoutError("expired"),
    ):
        host.palette.error = error
        panel.preview()
        assert not panel.report.text and not panel.output.text
        assert str(error) in panel.status.text


def test_icon_selection_contains_publication_refusal(host: Any) -> None:
    panel = load(TITLES[2])["main"]()
    panel.preview()
    panel.publish = lambda text: (_ for _ in ()).throw(ValueError("bad text"))
    panel.icons.currentRowChanged.emit(0)
    assert not panel.output.text and "bad text" in panel.status.text


def test_skipped_proof_names_are_listed_without_losing_other_output(host: Any) -> None:
    host.rows = (("+", "U+002B", ""), ("@", "U+0040", ""), *ROWS)
    panel = load(TITLES[1])["main"]()
    panel.preview()
    assert panel.output.text == "/A/B"
    assert "'+'" in panel.status.text and "'@'" in panel.status.text


def test_missing_archive_has_explicit_configuration_message(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(tmp_path))
    with pytest.raises(pytest.fail.Exception, match="Set FONTLAB_PRESERVED_ROOT"):
        preserved_source_root()


def test_completion_status_is_set_only_after_result_build(host: Any) -> None:
    for title in TITLES[:3]:
        panel = load(title)["main"]()

        def fail(panel: Any = panel) -> None:
            assert "ready. Select" not in panel.status.text
            raise RuntimeError("injected build failure")

        panel.build_result = fail
        panel.preview()
        assert panel.status.text == "injected build failure"


def test_preserved_source_headers_match_index() -> None:
    indexed = {
        row["target"]: row["target_sha256"]
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    for title in TITLES:
        lines = (ROOT / "Scripts" / "Widgets" / f"{title}.py").read_text().splitlines()
        sources = [
            (i, line.removeprefix("# preserved-source: "))
            for i, line in enumerate(lines)
            if line.startswith("# preserved-source: ")
        ]
        assert sources, f"Missing source provenance in {title}"
        for line, source in sources:
            assert lines[line + 1] == "# preserved-source-sha256: " + indexed[source]


def test_integration_rows_are_complete_hash_bound_and_disjoint() -> None:
    records = integration_rows()
    assert len(records["adaptations"]) == 18 and len(records["retirements"]) == 21
    assert (
        len(
            {
                row["menu"]
                for row in records["adaptations"]
                if row["disposition"] == "ported"
            }
        )
        == 5
    )
    all_sources = [row["source"] for group in records.values() for row in group]
    assert len(all_sources) == len(set(all_sources)) == 39
    for row in records["adaptations"]:
        assert (
            row["destination_sha256"]
            == hashlib.sha256((ROOT / row["menu"]).read_bytes()).hexdigest()
        )
        assert row["family"] and row["native_acceptance"] == "pending"


def test_native_fake_geometry_is_property_valued(host: Any) -> None:
    canvas = load(TITLES[4])["canvas_type"](host.qt, Widget(), lambda: None)(None)
    assert canvas.width == canvas.height == 500
    assert canvas.rect == (0, 0, 500, 500)
    with pytest.raises(TypeError):
        canvas.rect()


@pytest.mark.parametrize(
    "missing,pairs", [("WindowText", 15), ("Base", 12), ("Light", 18)]
)
def test_missing_named_palette_role_keeps_other_roles_and_skips_pair(
    host: Any, missing: str, pairs: int
) -> None:
    module = load(TITLES[3])
    enum = SimpleNamespace(
        **{
            name: getattr(FakePalette, name)
            for name in (*module["GROUPS"], *module["ROLES"])
            if hasattr(FakePalette, name) and name != missing
        }
    )
    host.qt.QtGui.QPalette = enum
    panel = module["main"]()
    panel.preview()
    assert panel.report.text.count(f"{missing}: unavailable by name") == 3
    for foreground, background in module["PAIRS"]:
        if missing in (foreground, background):
            assert f"{foreground}/{background}:" not in panel.report.text
    assert panel.report.text.count(":1") == pairs
    assert len(host.palette.calls) == 57
    assert panel.output.text, "Missing one role must not blank the output"
    scope = {"self": panel}
    exec(panel.output.text, scope)  # noqa: S102 - generated local snippet against fakes
    assert len(scope["colors"]["Active"]) == 19


@pytest.mark.parametrize(
    "base,text",
    [
        ((250, 250, 250, 255), (15, 15, 15, 255)),
        ((20, 20, 20, 255), (240, 240, 240, 255)),
    ],
)
def test_canvas_paint_uses_live_base_and_text_roles(
    host: Any, base: Any, text: Any
) -> None:
    host.qt.QtGui.QPainter = Painter
    host.qt.QtGui.QColor = FakeColor
    host.qt.QtGui.QBrush = lambda value: value
    host.qt.QtGui.QPen = lambda *values: values
    canvas = load(TITLES[4])["canvas_type"](host.qt, Widget(), lambda: None)(None)
    canvas.palette.overrides = {FakePalette.Base: base, FakePalette.Text: text}
    canvas.reference_path = object()
    canvas.paintEvent(None)
    assert Painter.last.background.rgba == base
    assert Painter.last.reference.rgba[:3] == text[:3]
    assert Painter.last.pen[0].rgba == text
    assert Painter.last.ended
