# this_file: tests/test_cov_font_drop_inspector.py
# SPDX-License-Identifier: Apache-2.0
"""Cover Font Drop Inspector panel behaviour with offline Qt/Fly doubles."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest

from _cov_support import Event, Widget, install_fly, make_qt

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Drag And Drop/Font Drop Inspector.py"


class Url:
    """URL double with local-file and plain-string forms."""

    def __init__(self, path: str, local: bool) -> None:
        self.path, self.local = path, local

    def isLocalFile(self) -> bool:
        return self.local

    def toLocalFile(self) -> str:
        return self.path

    def toString(self) -> str:
        return self.path


class Mime:
    """MIME payload double."""

    def __init__(self, formats: list[str], *, text: str | None = None,
                 urls: list[Url] | None = None) -> None:
        self._formats, self._text, self._urls = formats, text, urls

    def formats(self) -> list[str]:
        return self._formats

    def hasUrls(self) -> bool:
        return self._urls is not None

    def urls(self) -> list[Url]:
        return self._urls or []

    def hasText(self) -> bool:
        return self._text is not None

    def text(self) -> str:
        return self._text or ""


class ExplodingMime:
    """Payload whose format listing fails, like a broken native drop."""

    def formats(self) -> list[str]:
        raise RuntimeError("bad payload")


FACTS = NS(rows=(NS(name="A", unicodes=(65,)), NS(name="A.alt", unicodes=(65,)),
                 NS(name="V", unicodes=(86,))))


@pytest.fixture
def module() -> dict[str, Any]:
    return runpy.run_path(str(SCRIPT))


@pytest.fixture
def env(monkeypatch: Any) -> NS:
    qt = make_qt()
    return NS(qt=qt, fly=install_fly(monkeypatch, qt))


def build(module: dict[str, Any], env: NS, facts: Any = FACTS) -> Any:
    def capture() -> Any:
        if isinstance(facts, Exception):
            raise facts
        return facts

    return module["panel_type"](env.qt, capture)()


def test_coverage_report_when_text_exceeds_limit_then_refuses(module: dict[str, Any]) -> None:
    with pytest.raises(ValueError, match="5,000"):
        module["coverage_report"](FACTS, "A" * 5001)
    assert module["coverage_report"](FACTS, "A" * 5000).count("\n") == 4999, "limit is inclusive"


def test_refresh_when_capture_fails_then_status_shows_error_and_output_cleared(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env, ValueError("No font open."))
    assert panel.facts is None, "no facts are kept when capture fails"
    assert panel.status.text() == "No font open.", "capture error reaches the status"
    panel.output.setPlainText("stale")
    panel.refresh()
    assert panel.output.plainText() == "", "stale output must go when the font is gone"


def test_refresh_when_capture_succeeds_then_status_reports_snapshot(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    assert panel.facts is FACTS, "captured facts are kept"
    assert panel.status.text().startswith("Current-font snapshot captured"), "status reports the snapshot"


def test_use_input_when_clicked_then_reports_coverage_and_clears_entry(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.entry.setText("A ?")
    panel.scope.pairs[1][0].emit()
    assert panel.output.plainText() == "1: U+0041 → A, A.alt\n3: U+003F → MISSING", "report lists glyphs per character and flags missing ones"
    assert panel.entry.text() == "", "input is cleared after success"


def test_use_input_when_text_refused_then_failure_reaches_status(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.entry.setText("A" * 5001)
    panel.scope.pairs[1][0].emit()
    assert "5,000" in panel.status.text(), "the length refusal names the limit"
    assert panel.entry.text() == "A" * 5001, "refused input stays for correction"


def test_clear_when_clicked_then_draft_and_output_removed(module: dict[str, Any], env: NS) -> None:
    panel = build(module, env)
    panel.items.addItems(["text/plain"])
    panel.output.setPlainText("report")
    panel.scope.pairs[2][0].emit()
    assert panel.text_items() == (), "listed formats are removed"
    assert panel.output.plainText() == "", "output is removed"
    assert panel.status.text() == "Draft cleared.", "status confirms the clear"


def test_copy_output_when_empty_then_refuses_and_when_filled_then_copies(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.scope.pairs[3][0].emit()
    assert panel.status.text() == "There is no output to copy.", "empty output is refused"
    assert env.qt.clipboard.text() == "", "clipboard untouched on refusal"
    panel.output.setPlainText("report")
    panel.copy_output()
    assert env.qt.clipboard.text() == "report", "filled output is copied"


def test_receive_when_urls_dropped_then_lists_paths_without_opening(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.receive(Mime(["text/uri-list"], urls=[Url("/tmp/a.ufo", True), Url("http://x/y", False)]))
    assert panel.output.plainText() == (
        "MIME formats:\ntext/uri-list\nDropped URLs (not opened):\n/tmp/a.ufo\nhttp://x/y"
    ), "formats and URL paths are listed, nothing opened"
    assert panel.text_items() == ("text/uri-list",), "formats fill the item list"


def test_receive_when_text_dropped_then_reports_coverage_and_fills_entry(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.receive(Mime(["text/plain"], text="V?"))
    assert panel.output.plainText().endswith("1: U+0056 → V\n2: U+003F → MISSING"), "dropped text is checked against the font"
    assert panel.entry.text() == "V?", "dropped text fills the entry"


def test_receive_when_dropped_text_too_long_then_error_line_replaces_report(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.receive(Mime(["text/plain"], text="A" * 5001))
    assert panel.output.plainText().endswith("Check at most 5,000 characters at a time."), "over-long drop gets the limit line"


def test_receive_when_no_font_then_text_drop_reports_open_font(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env, ValueError("none"))
    panel.receive(Mime(["text/plain"], text="A"))
    assert panel.output.plainText().endswith("Open a font and refresh first."), "text drop without a font asks to open one"


def test_receive_when_binary_then_names_formats_only(module: dict[str, Any], env: NS) -> None:
    panel = build(module, env)
    panel.receive(Mime(["image/png"]))
    assert panel.output.plainText().endswith("No text or URLs; binary content was not decoded."), "binary drops are named, not decoded"


def test_items_drag_enter_when_formats_then_copy_accept_else_ignore(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    good, empty, moved = Event(Mime(["a"])), Event(Mime([])), Event(Mime(["a"]))
    panel.items.dragEnterEvent(good)
    panel.items.dragEnterEvent(empty)
    panel.items.dragMoveEvent(moved)
    assert good.accepted, "a payload with formats is accepted"
    assert good.action == 1, "acceptance uses the copy action"
    assert empty.ignored, "a payload without formats is ignored"
    assert not empty.accepted, "an ignored payload is not accepted"
    assert moved.accepted, "move re-evaluates acceptance"


def test_items_drop_when_receive_fails_then_event_ignored_and_status_set(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    ok = Event(Mime(["text/plain"], text="A"))
    panel.items.dropEvent(ok)
    assert ok.accepted, "a valid drop is accepted"
    assert not ok.ignored, "a valid drop is not ignored"
    bad = Event(ExplodingMime())
    panel.items.dropEvent(bad)
    assert bad.ignored, "a failing drop is ignored"
    assert panel.status.text() == "bad payload", "the drop failure reaches the status"


def test_start_drag_when_no_output_then_status_asks_for_content(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.items.startDrag(1)
    assert panel.status.text() == "Drop content before dragging the inspection report.", "empty report cannot be dragged"
    assert env.qt.drags == [], "no drag object for an empty report"


def test_start_drag_when_output_then_copy_drag_released(module: dict[str, Any], env: NS) -> None:
    panel = build(module, env)
    panel.output.setPlainText("report")
    panel.items.startDrag(1)
    (drag,) = env.qt.drags
    assert drag.mime.value == "report", "the report text is the drag payload"
    assert drag.deleted, "the drag object is released"
    assert not panel.busy, "busy flag is cleared after the drag"


def test_drag_output_when_target_raises_then_busy_cleared_and_error_shown(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    panel = build(module, env)
    panel.output.setPlainText("report")
    monkeypatch.setattr(env.qt.Drag, "failure", RuntimeError("target refused"))
    panel.drag_output()
    assert panel.status.text() == "target refused", "drag failure reaches the status"
    assert not panel.busy, "busy flag is cleared after failure"
    assert env.qt.drags[0].deleted, "the drag object is released after failure"


def test_export_mouse_when_left_press_and_far_move_then_drag_starts_once(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.output.setPlainText("report")
    export = panel.export
    export.mouseMoveEvent(Event(point=(50, 50)))
    assert export.origin is None, "move without press arms nothing"
    assert env.qt.drags == [], "move without press does nothing"
    export.mousePressEvent(Event(point=(0, 0), button=2))
    assert export.origin is None, "right button never arms a drag"
    export.mousePressEvent(Event(point=(0, 0), button=1))
    export.mouseMoveEvent(Event(point=(1, 1), buttons=1))
    assert export.origin is not None, "press arms the drag origin"
    assert env.qt.drags == [], "below threshold no drag starts"
    export.mouseMoveEvent(Event(point=(9, 9), buttons=0))
    assert env.qt.drags == [], "button released: no drag"
    export.mouseMoveEvent(Event(point=(9, 9), buttons=1))
    assert len(env.qt.drags) == 1, "a far move with button held starts one drag"
    assert export.origin is None, "origin is reset after the drag"


def test_close_event_when_busy_or_disconnect_refused_then_ignored(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.busy = True
    event = Event()
    panel.closeEvent(event)
    assert event.ignored, "close is ignored while a drag is busy"
    assert not panel.deleted, "busy panel is not deleted"
    panel.busy = False
    panel.scope.refuse = True
    event = Event()
    panel.closeEvent(event)
    assert event.ignored, "failed disconnect keeps the panel for a Close retry"
    panel.scope.refuse, panel.terminal.refuse = False, True
    assert panel.dispose() is False, "terminal scope refusal also blocks cleanup"


def test_close_event_when_clean_then_registry_key_removed_and_panel_deleted(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    panel = build(module, env)
    registry = {module["KEY"]: panel, "other": 1}
    monkeypatch.setattr(sys, "_fontlab_samples", registry, raising=False)
    event = Event()
    panel.closeEvent(event)
    assert event.accepted, "clean close is accepted"
    assert panel.deleted, "clean close deletes the panel"
    assert registry == {"other": 1}, "only the panel's own registry key is removed"
    assert panel.facts is None, "snapshot facts are dropped"


def test_destroyed_signal_when_emitted_then_dispose_keeps_foreign_registry_entry(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    panel = build(module, env)
    registry = {module["KEY"]: "someone else"}
    monkeypatch.setattr(sys, "_fontlab_samples", registry, raising=False)
    panel.destroyed.emit()
    assert registry == {module["KEY"]: "someone else"}, "only the owning panel is unregistered"
    assert panel.facts is None, "snapshot facts are dropped"


def test_main_when_called_then_shows_panel_through_fly(
    module: dict[str, Any], env: NS
) -> None:
    env.fly.capture_module.capture = lambda: FACTS
    env.fly.scripting.show_script_dialog = lambda panel, key: (panel, key)
    panel_cls, key = module["main"]()
    assert key == "drag_drop_dropsite", "panel is shown under its registry key"
    assert issubclass(panel_cls, Widget), "main passes the panel class to Fly"


def test_script_when_run_as_main_then_main_executes(env: NS) -> None:
    shown: list[str] = []
    env.fly.capture_module.capture = lambda: FACTS
    env.fly.scripting.show_script_dialog = lambda panel, key: shown.append(key)
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert shown == ["drag_drop_dropsite"], "__main__ run reaches main()"
