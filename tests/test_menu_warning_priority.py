# this_file: tests/test_menu_warning_priority.py
"""Actual menu error routes retain the host parent and shared warning policy."""
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace as NS

import pytest

ROOT = Path(__file__).resolve().parents[1]
MENUS = (
    "Drawing/Glyph Outline SVG.py",
    "Drawing/Glyph SVG Reference.py",
    "Windows/Glyph Snapshot Diff.py",
    "Windows/Unicode Issues Dock.py",
)


@pytest.mark.parametrize("relative", MENUS)
def test_warning_when_setup_fails_then_uses_owned_priority_helper(monkeypatch, relative):
    calls = []
    parent = object()
    qt = NS(QtGui=NS(QMessageBox=NS(Ok=1024, warning=lambda *args: None)))
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    fly.qt, fly.fl, fly.ap = qt, NS(MainWindow=lambda: parent), ap
    helpers = ModuleType("fly.ap.qt_dialogs")
    helpers.run_standard_message_box = lambda *args: calls.append(args)
    scripting = ModuleType("fly.ap.scripting")

    def fail(*args):
        raise TimeoutError("setup expired")

    scripting.show_script_dialog = fail
    ap.qt_dialogs, ap.scripting = helpers, scripting
    for name, value in (("fly", fly), ("fly.ap", ap),
                        ("fly.ap.qt_dialogs", helpers), ("fly.ap.scripting", scripting)):
        monkeypatch.setitem(sys.modules, name, value)
    menu = runpy.run_path(str(ROOT / "Scripts" / relative))
    menu["main"].__globals__.update(show=fail, panel_type=lambda qt: object)
    assert menu["main"]() is None, "Setup refusal must not escape after the warning"
    assert calls == [(qt, parent, menu["TITLE"], "setup expired", "Warning", 1024)], "Keep the native host parent, title, body and standard Ok button"


@pytest.mark.parametrize("relative", MENUS)
def test_actual_warning_when_setup_fails_then_modal_owner_is_preserved(monkeypatch, relative):
    import os
    binding = "PyQt5" if os.environ.get("FONTLABAPP_TEST_QT5") == "1" else "PySide6"
    C = pytest.importorskip(binding + ".QtCore")
    G = pytest.importorskip(binding + ".QtWidgets")
    import fontlabapp.qt_dialogs as real

    app = G.QApplication.instance() or G.QApplication([])
    parent = G.QWidget()
    fly, ap = ModuleType("fly"), ModuleType("fly.ap")
    fly.__path__, ap.__path__ = [], []
    qt = NS(QtCore=C, QtGui=G)
    fly.qt, fly.fl, fly.ap = qt, NS(MainWindow=lambda: parent), ap
    scripting = ModuleType("fly.ap.scripting")

    def fail(*args):
        raise TimeoutError("actual warning")

    scripting.show_script_dialog = fail
    ap.qt_dialogs, ap.scripting = real, scripting
    for name, value in (("fly", fly), ("fly.ap", ap),
                        ("fly.ap.qt_dialogs", real), ("fly.ap.scripting", scripting)):
        monkeypatch.setitem(sys.modules, name, value)
    menu = runpy.run_path(str(ROOT / "Scripts" / relative))
    menu["main"].__globals__.update(show=fail, panel_type=lambda qt: object)
    reference = G.QMessageBox(parent)
    reference.setWindowTitle(menu["TITLE"])
    expected_title = reference.windowTitle()  # Qt on macOS ignores message-box titles.
    reference.deleteLater()
    app.sendPostedEvents(None, C.QEvent.DeferredDelete)
    observed = []
    timer = C.QTimer()
    timer.setSingleShot(True)

    def accept():
        box = parent.findChild(G.QMessageBox)
        if box is not None:
            observed.append((box.parentWidget() is parent, box.windowTitle(), box.text(),
                             box.icon(), bool(box.windowFlags() & C.Qt.WindowStaysOnTopHint), box.isModal()))
            box.button(G.QMessageBox.Ok).click()

    watchdog = C.QTimer()
    watchdog.setSingleShot(True)

    def abort():
        box = app.activeModalWidget()
        if isinstance(box, G.QMessageBox):
            observed.append("deadline")
            box.reject()

    watchdog.timeout.connect(abort)
    watchdog.start(1500)
    timer.timeout.connect(accept)
    timer.start(0)
    try:
        assert menu["main"]() is None
        assert observed == [(True, expected_title, "actual warning", G.QMessageBox.Warning, True, True)], "Actual modal warning keeps host parent, priority and text"
    finally:
        timer.stop()
        watchdog.stop()
        timer.timeout.disconnect(accept)
        watchdog.timeout.disconnect(abort)
        parent.close()
        parent.deleteLater()
        app.sendPostedEvents(None, C.QEvent.DeferredDelete)
