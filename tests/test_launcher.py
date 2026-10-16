# this_file: tests/test_launcher.py
"""Launcher boundary tests with doubles, never native acceptance evidence."""

import importlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fontlab_python_examples as examples


def test_catalog_when_imported_without_host_then_names_and_source_mapping():
    records = examples.available()
    assert {entry["name"] for entry in records} >= {
        "QLabel",
        "QVBoxLayout",
        "Signals and Slots",
        "Qt Designer",
    }
    assert examples.describe("QLabel")["source_id"] == "ce3e17a7a2a03a02"
    assert examples.describe("ce3e17a7a2a03a02") == examples.describe("QLabel")
    json.dumps(records)


def test_launch_when_unknown_or_unported_then_actionable_error():
    with pytest.raises(ValueError, match="Unknown example"):
        examples.launch("no such example")
    with pytest.raises(NotImplementedError, match="not ported"):
        examples.launch("src/15 PyQt database example/main.py")


def test_launch_when_no_host_then_requires_existing_fontlab(monkeypatch):
    monkeypatch.setitem(sys.modules, "PythonQt", None)
    with pytest.raises(RuntimeError, match="inside FontLab"):
        examples.launch("QLabel")


def test_launch_when_reimported_then_retained_owned_handle_and_idempotent_close(
    native_boundary,
):
    handle = examples.launch("QLabel")
    assert handle.widget.text == "Hello World!"
    assert examples.launch("ce3e17a7a2a03a02") is handle
    assert importlib.import_module("fontlab_python_examples").get("QLabel") is handle
    assert examples.inspect("QLabel")["visible"] is True
    json.dumps(examples.inspect("QLabel"))
    unrelated = native_boundary[0].QtGui.QWidget()
    assert examples.close("QLabel")["closed"] is True
    assert examples.close("QLabel")["closed"] is True
    assert handle.widget is None
    assert unrelated.deleted is False


def test_layout_when_launched_then_top_bottom_vertical_order(native_boundary):
    handle = examples.launch("QVBoxLayout")
    assert [widget.text for widget in handle.widget.layout.widgets] == ["Top", "Bottom"]
    assert examples.inspect("QVBoxLayout")["buttons"] == ["Top", "Bottom"]
    handle.widget.layout.widgets[0].setText("Changed")
    assert examples.inspect("QVBoxLayout")["buttons"] == ["Changed", "Bottom"]


def test_signals_when_clicked_then_real_callback_builds_owned_async_alert(
    native_boundary,
):
    handle = examples.launch("Signals and Slots")
    handle.widget.clicked.emit()
    alert = handle.alerts[-1]
    assert alert.widget.text == "You clicked the button!"
    assert alert.widget.parent is handle.widget
    assert alert.widget.opened is True
    assert alert.widget.modality == native_boundary[0].QtCore.Qt.WindowModal
    assert examples.inspect("Signals and Slots")["alert_texts"] == [
        "You clicked the button!"
    ]
    alert_widget = alert.widget
    examples.close("Signals and Slots")
    assert alert_widget.deleted is True
    assert handle.callbacks == []


def test_designer_when_loaded_from_other_cwd_then_portable_ui_and_cleanup(
    native_boundary, monkeypatch, tmp_path
):
    monkeypatch.chdir(tmp_path)
    handle = examples.launch("Qt Designer")
    assert handle.widget.loaded_path.endswith("dialog-0bf07d6f0c55bc7e.ui")
    assert handle.widget.modal is False
    assert examples.inspect("Qt Designer")["result"] == 0
    assert all(obj.deleted for obj in native_boundary[0].temporary_objects)


def test_launch_when_show_fails_then_created_widget_is_closed(native_boundary):
    native_boundary[0].fail_show = True
    with pytest.raises(RuntimeError, match="show failed"):
        examples.launch("QLabel")
    assert native_boundary[1][-1].closed is True
    assert examples.inspect("QLabel")["launched"] is False


def test_handle_when_native_destroyed_then_snapshot_avoids_dead_wrapper(
    native_boundary,
):
    handle = examples.launch("QLabel")
    handle.owner.close()
    assert examples.inspect("QLabel")["closed"] is True
    assert handle.widget is None
    examples.close("QLabel")


def test_launch_when_no_existing_app_then_no_new_qapplication(native_boundary):
    native_boundary[0].QtGui.QApplication.instance = lambda: None
    with pytest.raises(RuntimeError, match="existing QApplication"):
        examples.launch("QLabel")


def test_port_when_executed_as_script_then_uses_named_retained_launcher(
    native_boundary,
):
    import runpy

    root = Path(__file__).resolve().parents[1]
    runpy.run_path(
        str(root / examples.describe("QLabel")["target_path"]), run_name="__main__"
    )
    assert examples.get("QLabel").widget.text == "Hello World!"


def test_alert_when_dismissed_and_clicked_again_then_previous_owned_dialog_removed(
    native_boundary,
):
    handle = examples.launch("Signals and Slots")
    handle.widget.clicked.emit()
    previous = handle.alerts[-1].widget
    previous.visible = False
    assert examples.inspect("Signals and Slots")["alert_texts"] == []
    handle.widget.clicked.emit()
    assert previous.deleted is True
    assert len(handle.alerts) == 1


def test_get_when_never_launched_then_explicit_launch_guidance():
    with pytest.raises(RuntimeError, match="call launch"):
        examples.get("QLabel")


@pytest.mark.parametrize("failure", ["open", "load"])
def test_designer_when_io_or_loader_fails_then_temporaries_destroyed(
    native_boundary, monkeypatch, failure
):
    qt, _ = native_boundary
    if failure == "open":
        monkeypatch.setattr(qt.QtCore.QFile, "open", lambda *args: False)
        monkeypatch.setattr(
            qt.QtCore.QFile, "errorString", lambda self: "missing", raising=False
        )
        error, message = OSError, "Cannot open Designer UI"
    else:
        monkeypatch.setattr(qt.QtUiTools.QUiLoader, "load", lambda *args: None)
        monkeypatch.setattr(
            qt.QtUiTools.QUiLoader, "errorString", lambda self: "bad XML", raising=False
        )
        error, message = RuntimeError, "Cannot load Designer UI"
    with pytest.raises(error, match=message):
        examples.launch("Qt Designer")
    assert all(obj.deleted for obj in qt.temporary_objects)


def test_alert_when_open_fails_then_owned_dialog_closed(native_boundary, monkeypatch):
    qt, _ = native_boundary

    def fail(self):
        raise RuntimeError("alert open failed")

    monkeypatch.setattr(qt.QtGui.QMessageBox, "open", fail)
    handle = examples.launch("Signals and Slots")
    with pytest.raises(RuntimeError, match="alert open failed"):
        handle.widget.clicked.emit()
    assert handle.alerts[-1].closed is True
