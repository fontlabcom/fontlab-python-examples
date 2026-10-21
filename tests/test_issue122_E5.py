# this_file: tests/test_issue122_E5.py
"""Exercise the drawing ports without executing preserved sources or FontLab."""

import ast
import hashlib
import importlib
import json
import math
import os
import re
import runpy
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS
from typing import Any, ClassVar

import pytest

ROOT = Path(__file__).resolve().parents[1]
TITLES = ("Glyph Outline SVG",)


def load(title: str) -> dict[str, Any]:
    """Load a new menu without starting its panel."""
    return runpy.run_path(str(ROOT / "Scripts/Drawing" / f"{title}.py"))


@pytest.mark.parametrize("title", (*TITLES, "Glyph SVG Reference"))
def test_menu_import_is_host_independent(title: str) -> None:
    assert callable(load(title)["main"]), "Menu must import without a native runtime"


@pytest.mark.parametrize("title", TITLES)
def test_svg_save_is_explicit_exact_and_never_overwrites(
    title: str, tmp_path: Path
) -> None:
    save = load(title)["save_svg"]
    target = tmp_path / "proof.svg"
    text = '<svg xmlns="http://www.w3.org/2000/svg"><title>é</title></svg>'
    save(str(target), text)
    assert target.read_bytes() == text.encode("utf-8"), "SVG bytes must remain exact"
    with pytest.raises(ValueError, match="exist"):
        save(str(target), "changed")
    assert target.read_bytes() == text.encode("utf-8")
    for name, payload in [
        ("relative.svg", text),
        (str(tmp_path / "bad.txt"), text),
        (str(tmp_path / "empty.svg"), ""),
    ]:
        with pytest.raises(ValueError):
            save(name, payload)


@pytest.mark.parametrize("title", (*TITLES, "Glyph SVG Reference"))
def test_real_app_names_are_available(monkeypatch: Any, title: str) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp" / "src"))
    for module, names in {
        "scripting": ("current_package", "show_script_dialog"),
        "node_coordinates": ("current_glyph",),
        "inspectors": ("outline", "outline_source"),
        "qt_properties": ("value",),
        "draft_signals": ("Scope",),
    }.items():
        real = importlib.import_module("fontlabapp." + module)
        for name in names:
            assert callable(getattr(real, name)), f"Missing real App {module}.{name}"
    assert load(title)["TITLE"] == title


@pytest.fixture
def app(monkeypatch: Any) -> dict[str, Any]:
    """Expose the real property and lifecycle helpers behind the Fly alias."""
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp" / "src"))
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.ap = ap
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", ap)
    modules = {}
    for name in (
        "qt_properties",
        "draft_signals",
        "scripting",
        "inspectors",
        "node_coordinates",
    ):
        real = importlib.import_module("fontlabapp." + name)
        fake = ModuleType("fly.ap." + name)
        fake.__dict__.update(real.__dict__)
        monkeypatch.setitem(sys.modules, "fly.ap." + name, fake)
        setattr(ap, name, fake)
        modules[name] = fake
    return modules


@pytest.mark.parametrize("title", (*TITLES, "Glyph SVG Reference"))
def test_capture_refuses_missing_stale_and_timeout(
    app: dict[str, Any], title: str
) -> None:
    m = load(title)
    app["scripting"].current_package = lambda *args: None
    with pytest.raises(ValueError, match="font"):
        m["capture_outline"]()
    package = NS(
        id=1,
        fgId=2,
        master="Regular",
        upm=1000,
        descender_value=-200,
        ascender_value=800,
    )
    layer = NS(id=5, isNull=False, advanceWidth=300)
    glyph = NS(id=3, name="A", package=package, findLayer=lambda name: layer)
    app["scripting"].current_package = lambda *args: package
    app["node_coordinates"].current_glyph = lambda pkg: glyph
    app["inspectors"].outline_source = lambda item: ((True, ((0, 0),)),)
    path = NS(isEmpty=lambda: False)
    app["inspectors"].outline = lambda item: path
    captured = m["capture_outline"]()
    label, result = captured[:2]
    if title == TITLES[0]:
        assert captured[2] == (300, -200, 800)
    assert label == "A / Regular" and result is path
    app["node_coordinates"].current_glyph = lambda pkg: None
    with pytest.raises(ValueError, match="glyph"):
        m["capture_outline"]()
    app["node_coordinates"].current_glyph = lambda pkg: glyph

    def changed(item: Any) -> Any:
        package.master = "Bold"
        return path

    app["inspectors"].outline = changed
    with pytest.raises(ValueError, match="changed"):
        m["capture_outline"]()
    app["inspectors"].outline = lambda item: path
    m["capture_outline"].__globals__["monotonic"] = iter((0, 0, 0, 3)).__next__
    with pytest.raises(TimeoutError):
        m["capture_outline"]()


@pytest.mark.parametrize("title", (*TITLES, "Glyph SVG Reference"))
def test_no_font_writes_or_native_member_collisions(title: str) -> None:
    tree = ast.parse((ROOT / "Scripts/Drawing" / f"{title}.py").read_text())
    forbidden = {
        "render",
        "size",
        "layout",
        "update",
        "font",
        "move",
        "statusBar",
        "actions",
        "rect",
        "data",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            assert (
                not {
                    item.name for item in node.body if isinstance(item, ast.FunctionDef)
                }
                & forbidden
            )
        if isinstance(node, ast.Attribute):
            if (
                isinstance(node.ctx, ast.Store)
                and isinstance(node.value, ast.Name)
                and node.value.id == "self"
            ):
                assert node.attr not in forbidden | {
                    "actions",
                    "children",
                    "parent",
                    "geometry",
                    "style",
                    "palette",
                    "windowTitle",
                    "objectName",
                }
            assert node.attr not in {
                "notifyChangesApplied",
                "fgGlyph",
                "applyTransform",
                "clone",
                "currentFrame",
            }


class Signal:
    """Keep exact owned callbacks for lifecycle verification."""

    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.refuse = False

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> bool:
        if self.refuse:
            return False
        self.slots.remove(slot)
        return True

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


class Widget:
    """Reject instance names that shadow common native members."""

    RESERVED: ClassVar[set[str]] = {
        "render",
        "size",
        "layout",
        "update",
        "font",
        "move",
        "statusBar",
        "actions",
        "rect",
        "data",
    }

    def __init__(self, *args: Any) -> None:
        self.destroyed = Signal()
        self.clicked = Signal()
        self.valueChanged = Signal()
        self.currentIndexChanged = Signal()
        self.text = ""
        self.value = 0.0
        self.currentIndex = 0
        self.deleted = False
        self.items: list[Any] = []

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self.RESERVED:
            raise AssertionError(f"Native member collision: {name}")
        object.__setattr__(self, name, value)

    def setWindowTitle(self, value: str) -> None:
        self.title = value

    def setAttribute(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def addWidget(self, value: Any) -> None:
        self.items.append(value)

    def addLayout(self, value: Any) -> None:
        self.items.append(value)

    def setWordWrap(self, value: bool) -> None:
        pass

    def setTextFormat(self, value: Any) -> None:
        pass

    def setText(self, value: str) -> None:
        self.text = value

    def setReadOnly(self, value: bool) -> None:
        pass

    def setMaximumHeight(self, value: int) -> None:
        pass

    def setPlaceholderText(self, value: str) -> None:
        pass

    def setPlainText(self, value: str) -> None:
        self.text = value

    def toPlainText(self) -> str:
        return self.text

    def addItems(self, values: list[str]) -> None:
        self.items.extend(values)

    def setRange(self, *args: Any) -> None:
        pass

    def setDecimals(self, value: int) -> None:
        pass

    def setValue(self, value: float) -> None:
        self.value = value
        self.valueChanged.emit(value)

    def setCurrentIndex(self, value: int) -> None:
        self.currentIndex = value
        self.currentIndexChanged.emit(value)

    def clear(self) -> None:
        self.items.clear()

    def addPath(self, *args: Any) -> None:
        self.items.append(args)

    def itemsBoundingRect(self) -> Any:
        return NS()

    def setSceneRect(self, value: Any) -> None:
        self.scene_box = value

    def fitInView(self, *args: Any) -> None:
        self.fit_box = args[0]

    def deleteLater(self) -> None:
        self.deleted = True

    def close(self) -> None:
        self.closeEvent(Event())


class Event:
    """Record whether a close is allowed."""

    def __init__(self) -> None:
        self.accepted = False

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.accepted = False


@pytest.fixture
def qt() -> Any:
    """Use property-shaped native doubles, including a noncallable currentIndex."""
    clipboard = NS(setText=lambda value: setattr(clipboard, "text", value), text="")

    class Path:
        def __init__(self, source: Any) -> None:
            self.source = source
            self.rule = None

        def setFillRule(self, rule: Any) -> None:
            self.rule = rule

        def boundingRect(self) -> Any:
            return self.source.boundingRect()

    class Transform:
        def __init__(self, *args: float) -> None:
            self.coefficients = args

        def map(self, path: Any) -> Any:
            rect = path.boundingRect()
            a, b, c, d, dx, dy = self.coefficients
            points = [
                (a * x + c * y + dx, b * x + d * y + dy)
                for x in (rect.x, rect.x + rect.width)
                for y in (rect.y, rect.y + rect.height)
            ]
            left, top = min(x for x, y in points), min(y for x, y in points)
            right, bottom = max(x for x, y in points), max(y for x, y in points)
            mapped = NS(x=left, y=top, width=right - left, height=bottom - top)
            return NS(boundingRect=lambda: mapped)

    names = (
        "QWidget",
        "QVBoxLayout",
        "QHBoxLayout",
        "QLabel",
        "QComboBox",
        "QDoubleSpinBox",
        "QGraphicsScene",
        "QGraphicsView",
        "QPlainTextEdit",
        "QLineEdit",
        "QPushButton",
    )
    gui = NS(
        **dict.fromkeys(names, Widget),
        QPainterPath=Path,
        QTransform=Transform,
        QPen=lambda value: value,
        QBrush=lambda value: value,
        QColor=lambda value: value,
        QApplication=NS(clipboard=lambda: clipboard),
    )
    core = NS(
        QRectF=lambda x, y, width, height: NS(x=x, y=y, width=width, height=height),
        Qt=NS(
            Window=1,
            WA_QuitOnClose=2,
            PlainText=3,
            NoPen=4,
            KeepAspectRatio=5,
            OddEvenFill=6,
            WindingFill=7,
            IgnoreAspectRatio=9,
        ),
    )
    return NS(QtGui=gui, QtCore=core, clipboard=clipboard)


@pytest.mark.parametrize("title", TITLES)
def test_panel_capture_preview_copy_save_and_close(
    app: dict[str, Any], qt: Any, title: str, tmp_path: Path
) -> None:
    m = load(title)
    panel = m["panel_type"](qt)(None)
    assert not panel.result
    panel.copy_svg()
    assert "Capture" in panel.message.text
    m["panel_type"].__globals__["capture_outline"] = lambda: (
        "A / Regular",
        NS(boundingRect=lambda: NS(x=40, y=20, width=120, height=680)),
        (300, -200, 800),
    )
    m["panel_type"].__globals__["svg_text"] = lambda *args: "<svg>artwork</svg>"
    panel.capture_result()
    assert panel.result == "<svg>artwork</svg>"
    assert Path(panel.file_entry.text).is_absolute() and panel.file_entry.text.endswith(
        "A_Regular.svg"
    )
    assert len(panel.canvas.items) == 1, "Preview must show captured artwork"
    assert vars(panel.canvas.scene_box) == {
        "x": 0,
        "y": -800,
        "width": 300,
        "height": 1000,
    }
    assert panel.viewer.fit_box is panel.canvas.scene_box
    panel.copy_svg()
    assert qt.clipboard.text == panel.result
    target = tmp_path / "panel.svg"
    panel.file_entry.text = str(target)
    panel.save_result()
    assert target.read_text() == panel.result
    if title == TITLES[0]:
        assert panel.proof_path().rule == 7
        panel.fill_choice.currentIndex = 1
        assert panel.proof_path().rule == 6
    event = Event()
    panel.closeEvent(event)
    assert event.accepted and panel.deleted
    assert panel.scope.dead and panel.terminal.dead
    assert panel.snapshot is None


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("error_type", (ValueError, RuntimeError, TimeoutError))
def test_slots_clear_stale_output_and_report(
    app: dict[str, Any], qt: Any, title: str, error_type: type[Exception]
) -> None:
    m = load(title)
    panel = m["panel_type"](qt)(None)

    def fail() -> Any:
        raise error_type("capture stopped")

    m["panel_type"].__globals__["capture_outline"] = fail
    panel.result = "stale"
    panel.capture_result()
    assert panel.result == "" and panel.snapshot is None
    assert "capture stopped" in panel.message.text
    panel.refresh_proof()
    assert "Capture" in panel.message.text


@pytest.mark.parametrize("title", (*TITLES, "Glyph SVG Reference"))
def test_disconnect_failure_preserves_close_retry_and_registry(
    app: dict[str, Any], qt: Any, title: str, monkeypatch: Any
) -> None:
    m = load(title)
    panel = m["panel_type"](qt)(None)
    registry = {m["KEY"]: panel}
    monkeypatch.setattr(sys, "_fontlab_samples", registry, raising=False)
    emitter = panel.scope.records[0][0]
    emitter.refuse = True
    event = Event()
    panel.closeEvent(event)
    assert not event.accepted and not panel.deleted and registry
    emitter.refuse = False
    panel.closeEvent(event)
    assert event.accepted and not registry


@pytest.mark.parametrize("title", (*TITLES, "Glyph SVG Reference"))
def test_main_uses_host_registry_and_error_boundary(
    app: dict[str, Any], qt: Any, title: str
) -> None:
    import fly

    fly.qt = qt
    m = load(title)
    app["scripting"].show_script_dialog = lambda cls, key: key
    assert m["main"]() == m["KEY"]

    def fail(*args: Any) -> Any:
        raise TimeoutError("host timed out")

    errors = []
    qt.QtGui.QMessageBox = NS(warning=lambda *args: errors.append(args))
    app["scripting"].show_script_dialog = fail
    assert m["main"]() is None
    assert errors[0][-1] == "host timed out"


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("failure", ("none", "begin", "draw"))
def test_svg_non_square_size_viewbox_and_painter_cleanup(
    app: dict[str, Any], qt: Any, title: str, failure: str
) -> None:
    log = []

    class Bounds:
        x, y, width, height = 40, 20, 120, 680

        def adjusted(self, *args: float) -> Any:
            log.append(("padding", args))
            return self

    path = NS(boundingRect=lambda: Bounds())

    class Buffer:
        def open(self, mode: Any) -> bool:
            return True

        def data(self) -> Any:
            return NS(data=lambda: b'<svg xmlns="http://www.w3.org/2000/svg"></svg>')

        def close(self) -> None:
            log.append("close")

    class Generator:
        def setOutputDevice(self, value: Any) -> None:
            pass

        def setSize(self, value: Any) -> None:
            log.append(("size", value))

        def setViewBox(self, value: Any) -> None:
            log.append(("viewBox", (value.x, value.y, value.width, value.height)))

        def setTitle(self, value: str) -> None:
            pass

        def setDescription(self, value: str) -> None:
            pass

    class Painter:
        def begin(self, value: Any) -> bool:
            return failure != "begin"

        def setPen(self, value: Any) -> None:
            pass

        def setBrush(self, value: Any) -> None:
            pass

        def drawPath(self, value: Any) -> None:
            assert vars(value.boundingRect()) == {
                "x": 40,
                "y": -700,
                "width": 120,
                "height": 680,
            }
            if failure == "draw":
                raise RuntimeError("injected paint failure")
            log.append("draw")

        def end(self) -> None:
            log.append("end")

    qt.QtSvg = NS(QSvgGenerator=Generator)
    qt.QtCore.QBuffer = Buffer
    qt.QtCore.QIODevice = NS(OpenMode=int, WriteOnly=1)
    qt.QtCore.QSize = lambda *args: args
    qt.QtGui.QPainter = Painter
    function = load(title)["svg_text"]
    if failure == "none":
        assert "<svg" in function(qt, path, "A / Regular", (0, -200, 300, 1000))
    else:
        with pytest.raises(RuntimeError, match="SVG drawing failed"):
            function(qt, path, "A / Regular", (0, -200, 300, 1000))
    assert log[-2:] == ["end", "close"], "Always end painter before closing its device"
    assert ("size", (300, 1000)) in log
    assert ("viewBox", (0, -800, 300, 1000)) in log


@pytest.mark.parametrize("title", TITLES)
def test_missing_svg_module_has_clear_refusal(
    app: dict[str, Any], qt: Any, title: str
) -> None:
    with pytest.raises(ValueError, match="QSvgGenerator"):
        load(title)["svg_text"](qt, object(), "A", (0, -200, 300, 1000))


SOURCE_IDENTITIES = (
    (
        "rescued/part2/ports/effects/pyqt-official/lighting-b823a76f79197d84.py",
        "a456bfc064bdbce5e773cda8bee36e3d714caced7175b6edb7473ad1df32b5a6",
    ),
    (
        "rescued/part2/ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py",
        "e50504501e5e1fc30a379750eca8f2974677fe37331a04ede54e2a857ee3f7ec",
    ),
    (
        "rescued/part2/ports/animation/pyqt-official/appchooser-de30d23621025fe6.py",
        "42248cab1676b4e4a1539df8af1ed10a26fbd193ebd4d327f9832b6d1dd609ae",
    ),
    (
        "rescued/part2/ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py",
        "1ac9db7d122e92313f1e386190eb2c54ad9da2686820a81397759e9e3e1164ec",
    ),
    (
        "rescued/part2/ports/animation/pyqt-official/easing-bd6c8feb783ba845.py",
        "d125a1afb91be58a87606d0e2d5ced5cdea2d06618eb9734d1f5245e4604ed10",
    ),
    (
        "rescued/part2/ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py",
        "b57501fe1276a4b4a7af18ed12c5bcf87e3da67b7cf92f27117d307ce8facaee",
    ),
    (
        "rescued/part2/ports/animation/pyqt-official/stickman-243ae486f9528e8c.py",
        "08dba971d70b27e0cce4e62dc52e35b2d6dce185b3456948859acb802f44aed4",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py",
        "5c65be4bdb28b434c36f778ca8d296baf09521c45b76bcc6fa527b7a25ff6490",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/animation/pyqt-official/appchooser-de30d23621025fe6.py",
        "49cd103c29c9725e74ebff89fa30fa3e24502056577f625bf448cdf14c4f7c8c",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py",
        "ae79ea27f4bb5bb28912a0d9c5ceb8524f3f1c09ca7161bd408bc0e6ca88efb3",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/transformations-c12a2071adbab88b.py",
        "533857ee814a9428e094f1ad7dc9c13b4dbe8476c991effaced2f8486bec5abc",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py",
        "94c7a27d22a78955265a73c0d98383088c334d50d100eb330b242b84fbee0bab",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/animation/pyqt-official/easing-bd6c8feb783ba845.py",
        "085f44636bcc65544209dddd56c17fd8f76714e274804c73df8e72b0b1b69e47",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/animation/pyqt-official/stickman-243ae486f9528e8c.py",
        "9684cefbfa0d7512e5101140a4fa113a40e948489021c2075898577cba810d44",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/effects/pyqt-official/lighting-b823a76f79197d84.py",
        "e6c214da486d995c252a53d7f6f7d7cd51c9623296127905201eded6a24cf48d",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py",
        "85add73f044870978af99c4693ae4f0accc5ef89e4e183ac0da97171ec840f26",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py",
        "e644d0b42d3821a7f4895d50e038ebca61313fb3ff29339289680dabbc2cd5a0",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py",
        "5c65be4bdb28b434c36f778ca8d296baf09521c45b76bcc6fa527b7a25ff6490",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py",
        "5c65be4bdb28b434c36f778ca8d296baf09521c45b76bcc6fa527b7a25ff6490",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py",
        "61ca929ec547aabaa46105db6886b56880fd95d6fbc4626f0f7acd173f08c642",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py",
        "03bb3127f4dfabc413625896f964436dd592f878d9fb483c37615582f6a1068a",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py",
        "b6e3c4a0a1f6d66b75ce086fc2bfce13c5a72c498a71d960fc29a9e56fb2d8dd",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py",
        "d2ccb421fa24dcc962e4abda1d081a7b5a0a4615a4aef6e1a4d2c8e4490c7665",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py",
        "5c65be4bdb28b434c36f778ca8d296baf09521c45b76bcc6fa527b7a25ff6490",
    ),
    (
        "rescued/part3/pyqt-official-ports/ports/opengl/pyqt-official/grabber-303ea3ee09c4677d.py",
        "5c65be4bdb28b434c36f778ca8d296baf09521c45b76bcc6fa527b7a25ff6490",
    ),
    (
        "rescued/part2/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py",
        "5e88ce4d8959a0e13df6478a7811d6f69bbaa217ecef4728bb1f3bcfd2a28105",
    ),
    (
        "rescued/part2/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py",
        "ee842206b60ab167e4f45919a779a784e7154c2d201f1fad86b389d6436575b8",
    ),
    (
        "rescued/part2/ports/painting/pyqt-official/transformations-c12a2071adbab88b.py",
        "af4e3e14274a354fcc26514a063d8d9ba38d6f5930cf272fc4cb28543be1ebcc",
    ),
    (
        "rescued/part2/ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py",
        "f6d04cce9f39c1d796a987e2b3d5c1b24ca3ed5cba5c5d18b79a1909e47cd854",
    ),
    (
        "rescued/part2/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py",
        "daa00fe5bed6797d682cb3b219d56fc73d8a0ec8b094144281efa69939008db7",
    ),
    (
        "rescued/part2/ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py",
        "6d2f8e76efde17106dd50a3c6823b20a8053823bd1629a297654ed6eaed02f98",
    ),
)


@pytest.mark.parametrize("source,digest", SOURCE_IDENTITIES)
def test_each_source_identity_is_preserved_not_executed(
    source: str, digest: str
) -> None:
    """Bind dispositions to all 31 exact source bodies without importing them."""
    index = json.loads((ROOT / "rescue-index.json").read_text())
    found = [row for row in index["menus"] if row["target"] == source]
    assert len(found) == 1 and found[0]["target_sha256"] == digest
    archive = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
    assert hashlib.sha256((archive / source).read_bytes()).hexdigest() == digest


def test_source_inventory_covers_exact_batch() -> None:
    names = [
        "basicdrawing",
        "concentriccircles",
        "painterpaths",
        "svgviewer",
        "transformations",
        "lighting",
        "animatedtiles",
        "appchooser",
        "easing",
        "moveblocks",
        "states",
        "stickman",
        "2dpainting",
        "grabber",
        "hellogl",
        "openglwindow",
        "overpainting",
        "textures",
    ]
    index = json.loads((ROOT / "rescue-index.json").read_text())
    found = {
        row["target"]
        for row in index["menus"]
        if any(re.search("/" + name + "[-/.]", row["target"]) for name in names)
    }
    assert len(found) == 31 and found == {source for source, _ in SOURCE_IDENTITIES}


REFERENCE = "Glyph SVG Reference"


def test_reference_alignment_is_centered_uniform_and_finite() -> None:
    align = load(REFERENCE)["alignment_matrix"]
    assert align((10, 20, 100, 200), (0, -700, 500, 700)) == (3.5, 0, 0, 3.5, 40, -770)
    for bad in ((0, 0, 0, 2), (0, 0, 2, -1), (math.nan, 0, 2, 2)):
        with pytest.raises(ValueError):
            align(bad, (0, 0, 2, 2))


def test_reference_refuses_missing_relative_and_non_svg_files(tmp_path: Path) -> None:
    check = load(REFERENCE)["reference_file"]
    for name in (
        "relative.svg",
        str(tmp_path / "none.svg"),
        str(tmp_path / "wrong.txt"),
    ):
        with pytest.raises(ValueError):
            check(name)
    source = tmp_path / "art.svg"
    payload = (
        b'<svg xmlns="http://www.w3.org/2000/svg"><defs/><path d="M0 0L1 1"/></svg>'
    )
    source.write_bytes(payload)
    assert check(str(source)) == source
    assert source.read_bytes() == payload


@pytest.mark.parametrize(
    "condition", ("valid", "invalid", "animated", "zero-bounds", "missing-module")
)
def test_vector_reference_compares_current_outline_and_clears_failures(
    app: dict[str, Any], qt: Any, tmp_path: Path, condition: str
) -> None:
    """Keep the exact source file intact; only scene item transforms may change."""
    m = load(REFERENCE)
    source = tmp_path / "reference.svg"
    payload = b'<svg xmlns="http://www.w3.org/2000/svg"><defs/><g/></svg>'
    source.write_bytes(payload)
    rect = NS(x=0.0, y=0.0, width=500.0, height=700.0)
    path = NS(boundingRect=lambda: rect)
    m["panel_type"].__globals__["capture_outline"] = lambda: ("A / Regular", path)

    class Item:
        def __init__(self, filename: str) -> None:
            assert filename == str(source)

        def renderer(self) -> Any:
            return NS(
                isValid=lambda: condition != "invalid",
                animated=lambda: condition == "animated",
                setAspectRatioMode=lambda mode: None,
                viewBoxF=lambda: NS(x=0, y=-700, width=500, height=700),
            )

        def boundingRect(self) -> Any:
            return NS(
                x=0.0,
                y=0.0,
                width=0.0 if condition == "zero-bounds" else 500.0,
                height=700.0,
            )

        def setTransform(self, value: Any) -> None:
            self.matrix = value.coefficients

        def setOpacity(self, value: float) -> None:
            self.opacity = value

        def setZValue(self, value: float) -> None:
            pass

    class Scene(Widget):
        def addItem(self, item: Any) -> None:
            self.items.append(item)

        def addPath(self, *args: Any) -> Any:
            self.items.append(args)
            return NS(setZValue=lambda value: None)

    qt.QtGui.QGraphicsScene = Scene
    qt.QtGui.QPen = lambda *args: NS(setCosmetic=lambda value: None)
    qt.QtCore.Qt.NoBrush = 8
    if condition != "missing-module":
        qt.QtSvg = NS(QGraphicsSvgItem=Item)
    panel = m["panel_type"](qt)(None)
    panel.source_entry.text = str(source)
    panel.compare()
    assert source.read_bytes() == payload, "SVG payload must never be rewritten"
    if condition == "valid":
        assert len(panel.canvas.items) == 2
        assert panel.canvas.items[0].opacity == 0.35
        assert panel.canvas.items[0].matrix == (1, 0, 0, 1, 0, -700)
        assert "normalized display scale" in panel.message.text
        item = panel.reference_item
        m["panel_type"].__globals__["capture_outline"] = lambda: pytest.fail(
            "Live controls must not reread the glyph"
        )
        panel.opacity_control.setValue(0.7)
        assert item.opacity == 0.7 and panel.reference_item is item
        panel.mode_choice.setCurrentIndex(1)
        assert item.matrix == (1, 0, 0, 1, 0, -700)
        assert "SVG user unit = font unit" in panel.message.text
    else:
        assert not panel.canvas.items, (
            "Failure must clear all partly created native items"
        )
        assert "snapshot" not in panel.message.text
    panel.closeEvent(Event())
    assert panel.deleted and panel.scope.dead and not panel.canvas.items


@pytest.mark.parametrize(
    "ink,metrics,expected",
    [
        ((40, 20, 120, 680), (300, -200, 800), (0, -200, 300, 1000)),
        ((-30.5, -250.5, 400, 1151.25), (300, -200, 800), (-31, -251, 401, 1152)),
    ],
)
def test_font_frame_keeps_origin_metrics_and_ink(
    app: dict[str, Any], ink: tuple, metrics: tuple, expected: tuple
) -> None:
    rect = NS(**dict(zip(("x", "y", "width", "height"), ink, strict=True)))
    assert (
        load("Glyph Outline SVG")["font_frame"](NS(boundingRect=lambda: rect), metrics)
        == expected
    )


def test_reference_font_units_restores_svg_viewbox_coordinates() -> None:
    matrix = load(REFERENCE)["reference_matrix"]
    # Qt item is 100 x 200, while original SVG user coordinates start at (-10,-800).
    assert matrix(
        (0, 0, 100, 200), (-10, -800, 500, 1000), (0, -700, 500, 700), True
    ) == (5, 0, 0, 5, -10, -800)


def test_source_paths_are_header_comments_and_consolidation_is_complete() -> None:
    outline = (ROOT / "Scripts/Drawing/Glyph Outline SVG.py").read_text()
    assert not (ROOT / "Scripts/Drawing/Glyph Transform Proof.py").exists()
    for title in ("Glyph Outline SVG", REFERENCE):
        source = (ROOT / "Scripts/Drawing" / f"{title}.py").read_text()
        doc = ast.get_docstring(ast.parse(source))
        assert "Source:" not in doc and "SHA256:" not in doc
        assert "# preserved-source:" in source
    assert len(re.findall(r"^# preserved-source:", outline, re.MULTILINE)) == 6
    assert "FontLab artwork importer" not in outline and "artwork import" not in outline


@pytest.mark.parametrize(
    "metrics", [(300, 800, -200), (math.inf, -200, 800), (300, math.nan, 800)]
)
def test_frame_refuses_invalid_metrics(app: dict[str, Any], metrics: tuple) -> None:
    path = NS(boundingRect=lambda: NS(x=0, y=0, width=120, height=680))
    with pytest.raises(ValueError):
        load(TITLES[0])["font_frame"](path, metrics)


def test_font_metrics_are_rechecked_during_capture(app: dict[str, Any]) -> None:
    m = load(TITLES[0])
    package = NS(
        id=1, fgId=2, master="Regular", ascender_value=800, descender_value=-200
    )
    layer = NS(id=5, isNull=False, advanceWidth=300)
    glyph = NS(id=3, name="A", package=package, findLayer=lambda name: layer)
    app["scripting"].current_package = lambda *args: package
    app["node_coordinates"].current_glyph = lambda pkg: glyph
    app["inspectors"].outline_source = lambda item: ()

    def changing(item: Any) -> Any:
        package.ascender_value = 900
        return NS(isEmpty=lambda: False)

    app["inspectors"].outline = changing
    with pytest.raises(ValueError, match="changed"):
        m["capture_outline"]()


OPENGL_REASON = "The source needs QOpenGLContext.versionFunctions() and QOpenGLFunctions_* wrappers. FontLab PythonQt does not export them."


def integration_records() -> dict[str, list[dict[str, Any]]]:
    """Build complete source-bound records for the controller's shared manifest."""
    archive = Path(os.environ["FONTLAB_PRESERVED_ROOT"])
    indexed = {
        row["target"]: row
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    targets = {
        "painterpaths": "Glyph Outline SVG",
        "basicdrawing": "Glyph Outline SVG",
        "transformations": "Glyph Outline SVG",
        "svgviewer": REFERENCE,
    }
    reasons = {
        "concentriccircles": "Animated integer/float antialiasing circles provide no distinct glyph action or consumable font output.",
        "lighting": "Animated lighting and shadows provide no outline edit or font-workflow output.",
        "animatedtiles": "Animated raster-tile layouts provide no glyph action or persistent font-workflow output.",
        "appchooser": "Application-icon chooser animation provides no current-font action or font-workflow output.",
        "easing": "Time easing of a moving pixmap is not master or axis interpolation and produces no usable font data.",
        "moveblocks": "Looping block motion has no glyph-outline or master-interpolation result and exports no font input.",
        "states": "Animated pixmap states provide no glyph action or persistent font-workflow output.",
        "stickman": "Skeletal keyframe editing and ragdoll physics have no glyph-contour mapping or font export.",
    }
    result: dict[str, list[dict[str, Any]]] = {"adaptations": [], "retirements": []}
    for source, digest in SOURCE_IDENTITIES:
        original = indexed[source]
        assert (
            original["target_sha256"]
            == digest
            == hashlib.sha256((archive / source).read_bytes()).hexdigest()
        )
        family = Path(source).stem.rsplit("-", 1)[0]
        row = {
            "source_menu": original["menu"],
            "source": source,
            "source_sha256": digest,
            "license": "Apache-2.0",
        }
        if family not in targets:
            row.update(
                disposition="retired",
                reason=OPENGL_REASON if "/opengl/" in source else reasons[family],
            )
            result["retirements"].append(row)
            continue
        menu = "Scripts/Drawing/" + targets[family] + ".py"
        primary = "/part2/" in source and family in ("painterpaths", "svgviewer")
        scope = (
            "Current-master rendered outline, fill-rule comparison, origin/advance/ascender/descender/ink frame in font units, preview and SVG export for an external vector editor."
            if family != "svgviewer"
            else "Static vector SVG comparison with the current glyph; live opacity; normalized silhouette or original SVG user coordinates in font units; source file unchanged."
        )
        row.update(
            menu=menu,
            destination_sha256=hashlib.sha256((ROOT / menu).read_bytes()).hexdigest(),
            entry_point="main",
            family=family,
            disposition="ported" if primary else "duplicate-of",
            scope=scope,
            native_acceptance="pending",
            original_workflow_accepted=False,
        )
        result["adaptations"].append(row)
    return result


def test_fragment_records_are_complete_and_use_ruled_reasons() -> None:
    records = integration_records()
    assert len(records["adaptations"]) == 8 and len(records["retirements"]) == 23
    assert sum(row["disposition"] == "ported" for row in records["adaptations"]) == 2
    assert all(
        row["menu"] == "Scripts/Drawing/Glyph Outline SVG.py"
        for row in records["adaptations"]
        if row["family"] == "transformations"
    )
    for row in records["retirements"]:
        assert "archived" not in row["reason"].lower()
        if "/opengl/" in row["source"]:
            assert row["reason"] == OPENGL_REASON
