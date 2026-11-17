# this_file: tests/test_task6c_drawing_insights.py
# SPDX-License-Identifier: Apache-2.0
"""Render menu canvases and exercise their input and worker callbacks offscreen."""

from pathlib import Path
from threading import enumerate as active_threads
from types import SimpleNamespace

import pytest

from module_doubles import install_module
from test_drawing_examples import DRAWING_TITLES, load
from test_restored_insights import qt

ROOT = Path(__file__).resolve().parents[1]


def launch_canvas(monkeypatch, qt, module):
    """Replace only the FontLab ownership boundary; construct the actual canvas."""
    def show(panel, key):
        assert key.startswith("drawing_")
        return panel(None)

    install_module(monkeypatch, "PythonQt", qt)
    install_module(monkeypatch, "fly.ap.core.scripting", SimpleNamespace(show_script_dialog=show))
    return module.main()


def rendered(qt, widget):
    image = qt.QtGui.QImage(widget.size(), qt.QtGui.QImage.Format_ARGB32)
    image.fill(qt.QtGui.QColor("magenta"))
    widget.render(image)
    return image


@pytest.mark.parametrize("title", [t for t in DRAWING_TITLES if t != "Image PNG Export"])
def test_canvas_menu_renders_coloured_geometry(qt, monkeypatch, title, capsys):
    module = load(ROOT / f"Scripts/Drawing/{title}.py")
    canvas = launch_canvas(monkeypatch, qt, module)
    try:
        if title == "Animated Orbit":
            canvas.timerEvent(qt.QtCore.QTimerEvent(canvas.orbit_timer_id))
        if title == "Mouse Stroke Canvas":
            from PySide6.QtTest import QTest
            QTest.mousePress(canvas, qt.QtCore.Qt.LeftButton, pos=qt.QtCore.QPoint(40, 40))
            QTest.mouseMove(canvas, qt.QtCore.QPoint(180, 130))
            QTest.mouseRelease(canvas, qt.QtCore.Qt.LeftButton)
            assert canvas.stroke_path.elementCount() >= 2
            assert not canvas.drawing_stroke
        image = rendered(qt, canvas)
        colours = {image.pixelColor(x, y).name() for x in range(10, 490, 10)
                   for y in range(10, 340, 10)}
        assert len(colours) > 1, title
        assert "#ff00ff" not in colours, "canvas must paint the entire background"
        assert not capsys.readouterr().out, "paint callbacks must finish without contained errors"
    finally:
        canvas.close()


def test_mouse_canvas_clears_and_contains_bad_input(qt, monkeypatch, capsys):
    from PySide6.QtTest import QTest
    module = load(ROOT / "Scripts/Drawing/Mouse Stroke Canvas.py")
    canvas = launch_canvas(monkeypatch, qt, module)
    try:
        canvas.mouseMoveEvent(SimpleNamespace())
        QTest.mousePress(canvas, qt.QtCore.Qt.LeftButton, pos=qt.QtCore.QPoint(30, 30))
        canvas.mouseMoveEvent(SimpleNamespace(pos=lambda: qt.QtCore.QPoint(160, 160)))
        assert rendered(qt, canvas).pixelColor(90, 90).name() == "#235e96"
        QTest.mouseClick(canvas, qt.QtCore.Qt.RightButton)
        assert canvas.stroke_path.isEmpty()
        assert rendered(qt, canvas).pixelColor(90, 90).name() == "#ffffff"
        QTest.mouseClick(canvas, qt.QtCore.Qt.MiddleButton)
        canvas.mousePressEvent(SimpleNamespace())
        assert "Mouse Stroke Canvas:" in capsys.readouterr().out
        canvas.drawing_stroke = True
        canvas.mouseMoveEvent(SimpleNamespace())
        assert not canvas.drawing_stroke
        assert "Mouse Stroke Canvas:" in capsys.readouterr().out
    finally:
        canvas.close()


def test_orbit_stops_timer_on_callback_failure(qt, monkeypatch, capsys):
    module = load(ROOT / "Scripts/Drawing/Animated Orbit.py")
    canvas = launch_canvas(monkeypatch, qt, module)
    try:
        def fail():
            raise RuntimeError("surface deleted")
        monkeypatch.setattr(canvas, "update", fail)
        canvas.timerEvent(None)
        assert canvas.orbit_timer_id == 0
        assert "surface deleted" in capsys.readouterr().out
    finally:
        canvas.close()


def test_png_menu_saves_real_image_and_displays_its_path(qt, monkeypatch, tmp_path):
    module = load(ROOT / "Scripts/Drawing/Image PNG Export.py")
    monkeypatch.setattr(module.tempfile, "tempdir", str(tmp_path))
    canvas = launch_canvas(monkeypatch, qt, module)
    try:
        paths = list(tmp_path.glob("*.png"))
        assert len(paths) == 1
        image = qt.QtGui.QImage(str(paths[0]))
        assert image.size() == qt.QtCore.QSize(440, 240)
        assert image.pixelColor(10, 10) != image.pixelColor(430, 230)
        labels = canvas.findChildren(qt.QtGui.QLabel)
        assert any(label.text() == str(paths[0]) for label in labels)
        assert any(not label.pixmap().isNull() for label in labels)
    finally:
        canvas.close()


@pytest.mark.parametrize("title", ["Glyph Properties", "Signal Lifetime"])
def test_insight_menu_callbacks_update_visible_state(qt, monkeypatch, title):
    module = load(ROOT / f"Scripts/Insights/{title}.py")
    monkeypatch.setattr(module.S, "launch", lambda build, *args: build(qt))
    handle = module.main()
    try:
        button = handle.controls["button"]
        button.click()
        if title == "Glyph Properties":
            assert handle.snapshot()["glyph_role"] == "alternate"
            button.click()
            assert handle.snapshot()["text"] == "A: default"
        else:
            button.click()
            assert handle.snapshot()["advance"] == 620
            assert handle.snapshot()["clicks"] == 2
            assert handle.controls["label"].text() == "Advance: 620"
    finally:
        handle.close()


def test_worker_delivers_completion_error_and_cancellation(qt, monkeypatch):
    module = load(ROOT / "Scripts/Insights/Worker Glyph Queue.py")
    monkeypatch.setattr(module.S, "launch", lambda build, *args: build(qt))
    handle = module.main()
    try:
        handle.controls["timer"].timeout.emit()
        handle.controls["start"].click()
        handle.controls["start"].click()
        assert handle.snapshot()["phase"] == "running"
        # Join the finite real producer, then deliver through the actual timer signal.
        for thread in active_threads():
            if thread.name == "insight-glyph-audit":
                thread.join(1)
        handle.controls["timer"].timeout.emit()
        assert handle.snapshot()["phase"] == "done"
        assert [r["glyph"] for r in handle.snapshot()["results"]] == list(module.NAMES)
        assert "space: 524" in handle.controls["log"].toPlainText()
        monkeypatch.setattr(module, "NAMES", [None])
        handle.controls["start"].click()
        for thread in active_threads():
            if thread.name == "insight-glyph-audit":
                thread.join(1)
        handle.controls["timer"].timeout.emit()
        assert handle.snapshot()["phase"] == "error"
        assert handle.snapshot()["error"]
        handle.controls["start"].click()
        handle.controls["stop"].click()
        assert handle.snapshot()["phase"] == "stopped"
        assert not handle.snapshot()["worker_alive"]
    finally:
        handle.close()


def test_word_form_inspection_and_entrypoint(qt, monkeypatch):
    module = load(ROOT / "Scripts/UI Loading/Load Word Form With Actions.py")
    monkeypatch.setattr(module.S, "launch", lambda build, *args: build(qt))
    handle = module.main()
    handle.controls["Add"].click()
    assert handle.snapshot()["count"] == 4
    handle.controls["Clear"].click()
    assert handle.snapshot()["count"] == 0
    handle.controls["OK"].click()
    assert handle.owner.closed
