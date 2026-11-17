# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_drawing_examples.py
"""Small host-free checks for drawing entrypoints and resource cleanup."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
DRAWING_TITLES = (
    "Linear Gradient Swatches", "Radial Gradient Light", "Conical Gradient Wheel",
    "Pen Dash Gallery", "Stroke Join Gallery", "Bezier Construction",
    "Path Boolean Gallery", "Text Along A Curve", "Painter Transform Gallery",
    "Path Clipping", "Composition Gallery", "Hatch Pattern Gallery",
    "Antialiasing Comparison", "Painter Opacity Layers", "Path Fill Rules",
    "Path Stroke Outline", "Rounded Label Drawing", "Picture Recording",
    "Image PNG Export", "Mouse Stroke Canvas", "Animated Orbit",
)
PATHS = [ROOT / "Scripts/Drawing" / f"{title}.py" for title in DRAWING_TITLES]
PATHS.append(ROOT / "Scripts/Graphics/Graphics Scene Shapes.py")


def load(path):
    spec = importlib.util.spec_from_file_location("drawing_example", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("path", PATHS, ids=lambda path: path.stem)
def test_drawing_when_imported_outside_fontlab_then_entrypoint_available(path):
    module = load(path)
    assert callable(module.main)
    assert "What:" in module.__doc__
    assert "Setup:" in module.__doc__
    source = path.read_text()
    assert "# SPDX-License-Identifier: Apache-2.0" in source
    assert f"# this_file: {path.relative_to(ROOT)}" in source


def test_orbit_when_quarter_turn_then_at_ellipse_bottom():
    module = load(ROOT / "Scripts/Drawing/Animated Orbit.py")
    assert module.orbit_position(0.0) == pytest.approx((430.0, 175.0))
    assert module.orbit_position(1.0) == pytest.approx((250.0, 285.0))
    assert module.orbit_position(4.0) == pytest.approx(module.orbit_position(0.0))


def test_png_when_encoder_fails_then_partial_file_removed(tmp_path, monkeypatch):
    module = load(ROOT / "Scripts/Drawing/Image PNG Export.py")
    monkeypatch.setattr(module.tempfile, "tempdir", str(tmp_path))
    image = SimpleNamespace(save=lambda *args: False)
    with pytest.raises(OSError, match="could not save"):
        module.save_png(image)
    assert list(tmp_path.iterdir()) == []


def test_png_when_encoder_succeeds_then_return_existing_unique_path(tmp_path, monkeypatch):
    module = load(ROOT / "Scripts/Drawing/Image PNG Export.py")
    monkeypatch.setattr(module.tempfile, "tempdir", str(tmp_path))
    image = SimpleNamespace(save=lambda *args: True)
    first, second = module.save_png(image), module.save_png(image)
    assert first != second
    assert Path(first).parent == tmp_path
    assert Path(first).exists() and Path(second).exists()


@pytest.mark.parametrize("path", PATHS[:18], ids=lambda path: path.stem)
def test_paint_when_drawing_raises_then_painter_ended(path, monkeypatch, capsys):
    module = load(path)
    calls = []

    class Widget:
        pass

    class Painter:
        Antialiasing = 1

        def __init__(self, device):
            pass

        def fillRect(self, *args):
            pass

        def setRenderHint(self, *args):
            pass

        def setPen(self, *args):
            pass

        def end(self):
            calls.append("end")

    def fail(*args):
        raise RuntimeError("drawing failed")

    monkeypatch.setattr(module, "draw", fail)
    gui = SimpleNamespace(QWidget=Widget, QPainter=Painter, QColor=lambda value: value)
    core = SimpleNamespace(QRectF=lambda *args: args)
    panel = module.panel_type(core, gui)
    panel.paintEvent(object(), None)
    assert calls == ["end"]
    assert "drawing failed" in capsys.readouterr().out


@pytest.mark.parametrize("path", [p for p in PATHS if p.stem not in {"Image PNG Export", "Graphics Scene Shapes"}], ids=lambda path: path.stem)
def test_canvas_when_constructed_then_close_deletes_native_widget(path):
    attributes = {}

    class Widget:
        def __init__(self, *args):
            pass

        def setWindowTitle(self, title):
            pass

        def setAttribute(self, key, value):
            attributes[key] = value

        def setFixedSize(self, *args):
            pass

        def startTimer(self, interval):
            assert interval == 33
            return 17

    qt = SimpleNamespace(Window=1, WA_QuitOnClose=2, WA_DeleteOnClose=3)
    core = SimpleNamespace(Qt=qt)
    gui = SimpleNamespace(QWidget=Widget, QPainterPath=object)
    load(path).panel_type(core, gui)(None)
    assert attributes[qt.WA_DeleteOnClose] is True
    assert attributes[qt.WA_QuitOnClose] is False


def test_animation_when_closed_then_timer_stops_before_accept():
    module = load(ROOT / "Scripts/Drawing/Animated Orbit.py")
    calls = []
    owner = SimpleNamespace(orbit_timer_id=17, killTimer=lambda value: calls.append(value))
    event = SimpleNamespace(accept=lambda: calls.append("accepted"))
    panel = module.panel_type(None, SimpleNamespace(QWidget=object))
    panel.closeEvent(owner, event)
    assert owner.orbit_timer_id == 0
    assert calls == [17, "accepted"]
