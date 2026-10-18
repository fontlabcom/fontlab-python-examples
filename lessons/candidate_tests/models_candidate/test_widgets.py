# this_file: lessons/candidate_tests/models_candidate/test_widgets.py
"""Actual offscreen Qt widgets behind a PythonQt-shaped, host-free boundary.

PySide6 is used in this isolated test process only. Production imports PythonQt
through fly.qt and shares App's real NamesDialog/connection/close implementation.
These tests do not establish native FontLab acceptance.
"""

import importlib
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from types import SimpleNamespace as NS

import pytest
from PySide6 import QtCore, QtGui, QtUiTools, QtWidgets
from test_domain import Source

ROOT = Path(__file__).resolve().parents[2]
WORKSPACE = ROOT.parents[1]


class Properties:
    """Expose the PythonQt property shape while running actual Qt widgets."""

    def __getattribute__(self, name):
        value = super().__getattribute__(name)
        if name in {"palette", "font", "text", "value", "currentText"} and callable(value):
            return value()
        return value


@pytest.fixture(scope="session")
def application():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    yield app


@pytest.fixture
def host(monkeypatch, application):
    gui = NS(**{name: getattr(QtGui, name) for name in dir(QtGui) if name.startswith("Q")})
    for name in dir(QtWidgets):
        if name.startswith("Q"):
            value = getattr(QtWidgets, name)
            setattr(
                gui,
                name,
                type(name, (Properties, value), {})
                if isinstance(value, type) and issubclass(value, QtWidgets.QWidget)
                else value,
            )
    gui.QStringListModel = QtCore.QStringListModel
    gui.QAbstractTableModel = QtCore.QAbstractTableModel
    gui.QWidget = QtWidgets.QWidget

    class Loader(QtUiTools.QUiLoader):
        def createWidget(self, classname, parent=None, name=""):
            widget = getattr(gui, classname)(parent)
            widget.setObjectName(name)
            return widget

    qt = NS(QtCore=QtCore, QtGui=gui, QtUiTools=NS(QUiLoader=Loader))
    source = Source()
    source.calls = []
    source.select_glyphs = lambda names, **kw: source.calls.append((names, kw)) or names
    native = NS(MainWindow=lambda: None)
    parent_module = ModuleType("fontlabapp")
    parent_module.__path__ = [
        os.environ.get("EXAMPLES_APP_SOURCE", str(WORKSPACE / "fontlab-fontlabapp/src/fontlabapp"))
    ]
    parent_module._native = lambda name: qt if name == "PythonQt" else native
    monkeypatch.setitem(sys.modules, "fontlabapp", parent_module)
    for name in ("fontlabapp.scripting", "fontlabapp._names_dialog"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    scripting = importlib.import_module("fontlabapp.scripting")
    for name in (
        "current_package",
        "names_font_glyphs",
        "names_font_window_selection",
        "inspectors_api",
        "select_glyphs",
    ):
        monkeypatch.setattr(scripting, name, getattr(source, name))
    fly = ModuleType("fly")
    fly.__path__ = []
    fly.qt = qt
    ap = ModuleType("fly.ap")
    ap.__path__ = []
    ap.scripting = scripting
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", ap)
    monkeypatch.setitem(sys.modules, "fly.ap.scripting", scripting)
    for name in list(sys.modules):
        if name.startswith("fontlab_python_lessons.") and name.rsplit(".", 1)[-1] in {
            "_dialog",
            "panels",
            "form_dialog",
            "ui",
        }:
            monkeypatch.delitem(sys.modules, name)
    dialogs = []

    def make(name):
        from fontlab_python_lessons import launch

        dialog = launch(name)
        dialogs.append(dialog)
        return dialog

    yield NS(qt=qt, source=source, make=make, scripting=scripting, dialogs=dialogs)
    for dialog in dialogs:
        try:
            dialog.close()
        except RuntimeError:
            pass
    QtCore.QCoreApplication.sendPostedEvents(None, QtCore.QEvent.DeferredDelete)
    application.processEvents()
    for name in ("fontlabapp.scripting", "fontlabapp._names_dialog"):
        sys.modules.pop(name, None)


def test_name_filter_when_prefix_select_and_refresh_then_uses_real_ordered_names(host):
    dialog = host.make("glyph-name-filter")
    assert dialog.model.stringList() == host.source.names
    dialog.query.setText("a")
    dialog.filter_button.click()
    assert dialog.model.stringList() == ["A", "Aacute"]
    index = dialog.model.index(1, 0)
    dialog.view.selectionModel().select(index, QtCore.QItemSelectionModel.Select)
    dialog.select_button.click()
    assert host.source.calls == [(["Aacute"], {"package_id": 14})]
    host.source.names.append("a.new")
    dialog.filter_button.click()
    assert dialog.snapshot is None and not dialog.select_button.isEnabled()
    assert "Refresh" in dialog.status.text
    dialog.refresh_button.click()
    assert dialog.model.stringList() == ["A", "Aacute", "a.new"]


def test_filter_when_no_rows_selected_or_no_matches_then_no_selection_write(host):
    dialog = host.make("glyph-name-filter")
    dialog.select_button.click()
    assert host.source.calls == [] and dialog.snapshot is None
    dialog.refresh_button.click()
    dialog.query.setText("does-not-exist")
    dialog.filter_button.click()
    assert dialog.model.rowCount() == 0 and not dialog.select_button.isEnabled()


def test_metrics_when_real_rows_then_actual_qt_model_preserves_zero_missing_and_roles(host):
    from fontlab_python_lessons.domain import Metric
    from fontlab_python_lessons.models import metrics_model

    dialog = host.make("glyph-metrics-model")
    model = dialog.model
    assert model.rowCount() == 2 and model.columnCount() == 3
    assert model.data(model.index(1, 1)) == 0
    assert model.data(model.index(0, 2)) == 0
    assert model.headerData(1, QtCore.Qt.Horizontal) == "Advance"
    assert model.headerData(-1, QtCore.Qt.Horizontal) is None
    assert model.headerData(0, QtCore.Qt.Vertical) is None
    assert model.rowCount(model.index(0, 0)) == model.columnCount(model.index(0, 0)) == 0
    assert model.data(QtCore.QModelIndex()) is None
    assert model.data(model.index(0, 0), QtCore.Qt.ToolTipRole) is None
    assert model.data(model.index(0, 1), QtCore.Qt.TextAlignmentRole)
    assert not model.flags(model.index(0, 0)) & QtCore.Qt.ItemIsEditable
    assert model.flags(QtCore.QModelIndex()) == QtCore.Qt.NoItemFlags
    other = metrics_model(host.qt, (Metric("missing", None, None),), dialog)
    assert other.data(other.index(0, 1)) == "—"
    host.source.selected = []
    dialog.refresh_button.click()
    assert dialog.model.rowCount() == 0 and "0 selected" in dialog.status.text


def test_form_when_preview_then_loads_actual_resource_and_never_writes_font(host):
    dialog = host.make("glyph-metrics-form")
    assert dialog.snapshot is not None, dialog.status.text
    assert dialog.glyph_name.currentText == "A"
    assert dialog.actual_advance.text == "600" and dialog.actual_lsb.text == "0"
    dialog.advance_box.setValue(612.5)
    dialog.preview_button.click()
    assert "change +12.5" in dialog.result_label.text
    assert host.source.rows["A"] == (600, 0) and host.source.calls == []
    dialog.glyph_name.setCurrentIndex(3)
    assert dialog.actual_advance.text == "0" and dialog.actual_lsb.text == "0"
    host.source.rows["zero"] = (1, 0)
    dialog.preview_button.click()
    assert dialog.snapshot is None and not dialog.preview_button.isEnabled()
    assert dialog.result_label.text == ""
    dialog.refresh_button.click()
    assert dialog.snapshot is not None


@pytest.mark.parametrize("name", ["glyph-name-filter", "glyph-metrics-model", "glyph-metrics-form"])
def test_panel_when_no_font_and_read_failure_then_close_remains_connected(host, name):
    host.source.package = None
    dialog = host.make(name)
    assert dialog.snapshot is None and "Open a font" in dialog.status.text
    assert dialog.close_button.isEnabled()
    assert dialog._connections, "Close must remain owned and connected"
    dialog.close_button.click()
    assert dialog._connections == [], "App must disconnect every owned signal"


@pytest.mark.parametrize("name", ["glyph-name-filter", "glyph-metrics-model", "glyph-metrics-form"])
def test_panel_when_relaunch_then_replaces_only_owned_dialog_and_cleans_slots(host, name):
    first = host.make(name)
    second = host.make(name)
    assert first is not second and first._connections == []
    second.close()
    assert second.snapshot is None and second._connections == []


def test_form_when_missing_resource_or_controls_then_remains_closable(host, monkeypatch):
    from fontlab_python_lessons import forms

    monkeypatch.setattr(forms, "files", lambda package: Path("/nonexistent-owned-resource"))
    dialog = host.make("glyph-metrics-form")
    assert dialog.snapshot is None and "Cannot open" in dialog.status.text
    assert dialog.close_button.isEnabled()


def test_form_when_empty_font_then_has_no_invented_values_or_preview(host):
    host.source.names = host.source.selected = []
    dialog = host.make("glyph-metrics-form")
    assert dialog.snapshot is not None and dialog.snapshot.rows == ()
    assert dialog.actual_advance.text == "—" and not dialog.preview_button.isEnabled()


def test_capture_when_read_raises_then_clears_previously_displayed_models(host, monkeypatch):
    dialog = host.make("glyph-metrics-model")

    def fail():
        raise RuntimeError("owned read failure")

    monkeypatch.setattr(host.scripting, "names_font_glyphs", fail)
    dialog.refresh_button.click()
    assert dialog.snapshot is None and dialog.model is None
    assert "owned read failure" in dialog.status.text


def test_form_when_required_control_absent_then_deletes_partial_form_and_keeps_close(
    host, monkeypatch
):
    from fontlab_python_lessons import forms

    monkeypatch.setattr(forms, "CONTROL_NAMES", forms.CONTROL_NAMES + ("missingOwnedControl",))
    dialog = host.make("glyph-metrics-form")
    assert dialog.snapshot is None and "lacks required controls" in dialog.status.text
    assert dialog.close_button.isEnabled()


def test_actual_app_layout_when_empty_falsey_glyph_then_reads_its_zero_metrics(host, monkeypatch):
    from fontlab_python_lessons.domain import capture

    inspectors = importlib.import_module("fontlabapp.inspectors")

    class Glyph:
        def __bool__(self):
            return False

        def findLayer(self, name):
            return NS(
                isNull=False,
                advanceWidth=0,
                boundingBox=NS(width=lambda: 100, height=lambda: 100, x=lambda: 0),
            )

    host.source.package.findName = lambda name: Glyph()
    monkeypatch.setattr(host.scripting, "inspectors_api", lambda: inspectors)
    scanned = capture(host.scripting, "metrics")
    assert [(r.advance, r.lsb) for r in scanned.rows] == [(0, 0), (0, 0)]


def test_form_when_wrong_control_type_then_rejects_resource_and_releases_form(
    host, monkeypatch, tmp_path
):
    from fontlab_python_lessons import forms

    resource = ROOT / "src/fontlab_python_lessons/resources/glyph-metrics-form.ui"
    altered = tmp_path / "resources"
    altered.mkdir()
    (altered / resource.name).write_text(
        resource.read_text().replace(
            'class="QDoubleSpinBox" name="advanceBox"', 'class="QLabel" name="advanceBox"'
        )
    )
    monkeypatch.setattr(forms, "files", lambda package: tmp_path)
    dialog = host.make("glyph-metrics-form")
    assert dialog.snapshot is None and "wrong control type" in dialog.status.text
    assert dialog.close_button.isEnabled(), "Invalid resources must retain a working Close"


def test_form_when_corrupt_resource_then_close_remains_usable(host, monkeypatch, tmp_path):
    from fontlab_python_lessons import forms

    resources = tmp_path / "resources"
    resources.mkdir()
    (resources / "glyph-metrics-form.ui").write_text("<ui><broken")
    monkeypatch.setattr(forms, "files", lambda package: tmp_path)
    dialog = host.make("glyph-metrics-form")
    assert dialog.snapshot is None and dialog.status.text
    dialog.close_button.click()
    assert dialog._connections == [], "Corrupt resources must release owned signals"


def test_launch_when_unknown_name_then_refuses_before_native_import():
    from fontlab_python_lessons import launch

    with pytest.raises(ValueError, match="Unknown lesson"):
        launch("unknown")
