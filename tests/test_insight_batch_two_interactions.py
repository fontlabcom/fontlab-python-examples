# this_file: tests/test_insight_batch_two_interactions.py
"""Real Python worker/namespace logic with hardened owned Qt doubles."""

import threading
import time

import advanced_insight_doubles
import insight_doubles
import pytest
import test_second_batch

advanced_qt = advanced_insight_doubles.advanced_qt
insight_qt = insight_doubles.insight_qt
batch_qt = test_second_batch.batch_qt


def test_worker_when_run_then_plain_data_delivered_only_on_gui_and_joined(
    advanced_qt, monkeypatch
):
    from fontlab_python_examples import close, launch

    h = launch("worker-glyph-queue")
    gui_thread = threading.get_ident()
    producer_threads = []
    start = h.controls["start"].clicked.callbacks[0]

    def record_ord(value):
        producer_threads.append(threading.get_ident())
        return ord(value)

    monkeypatch.setitem(start.__globals__, "ord", record_ord)
    h.controls["start"].clicked.emit()
    h.controls["start"].clicked.emit()
    assert sum(t.name == "insight-glyph-audit" for t in threading.enumerate()) <= 1
    deadline = time.monotonic() + 1
    while h.snapshot()["phase"] == "running" and time.monotonic() < deadline:
        h.controls["timer"].timeout.emit()
        time.sleep(0.005)
    assert h.snapshot()["phase"] == "done"
    assert [row["glyph"] for row in h.snapshot()["results"]] == ["A", "H", "O", "space"]
    assert producer_threads and all(t != gui_thread for t in producer_threads)
    assert not h.snapshot()["worker_alive"] and not h.snapshot()["timer_active"]
    h.controls["start"].clicked.emit()
    h.controls["stop"].clicked.emit()
    assert h.snapshot()["phase"] == "stopped" and not h.snapshot()["worker_alive"]
    h.controls["start"].clicked.emit()
    close("worker-glyph-queue")
    assert not any(t.name == "insight-glyph-audit" for t in threading.enumerate())


def test_worker_when_calculation_fails_then_owned_error_and_shutdown(
    advanced_qt, monkeypatch
):
    from fontlab_python_examples import launch

    h = launch("worker-glyph-queue")
    start = h.controls["start"].clicked.callbacks[0]

    def bad_ord(value):
        raise ValueError("sample calculation failed")

    monkeypatch.setitem(start.__globals__, "ord", bad_ord)
    h.controls["start"].clicked.emit()
    deadline = time.monotonic() + 1
    while h.snapshot()["phase"] == "running" and time.monotonic() < deadline:
        h.controls["timer"].timeout.emit()
        time.sleep(0.005)
    assert h.snapshot()["phase"] == "error"
    assert h.snapshot()["error"] == "sample calculation failed"
    assert not h.snapshot()["worker_alive"] and not h.snapshot()["timer_active"]


def test_repl_when_evaluated_then_owned_globals_and_output_without_global_hooks(
    advanced_qt, capsys
):
    from fontlab_python_examples import close, launch

    h, other = launch("owned-repl"), launch("glyph-properties")

    def run(source):
        h.controls["input"].setText(source)
        h.controls["run"].clicked.emit()

    run("advance")
    assert "600" in h.snapshot()["output"]
    run("advance = 720")
    run("print(advance)")
    assert "720" in h.snapshot()["output"]
    assert not capsys.readouterr().out, "Never send console output to host stdout"
    run("unknown_name")
    assert "NameError" in h.snapshot()["error"]
    run("advance =")
    assert "SyntaxError" in h.snapshot()["error"]
    run("len(glyph_names)")
    assert not h.snapshot()["error"]
    assert other.snapshot()["glyph_role"] == "default"
    namespace = h.controls["run"].clicked.callbacks[0].__closure__
    h.controls["reset"].clicked.emit()
    assert h.snapshot()["executions"] == 0 and not h.snapshot()["output"]
    h.controls["input"].setText("advance")
    h.controls["input"].returnPressed.emit()
    assert "600" in h.snapshot()["output"]
    close("owned-repl")
    assert any(
        cell.cell_contents == {}
        for cell in namespace
        if isinstance(cell.cell_contents, dict)
    ), "Drop the owned namespace on close"


def test_undo_when_applied_then_native_stack_runs_overrides_and_discards_redo_branch(
    advanced_qt,
):
    from fontlab_python_examples import close, launch

    h = launch("metrics-undo")
    stack = h.controls["stack"]
    for value in (700, 800):
        h.controls["advance"].setValue(value)
        h.controls["apply"].clicked.emit()
    assert h.snapshot()["advance"] == 800 and h.snapshot()["count"] == 2
    h.controls["undo"].clicked.emit()
    assert h.snapshot()["advance"] == 700 and h.snapshot()["can_redo"]
    h.controls["redo"].clicked.emit()
    assert h.snapshot()["text"] == "Advance: 800"
    h.controls["undo"].clicked.emit()
    h.controls["advance"].setValue(750)
    h.controls["apply"].clicked.emit()
    assert h.snapshot()["advance"] == 750 and not h.snapshot()["can_redo"]
    assert h.snapshot()["count"] == 2
    close("metrics-undo")
    assert stack.clear_count == 1 and not stack.commands
    assert not stack.indexChanged.callbacks


def test_compiled_exposure_when_buttons_used_then_move_and_native_clear_slot(
    advanced_qt,
):
    from fontlab_python_examples import launch

    h = launch("compiled-slot-exposure")
    assert h.snapshot()["slot_index"] >= 0
    h.controls["move"].clicked.emit()
    assert h.snapshot()["position"] == [20, 10]
    h.controls["clear"].clicked.emit()
    assert h.snapshot()["input"] == ""
    assert not h.snapshot()["compiled_here"]


def test_handle_disconnect_when_untracked_then_does_not_remove_other_receivers(
    advanced_qt,
):
    from fontlab_python_examples import launch

    h = launch("plugin-tokens")
    with pytest.raises(ValueError, match="not tracked"):
        h.disconnect(h.controls["install"].clicked, lambda: None)
    assert len(h.connections) == 2
