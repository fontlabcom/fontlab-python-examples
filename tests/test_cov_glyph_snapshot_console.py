# this_file: tests/test_cov_glyph_snapshot_console.py
# SPDX-License-Identifier: Apache-2.0
"""Cover Glyph Snapshot Console: trace guard internals, capture and panel lifecycle.

Loops under test are bounded by a wall-clock valve inside the namespace, so a
tracer that silently drops the guard (coverage's C tracer) fails the assertion
instead of hanging the suite.
"""

from __future__ import annotations

import runpy
import sys
import time
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest

import _cov_support
from _cov_support import Event, Widget, install_fly, make_qt

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Tools/Glyph Snapshot Console.py"
ROWS = (("A", "U+0041", ""), ("B", "", "2026-01-02 03:04:05"))
VALVE_SECONDS = 3.0


@pytest.fixture
def module() -> dict[str, Any]:
    return runpy.run_path(str(SCRIPT))


@pytest.fixture
def env(monkeypatch: Any) -> NS:
    qt = make_qt()
    return NS(qt=qt, fly=install_fly(monkeypatch, qt))


def namespace(module: dict[str, Any], **extra: Any) -> dict[str, Any]:
    ns = module["snapshot_namespace"](ROWS)
    ns.update(extra)
    return ns


def grab_guard(module: dict[str, Any], seconds: float, previous: Any) -> Any:
    """Run evaluate once under ``previous`` and return the guard closure it installed."""
    seen: dict[str, Any] = {}

    def grab() -> int:
        seen["guard"] = sys.gettrace()
        return 1

    original = sys.gettrace()
    sys.settrace(previous)
    try:
        assert module["evaluate"]("grab()", namespace(module, grab=grab), seconds) == "1"
    finally:
        sys.settrace(original)
    return seen["guard"]


class Frame:
    """Hashable frame double (the guard keys frames in a dict)."""

    def __init__(self, name: str, opcodes: bool) -> None:
        self.f_code, self.f_trace_opcodes = NS(co_filename=name), opcodes


def frame(name: str, *, opcodes: bool = False) -> Frame:
    return Frame(name, opcodes)


class Recorder:
    """Previous-trace double that logs events and keeps tracing."""

    def __init__(self) -> None:
        self.events: list[str] = []

    def __call__(self, frame_: Any, event: str, arg: Any) -> Any:
        self.events.append(event)
        return self


def test_evaluate_when_loop_outlives_deadline_then_timeout_error_and_trace_restored(
    module: dict[str, Any],
) -> None:
    started = time.monotonic()
    ns = namespace(module, expired=lambda: time.monotonic() - started > VALVE_SECONDS)
    before = sys.gettrace()
    with pytest.raises(TimeoutError, match="Query exceeded 0.05 seconds"):
        module["evaluate"]("while not expired(): pass", ns, 0.05)
    assert time.monotonic() - started < VALVE_SECONDS, "the guard, not the valve, stopped the loop"
    assert sys.gettrace() is before, "the earlier host trace must be restored"


def test_evaluate_when_call_stalls_without_line_events_then_final_check_raises(
    module: dict[str, Any],
) -> None:
    ns = namespace(module, stall=lambda: time.sleep(0.12))
    with pytest.raises(TimeoutError, match="Query exceeded 0.05 seconds"):
        module["evaluate"]("stall()", ns, 0.05)


def test_evaluate_when_print_expression_then_output_is_result(module: dict[str, Any]) -> None:
    assert module["evaluate"]("print('hi')", namespace(module)) == "hi\n"


def test_evaluate_when_deadline_out_of_range_then_refuses(module: dict[str, Any]) -> None:
    for seconds in (0, -1, 60.5):
        with pytest.raises(ValueError, match="at most 60 seconds"):
            module["evaluate"]("1", namespace(module), seconds)


def test_evaluate_when_host_trace_is_opaque_then_refuses_without_running(
    module: dict[str, Any], monkeypatch: Any
) -> None:
    ran: list[int] = []
    ns = namespace(module, mark=lambda: ran.append(1))
    with monkeypatch.context() as patch:
        patch.setattr(sys, "gettrace", lambda: object())
        with pytest.raises(RuntimeError, match="Time limit unavailable"):
            module["evaluate"]("mark()", ns)
    assert ran == [], "no query code may run without a usable deadline"


def test_guard_when_frame_unwatched_then_chains_previous_and_leaves_opcodes_alone(
    module: dict[str, Any],
) -> None:
    previous = Recorder()
    guard = grab_guard(module, 5.0, previous)
    previous.events.clear()
    other = frame("host.py")
    local = guard(other, "call", None)
    assert previous.events == ["call"]
    assert local(other, "line", None) is local
    assert previous.events == ["call", "line"]
    assert other.f_trace_opcodes is False, "unwatched frames keep their opcode flag"


def test_guard_when_frame_watched_then_enables_opcodes_and_filters_opcode_events(
    module: dict[str, Any],
) -> None:
    previous = Recorder()
    guard = grab_guard(module, 5.0, previous)
    previous.events.clear()
    query = frame("<glyph-snapshot>")
    local = guard(query, "call", None)
    assert query.f_trace_opcodes is True, "single-line loops need opcode events"
    local(query, "opcode", None)
    assert previous.events == ["call"], "earlier trace did not ask for opcodes"
    local(query, "line", None)
    assert previous.events == ["call", "line"]
    asked = frame("<glyph-snapshot>", opcodes=True)
    local = guard(asked, "call", None)
    local(asked, "opcode", None)
    assert previous.events[-1] == "opcode", "opcodes pass through when the host wanted them"


def test_guard_when_no_previous_trace_then_only_deadline_is_enforced(
    module: dict[str, Any],
) -> None:
    guard = grab_guard(module, 5.0, None)
    query = frame("<glyph-snapshot>")
    local = guard(query, "call", None)
    assert local(query, "line", None) is local and query.f_trace_opcodes is True


def test_guard_when_deadline_passed_then_call_event_raises(module: dict[str, Any]) -> None:
    guard = grab_guard(module, 0.05, Recorder())
    time.sleep(0.1)
    with pytest.raises(TimeoutError, match="Query exceeded 0.05 seconds"):
        guard(frame("<glyph-snapshot>"), "call", None)
    guard(frame("host.py"), "call", None)  # unwatched frames never time out


def test_local_trace_when_deadline_passes_mid_frame_then_next_event_raises(
    module: dict[str, Any],
) -> None:
    guard = grab_guard(module, 0.15, Recorder())
    query = frame("<glyph-snapshot>")
    local = guard(query, "call", None)
    local(query, "line", None)
    time.sleep(0.2)
    with pytest.raises(TimeoutError, match="Query exceeded 0.15 seconds"):
        local(query, "line", None)


def test_capture_current_when_no_package_then_refuses(module: dict[str, Any], env: NS) -> None:
    env.fly.scripting.current_package = lambda: None
    with pytest.raises(ValueError, match="Open a font before scanning"):
        module["capture_current"](Widget())


@pytest.mark.parametrize(("count", "label"), [(100, "12"), (10_000_000, "120")])
def test_capture_current_when_scaled_then_status_shows_budget_and_deadline_passed(
    module: dict[str, Any], env: NS, count: int, label: str
) -> None:
    seen: dict[str, float] = {}
    env.fly.scripting.current_package = lambda: NS(glyphsCount=count)
    env.fly.catalog.capture = lambda *, deadline: seen.setdefault("deadline", deadline) or "snap"
    status = Widget()
    start = time.monotonic()
    module["capture_current"](status)
    assert f"budget {label} s" in status.text() and f"{count:,}" in status.text()
    assert abs(seen["deadline"] - start - float(label)) < 1.0, "deadline = now + budget"


def build(module: dict[str, Any], env: NS) -> Any:
    return module["show"](env.qt, None)


def click(panel: Any, index: int) -> None:
    panel.scope.pairs[index][0].emit()


def test_show_when_built_then_panel_registered_with_defaults(module: dict[str, Any], env: NS) -> None:
    panel = build(module, env)
    assert module["_PANELS"] == [panel] and panel.shown == 1
    assert panel.query_namespace is None and panel.query_entry.text() == "len(glyphs)"
    assert panel.deadline_control.value() == 5.0


def test_run_query_when_not_captured_then_output_reports_capture_first(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    click(panel, 3)
    assert panel.output_box.plainText() == "ValueError: Capture before Run."
    assert panel.status_line.text().startswith("Query failed.")


def test_capture_then_run_when_enter_pressed_then_result_shown(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    monkeypatch.setitem(module["show"].__globals__, "capture_current",
                        lambda status: NS(rows=ROWS))
    panel = build(module, env)
    click(panel, 2)
    assert panel.status_line.text() == "Ready: 2 glyphs. Capture resets variables."
    panel.query_entry.returnPressed.emit()
    assert panel.output_box.plainText() == "2"
    assert panel.status_line.text().startswith("Result from the captured snapshot")


def test_run_query_when_code_fails_or_deadline_invalid_then_error_text_and_hint(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    monkeypatch.setitem(module["show"].__globals__, "capture_current",
                        lambda status: NS(rows=ROWS))
    panel = build(module, env)
    click(panel, 2)
    panel.query_entry.setText("1 / 0")
    panel.run_query()
    assert panel.output_box.plainText() == "ZeroDivisionError: division by zero"
    panel.query_entry.setText("1")
    panel.deadline_control.setValue(0)
    panel.run_query()
    assert panel.output_box.plainText().startswith("ValueError: Choose a query deadline")
    assert panel.status_line.text().startswith("Query failed.")


def test_clear_snapshot_when_clicked_then_namespace_dropped_and_run_refused(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    monkeypatch.setitem(module["show"].__globals__, "capture_current",
                        lambda status: NS(rows=ROWS))
    panel = build(module, env)
    click(panel, 2)
    panel.output_box.setPlainText("old")
    click(panel, 4)
    assert panel.query_namespace is None and panel.output_box.plainText() == ""
    assert panel.status_line.text() == "Snapshot cleared. Capture again before Run."


def test_capture_rows_when_scan_fails_then_status_gets_error_via_scope(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    def refuse(status: Any) -> Any:
        raise ValueError("Open a font before scanning.")

    monkeypatch.setitem(module["show"].__globals__, "capture_current", refuse)
    panel = build(module, env)
    click(panel, 2)
    assert panel.status_line.text() == "Open a font before scanning."
    assert panel.query_namespace is None


def test_destroyed_signal_when_emitted_then_panel_unregistered(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.destroyed.emit()
    assert module["_PANELS"] == []
    panel.release_owner()  # second release stays harmless
    assert module["_PANELS"] == []


def test_close_event_when_disconnect_refused_then_ignored_and_kept(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.scope.refuse = True
    event = Event()
    panel.closeEvent(event)
    assert event.ignored and not event.accepted and not panel.deleted
    assert module["_PANELS"] == [panel]
    panel.scope.refuse = False
    event = Event()
    panel.closeEvent(event)
    assert event.accepted and panel.deleted and module["_PANELS"] == []


def test_show_when_panel_show_fails_then_clean_panel_removed_and_error_raised(
    module: dict[str, Any], env: NS
) -> None:
    class Failing(Widget):
        show_error = RuntimeError("cannot show")

    with pytest.raises(RuntimeError, match="cannot show"):
        module["show"](make_qt(Failing), None)
    assert module["_PANELS"] == [], "a cleanly closed panel must not stay registered"


def test_show_when_panel_show_fails_and_disconnect_refused_then_panel_kept(
    module: dict[str, Any], monkeypatch: Any
) -> None:
    class Failing(Widget):
        show_error = RuntimeError("cannot show")

    qt = make_qt(Failing)
    install_fly(monkeypatch, qt)
    monkeypatch.setattr(_cov_support.Scope, "refuse_default", True)
    with pytest.raises(RuntimeError, match="cannot show"):
        module["show"](qt, None)
    (panel,) = module["_PANELS"]
    assert panel.shown == 2, "a panel that cannot be torn down is shown again for a Close retry"
    assert panel.query_namespace is None


def test_main_when_window_available_then_panel_opens(module: dict[str, Any], env: NS) -> None:
    module["main"]()
    assert len(module["_PANELS"]) == 1


@pytest.mark.parametrize("error", [ValueError("no window"), AttributeError("no MainWindow")])
def test_main_when_window_lookup_fails_then_message_printed(
    module: dict[str, Any], env: NS, capsys: Any, error: Exception
) -> None:
    def fail() -> Any:
        raise error

    env.fly.root.fl = NS(MainWindow=fail)
    module["main"]()
    assert capsys.readouterr().out == f"Glyph Snapshot Console: {error}\n"
    assert module["_PANELS"] == []


def test_script_when_run_as_main_then_main_executes(env: NS, capsys: Any) -> None:
    env.fly.root.fl = NS(MainWindow=lambda: (_ for _ in ()).throw(ValueError("no window")))
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert "Glyph Snapshot Console: no window" in capsys.readouterr().out
