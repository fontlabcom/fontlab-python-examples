# this_file: tests/test_native_attributes.py
"""Measured native PythonQt field restrictions and owned-control regression."""

import insight_doubles
import pytest
import test_second_batch

insight_qt = insight_doubles.insight_qt
batch_qt = test_second_batch.batch_qt


@pytest.mark.parametrize("name", ["QWidget", "QTableView", "QMainWindow"])
def test_native_widget_when_given_python_controls_then_rejected(name, insight_qt):
    native = getattr(insight_qt.QtGui, name)()
    with pytest.raises(AttributeError, match="controls"):
        native.controls = {}
    native.text = "Existing Qt property"
    assert native.text == "Existing Qt property"

    class PythonWidget(type(native)):
        pass

    subclass = PythonWidget()
    subclass.controls = {}
    assert subclass.controls == {}, "Python subclasses may retain Python state"


def test_owned_builder_when_native_widget_then_controls_live_only_on_handle(insight_qt):
    from fontlab_python_examples.insights import owned

    window = insight_qt.QtGui.QWidget()
    with owned(window, "Regression") as handle:
        handle.controls["label"] = insight_qt.QtGui.QLabel("Owned", window)
        assert "controls" not in window.__dict__, (
            "Never attach state to native wrappers"
        )
    handle.close()
    assert not handle.controls, "Release child references before deletion"


@pytest.mark.parametrize(
    "kind",
    ["timer", "list-model", "table-model", "settings", "path", "scene", "object"],
)
def test_native_object_when_given_python_state_then_rejected(kind, insight_qt):
    qt = insight_qt
    window = qt.QtGui.QWidget()
    factories = {
        "timer": lambda: qt.QtCore.QTimer(window),
        "list-model": lambda: qt.QtGui.QStringListModel([], window),
        "table-model": lambda: qt.QtGui.QAbstractTableModel(window),
        "settings": lambda: qt.QtCore.QSettings(
            "FontLabPythonExamples", "InsightsSandbox", window
        ),
        "path": qt.QtGui.QPainterPath,
        "scene": lambda: qt.QtGui.QGraphicsScene(window),
        "object": lambda: qt.private.QObject(window),
    }
    native = factories[kind]()
    with pytest.raises(AttributeError, match="python_state"):
        native.python_state = {}
