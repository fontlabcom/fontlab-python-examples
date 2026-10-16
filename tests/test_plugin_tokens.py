# this_file: tests/test_plugin_tokens.py
"""Dynamic menu token idempotency and disconnect-before-delete failure behavior."""

import advanced_insight_doubles
import insight_doubles
import pytest
import test_second_batch

advanced_qt = advanced_insight_doubles.advanced_qt
insight_qt = insight_doubles.insight_qt
batch_qt = test_second_batch.batch_qt


def test_plugin_when_installed_and_unloaded_twice_then_tokens_and_pairs_are_idempotent(
    advanced_qt,
):
    from fontlab_python_examples import close, launch

    h = launch("plugin-tokens")
    for _ in range(2):
        h.controls["install"].clicked.emit()
    assert h.snapshot()["tokens"] == ["advance-action", "proof-menu"]
    assert len(h.widget.menuBar().actions()) == 1 and len(h.connections) == 3
    action = h.controls["plugin_action"]
    action.trigger()
    assert h.snapshot()["invocations"] == 1
    for _ in range(2):
        h.controls["unload"].clicked.emit()
    assert not h.snapshot()["tokens"] and not action.triggered.callbacks
    assert len(h.connections) == 2 and not h.widget.menuBar().actions()
    assert h.controls["plugin_action"] is None and len(advanced_qt.deleted_menus) == 1
    h.controls["install"].clicked.emit()
    action = h.controls["plugin_action"]
    close("plugin-tokens")
    assert not action.triggered.callbacks and len(advanced_qt.deleted_menus) == 2


def test_plugin_when_disconnect_fails_then_tokens_and_owned_menu_are_retained(
    advanced_qt, monkeypatch
):
    from fontlab_python_examples import launch

    h = launch("plugin-tokens")
    h.controls["install"].clicked.emit()
    signal = h.controls["plugin_action"].triggered

    def fail(slot):
        raise RuntimeError("disconnect failed")

    with monkeypatch.context() as patch:
        patch.setattr(signal, "disconnect", fail)
        with pytest.raises(RuntimeError, match="disconnect failed"):
            h.controls["unload"].clicked.emit()
        assert h.snapshot()["registered"] and len(h.connections) == 3
        assert not advanced_qt.deleted_menus, "Never delete with live tracked receivers"
    h.controls["unload"].clicked.emit()
    assert not h.snapshot()["registered"]
