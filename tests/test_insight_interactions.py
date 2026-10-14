# this_file: tests/test_insight_interactions.py
"""Observable owned interactions; no native acceptance is inferred."""

from types import SimpleNamespace

import insight_doubles
import pytest
import test_second_batch

# Expose existing fixtures without redefining the boundary.
insight_qt = insight_doubles.insight_qt
batch_qt = test_second_batch.batch_qt


def test_interactions_when_owned_then_observable_changes_and_bounded_work(insight_qt):
    from fontlab_python_examples import launch

    h = launch("signal-lifetime")
    h.controls["button"].clicked.emit()
    assert h.snapshot()["advance"] == 610
    h = launch("glyph-list")
    h.controls["filter"].text = "a"
    h.controls["apply"].clicked.emit()
    assert h.snapshot()["glyph_names"] == ["A", "Aacute"]
    h.controls["filter"].text = "missing"
    h.controls["apply"].clicked.emit()
    assert h.snapshot()["glyph_names"] == []
    h = launch("timer-batch")
    timer = h.controls["timer"]
    for _ in range(5):
        timer.timeout.emit()
    assert h.snapshot()["processed"] == 4 and not timer.active
    h.close()
    assert not timer.active and not timer.timeout.callbacks
    h = launch("metric-controls")
    h.controls["spin"].setValue(720)
    assert h.snapshot()["slider"] == 720
    h.controls["slider"].setValue(340)
    assert h.snapshot()["spin"] == 340
    assert h.snapshot()["updates"] == 2, "No recursive value feedback"
    h = launch("glyph-properties")
    h.controls["button"].clicked.emit()
    assert h.snapshot()["glyph_role"] == "alternate"
    h = launch("callback-errors")
    h.controls["input"].text = "bad"
    h.controls["apply"].clicked.emit()
    assert h.snapshot()["error"] and h.snapshot()["advance"] == 600
    h.controls["input"].text = "750"
    h.controls["apply"].clicked.emit()
    assert not h.snapshot()["error"] and h.snapshot()["advance"] == 750


def test_table_when_queried_then_headers_values_and_invalid_indices(insight_qt):
    from fontlab_python_examples import launch

    h = launch("metrics-table")
    model, qt = h.model, insight_qt.QtCore.Qt
    assert model.rowCount() == 3 and model.columnCount() == 3
    assert model.data(model.index(0, 1), qt.DisplayRole) == 600
    assert model.headerData(0, qt.Horizontal) == "Glyph"
    assert model.data(model.index(99, 0)) is None
    assert model.data(model.index(-1, 0)) is None
    assert model.data(model.index(0, 0), 999) is None
    assert model.rowCount(model.index(0, 0)) == 0
    assert model.columnCount(model.index(0, 0)) == 0
    assert model.headerData(99, qt.Horizontal) is None
    assert model.headerData(0, 999) is None


def test_event_filter_when_keys_arrive_then_only_owned_target_is_observed(insight_qt):
    from fontlab_python_examples import launch

    h = launch("owned-key-filter")
    controls = h.controls
    event = SimpleNamespace(
        type=lambda: insight_qt.QtCore.QEvent.KeyPress, text=lambda: "a"
    )
    filt = controls["filter"]
    assert filt.eventFilter(controls["editor"], event) is False
    assert filt.eventFilter(object(), event) is False
    assert h.snapshot()["keys"] == ["a"]
    for _ in range(40):
        filt.eventFilter(controls["editor"], event)
    assert len(h.snapshot()["keys"]) == 20, "Keep the log bounded"
    editor = controls["editor"]
    h.close()
    assert not editor.filters and filt.target is None


def test_paint_when_draw_raises_then_painter_always_ends(insight_qt, monkeypatch):
    from fontlab_python_examples import launch

    h = launch("contour-canvas")
    h.widget.paintEvent(None)
    assert insight_qt.paint_events == ["begin", "draw", "end"]

    def fail(self, path):
        raise RuntimeError("draw failed")

    monkeypatch.setattr(insight_qt.QtGui.QPainter, "drawPath", fail)
    with pytest.raises(RuntimeError, match="draw failed"):
        h.widget.paintEvent(None)
    assert insight_qt.paint_events[-1] == "end"
    h.close()


def test_settings_when_saved_then_owned_namespace_persists_and_can_be_reset(insight_qt):
    from fontlab_python_examples import close, launch

    h = launch("sandbox-settings")
    assert not insight_qt.settings_writes, "Build must not write preferences"
    h.controls["input"].text = "HAMBURGEFONTSIV"
    h.controls["save"].clicked.emit()
    assert h.snapshot()["saved"] == "HAMBURGEFONTSIV"
    close("sandbox-settings")
    h = launch("sandbox-settings")
    assert h.snapshot()["sample"] == "HAMBURGEFONTSIV"
    h.controls["reset"].clicked.emit()
    assert not insight_qt.settings_store
    assert set(insight_qt.settings_writes) == {"proof/sample"}


def test_dock_and_scene_when_built_then_owned_content_and_geometry(insight_qt):
    from fontlab_python_examples import launch

    h = launch("owned-dock")
    dock = h.controls["dock"]
    assert dock.parent is h.widget
    h.controls["toggle"].clicked.emit()
    assert dock.isVisible()
    h = launch("contour-scene")
    scene = h.controls["scene"]
    assert scene.parent is h.widget
    assert len(scene.scene_items) == 3, "Contour, baseline and advance guide"


def test_callback_when_boundary_values_then_previous_valid_value_survives(insight_qt):
    from fontlab_python_examples import launch

    h = launch("callback-errors")
    for raw in ("", "-1", "2001", "9" * 5000):
        h.controls["input"].text = raw
        h.controls["apply"].clicked.emit()
        assert h.snapshot()["error"] and h.snapshot()["advance"] == 600, raw[:20]
    for raw in ("0", "2000"):
        h.controls["input"].text = raw
        h.controls["apply"].clicked.emit()
        assert h.snapshot()["advance"] == int(raw) and not h.snapshot()["error"]


def test_settings_when_sync_fails_then_owned_error_is_observable(
    insight_qt, monkeypatch
):
    from fontlab_python_examples import launch

    monkeypatch.setattr(insight_qt.QtCore.QSettings, "status", lambda self: 1)
    h = launch("sandbox-settings")
    h.controls["save"].clicked.emit()
    assert h.snapshot()["error"] == "Settings write failed"
