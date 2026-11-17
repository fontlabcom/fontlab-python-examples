# this_file: tests/test_restored_insights.py
# SPDX-License-Identifier: Apache-2.0
"""Offscreen behaviour checks for the restored, synthetic Insights demos."""
import importlib.util
import sys
from pathlib import Path
from queue import Queue
from threading import Event
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = sorted((ROOT / "Scripts/Insights").glob("*.py"))


def load(path):
    spec = importlib.util.spec_from_file_location("restored_insight", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def qt(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "lessons/src"))
    from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools
    from fontlab_python_lessons import qt_demos as support

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    gui = SimpleNamespace(**{name: getattr(QtGui, name) for name in dir(QtGui)})
    for module in (QtWidgets,):
        for name in dir(module):
            if name.startswith("Q"):
                setattr(gui, name, getattr(module, name))
    gui.QStringListModel = QtCore.QStringListModel
    gui.QAbstractTableModel = QtCore.QAbstractTableModel

    class Owner:
        def __init__(self, widget, content):
            self.widget, self.closed = widget, False

        def close(self):
            self.widget.close()
            self.widget.deleteLater()
            self.closed = True
            return True

    def connect_old(handle, obj, signature, callback):
        handle.connect(getattr(obj, signature.split("(")[0]), callback)

    monkeypatch.setitem(sys.modules, "fly.ap.qt.widgets", SimpleNamespace(OwnedWidget=Owner))
    monkeypatch.setitem(sys.modules, "PythonQt", SimpleNamespace(QtUiTools=QtUiTools))
    monkeypatch.setattr(support.ExampleHandle, "connect_old", connect_old)
    yield SimpleNamespace(QtCore=QtCore, QtGui=gui, private=SimpleNamespace(QObject=QtCore.QObject), app=app)
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    app.processEvents()


@pytest.mark.parametrize("path", SCRIPTS, ids=lambda p: p.stem)
def test_insight_builds_and_closes_offscreen(qt, path):
    handle = load(path).build(qt)
    try:
        handle.widget.show()
        qt.app.processEvents()
        assert handle.snapshot()["launched"]
        assert not handle.owner.closed
    finally:
        handle.close()
    assert handle.owner.closed
    assert not handle.connections


def test_callback_errors_preserve_last_valid_advance(qt):
    handle = load(ROOT / "Scripts/Insights/Callback Errors.py").build(qt)
    try:
        editor, button = handle.controls["input"], handle.controls["apply"]
        for text in ("", "bad", "-1", "2001", "9999999999999999999999"):
            editor.setText(text)
            button.click()
            assert handle.snapshot()["advance"] == 600
            assert handle.snapshot()["error"]
        editor.setText("0")
        button.click()
        assert handle.snapshot()["advance"] == 0
        assert handle.snapshot()["error"] == ""
    finally:
        handle.close()


def test_glyph_list_filters_case_insensitively(qt):
    handle = load(ROOT / "Scripts/Insights/Glyph List.py").build(qt)
    try:
        handle.controls["filter"].setText("a")
        handle.controls["apply"].click()
        assert handle.snapshot()["glyph_names"] == ["A", "Aacute"]
        handle.controls["filter"].setText("no match")
        handle.controls["apply"].click()
        assert handle.snapshot()["glyph_names"] == []
    finally:
        handle.close()


def test_metrics_undo_redo_and_duplicate_apply(qt):
    handle = load(ROOT / "Scripts/Insights/Metrics Undo.py").build(qt)
    try:
        controls = handle.controls
        controls["advance"].setValue(750)
        controls["apply"].click()
        controls["apply"].click()
        assert handle.snapshot()["advance"] == 750
        assert handle.snapshot()["count"] == 1
        controls["undo"].click()
        assert handle.snapshot()["advance"] == 600
        controls["redo"].click()
        assert handle.snapshot()["advance"] == 750
    finally:
        handle.close()


def test_controls_mirror_without_recursion(qt):
    handle = load(ROOT / "Scripts/Insights/Metric Controls.py").build(qt)
    try:
        handle.controls["spin"].setValue(700)
        assert handle.snapshot()["slider"] == 700
        assert handle.snapshot()["updates"] == 1
        handle.controls["slider"].setValue(800)
        assert handle.snapshot()["spin"] == 800
        assert handle.snapshot()["updates"] == 2
    finally:
        handle.close()


def test_plugin_tokens_install_unload_and_reinstall(qt):
    handle = load(ROOT / "Scripts/Insights/Plugin Tokens.py").build(qt)
    try:
        controls = handle.controls
        controls["install"].click()
        controls["install"].click()
        assert len(handle.snapshot()["tokens"]) == 2
        controls["plugin_action"].trigger()
        assert handle.snapshot()["invocations"] == 1
        controls["unload"].click()
        assert handle.snapshot()["tokens"] == []
        controls["install"].click()
        controls["plugin_action"].trigger()
        assert handle.snapshot()["invocations"] == 2
    finally:
        handle.close()


def test_settings_are_isolated_and_removed_on_close(qt):
    handle = load(ROOT / "Scripts/Insights/Sandbox Settings.py").build(qt)
    path = Path(handle.snapshot()["settings_file"])
    try:
        handle.controls["input"].setText("Proof 123")
        handle.controls["save"].click()
        assert handle.snapshot()["saved"] == "Proof 123"
        assert path.exists()
        handle.controls["reset"].click()
        assert handle.snapshot()["saved"] == "Hamburgefontsiv"
    finally:
        handle.close()
    assert not path.exists()


def test_loaded_form_preserves_named_controls(qt):
    handle = load(ROOT / "Scripts/Insights/Loaded Glyph Form.py").build(qt)
    try:
        handle.controls["glyph_name"].setText("O")
        handle.controls["advance"].setValue(640)
        handle.controls["apply"].click()
        assert handle.snapshot()["result"] == "O: advance 640"
    finally:
        handle.close()


def test_worker_publishes_plain_data_and_honours_cancellation(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "lessons/src"))
    module = load(ROOT / "Scripts/Insights/Worker Glyph Queue.py")
    incoming, stop = Queue(maxsize=8), Event()
    module._produce(incoming, stop)
    messages = [incoming.get_nowait() for _ in range(incoming.qsize())]
    assert [item[1]["glyph"] for item in messages[:-1]] == list(module.NAMES)
    assert messages[0] == ("result", {"glyph": "A", "name_score": 65})
    assert messages[-1] == ("done", None)
    stop.set()
    module._produce(incoming, stop)
    assert incoming.empty()
