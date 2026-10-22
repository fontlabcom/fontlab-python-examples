# this_file: tests/test_cov_symbol_tag_search.py
# SPDX-License-Identifier: Apache-2.0
"""Cover Symbol Tag Search refusals, name filtering and the owned panel lifecycle."""

from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest

import _cov_support
from _cov_support import Event, Widget, install_fly, make_qt

SCRIPT = Path(__file__).resolve().parents[1] / "Scripts/Tools/Symbol Tag Search.py"
FAR = 1.0e18


class Glyph:
    """Native glyph double."""

    def __init__(self, name: Any, tags: Any = (), *, null: bool = False) -> None:
        self.name, self.tags, self.isNull = name, tags, null


class Native:
    """Native ``fl`` double; ``flips`` makes the package change after the scan."""

    def __init__(self, glyphs: list[Any], *, package_null: bool = False,
                 font_id: int = 99, flips: bool = False, no_package: bool = False,
                 no_font: bool = False) -> None:
        self.glyphs = glyphs
        self.package = NS(id=7, fgId=99, isNull=package_null, findFgId=self.find)
        self.other = NS(id=8, fgId=99, isNull=False, findFgId=self.find)
        self.font = None if no_font else NS(
            id=font_id, glyphs=[NS(id=i) for i in range(len(glyphs))])
        self.flips, self.no_package, self.reads = flips, no_package, 0
        self.flWorkspace = NS(instance=lambda: self)

    def find(self, index: int) -> Any:
        return self.glyphs[index]

    @property
    def currentPackage(self) -> Any:
        if self.no_package:
            return None
        self.reads += 1
        return self.other if self.flips and self.reads > 1 else self.package

    def CurrentFont(self) -> Any:  # noqa: N802 - mirrors the native API
        return self.font


@pytest.fixture
def module() -> dict[str, Any]:
    return runpy.run_path(str(SCRIPT))


@pytest.fixture
def env(monkeypatch: Any) -> NS:
    qt = make_qt()
    return NS(qt=qt, fly=install_fly(monkeypatch, qt))


def test_capture_tags_when_native_omitted_then_reads_fly_fl(module: dict[str, Any], env: NS) -> None:
    env.fly.root.fl = Native([Glyph("arrow", ["a"]), Glyph("dot")])
    rows, skipped = module["capture_tags"](deadline=FAR)
    assert rows == (("arrow", ("a",)), ("dot", ())) and skipped == ()


def test_capture_tags_when_off_main_thread_then_refuses(
    module: dict[str, Any], monkeypatch: Any
) -> None:
    monkeypatch.setitem(module["capture_tags"].__globals__, "main_thread", lambda: object())
    with pytest.raises(RuntimeError, match="main UI thread"):
        module["capture_tags"](Native([]))


@pytest.mark.parametrize("native", [
    Native([], no_package=True),
    Native([], package_null=True),
    Native([], no_font=True),
    Native([], font_id=5),
], ids=["no-package", "null-package", "no-font", "font-mismatch"])
def test_capture_tags_when_no_matching_font_then_open_font_refusal(
    module: dict[str, Any], native: Native
) -> None:
    with pytest.raises(ValueError, match="Open a font first"):
        module["capture_tags"](native, deadline=FAR)


@pytest.mark.parametrize("gone", [None, Glyph("A", null=True)], ids=["missing", "null"])
def test_capture_tags_when_glyph_disappears_then_refresh_requested(
    module: dict[str, Any], gone: Any
) -> None:
    with pytest.raises(ValueError, match="disappeared"):
        module["capture_tags"](Native([gone]), deadline=FAR)


def test_capture_tags_when_names_or_tags_unusable_then_skipped_with_reason(
    module: dict[str, Any],
) -> None:
    native = Native([
        Glyph("good", None), Glyph(7), Glyph(""), Glyph("a b"), Glyph("a/b"),
        Glyph("nul\0"), Glyph("badtags", ["x", 3]), Glyph("tagged", ("t",)),
    ])
    rows, skipped = module["capture_tags"](native, deadline=FAR)
    assert rows == (("good", ()), ("tagged", ("t",))), "None tags read as empty"
    assert len(skipped) == 6 and all(line.startswith("Skipped ") for line in skipped)
    assert "name cannot form a slash proof" in skipped[0] and "7" in skipped[0]
    assert "NUL" in skipped[4] and "unreadable tags" in skipped[5]


def test_capture_tags_when_deadline_passes_after_walk_then_no_partial_result(
    module: dict[str, Any], monkeypatch: Any
) -> None:
    ticks = iter([0.0, 5.0])
    monkeypatch.setitem(module["capture_tags"].__globals__, "monotonic", lambda: next(ticks))
    with pytest.raises(TimeoutError, match="no partial result"):
        module["capture_tags"](Native([Glyph("A")]), deadline=1.0)


def test_capture_tags_when_default_deadline_then_two_second_budget(
    module: dict[str, Any], monkeypatch: Any
) -> None:
    clock = iter([100.0, 103.0])
    monkeypatch.setitem(module["capture_tags"].__globals__, "monotonic", lambda: next(clock))
    with pytest.raises(TimeoutError):
        module["capture_tags"](Native([Glyph("A")]))


def test_capture_tags_when_font_changes_during_scan_then_refresh_requested(
    module: dict[str, Any],
) -> None:
    with pytest.raises(ValueError, match="Current font changed"):
        module["capture_tags"](Native([Glyph("A")], flips=True), deadline=FAR)


def test_search_result_when_terms_given_then_all_must_match_name_or_tags(
    module: dict[str, Any], monkeypatch: Any
) -> None:
    rows = (("arrow_left", ("Arrow", "direction")), ("circle", ("shape",)), ("arrow", ()))
    monkeypatch.setitem(module["search_result"].__globals__, "capture_tags",
                        lambda: (rows, ("Skipped 'x': y",)))
    text, skipped = module["search_result"](("ARROW  direction",))
    assert text == "/arrow_left" and skipped == ("Skipped 'x': y",)
    assert module["search_result"](("shape circle",))[0] == "/circle"
    assert module["build_output"](("arrow",)) == "/arrow_left/arrow"
    assert module["search_result"](("nothing",))[0] == ""


def test_checked_when_text_has_forbidden_character_then_refuses(module: dict[str, Any]) -> None:
    assert module["checked"]("fine é") == "fine é"
    for bad in ("\0", " ", " ", " ", "\r"):
        with pytest.raises(ValueError, match="NUL, NBSP"):
            module["checked"]("a" + bad)
    with pytest.raises(ValueError, match="surrogate"):
        module["checked"]("\ud800")


def build(module: dict[str, Any], env: NS, found: Any = ("/A/B", ())) -> Any:
    def fake(fields: tuple[str, ...]) -> Any:
        if isinstance(found, Exception):
            raise found
        return found

    module["search_result"].__globals__["search_result"] = fake
    return module["show"](env.qt, None)


def test_show_when_built_then_refreshes_once_and_registers_panel(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env, ("/A", ("Skipped 'q': r",)))
    assert module["_PANELS"] == [panel] and panel.shown == 1
    assert panel.output_box.plainText() == "/A"
    assert panel.status_line.text().endswith("Skipped 'q': r")


def test_refresh_output_when_search_refused_then_output_cleared_and_message_shown(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env, TimeoutError("Font tag scan expired; no partial result."))
    assert panel.output_box.plainText() == ""
    assert panel.status_line.text() == "Font tag scan expired; no partial result."


def test_copy_output_when_matches_then_clipboard_and_status_updated(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env, ("/A/B", ("Skipped 'q': r",)))
    panel.signal_scope.pairs[1][0].emit()
    assert env.qt.clipboard.text() == "/A/B"
    assert panel.status_line.text() == "Fresh result copied.\nSkipped 'q': r"


def test_copy_output_when_nothing_matches_then_clipboard_untouched(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env, ("", ()))
    env.qt.clipboard.setText("keep")
    panel.copy_output()
    assert env.qt.clipboard.text() == "keep"
    assert panel.status_line.text() == "No matching output to copy."
    assert panel.output_box.plainText() == ""


def test_refresh_button_when_clicked_then_output_replaced(module: dict[str, Any], env: NS) -> None:
    panel = build(module, env, ("/A", ()))
    panel.output_box.setPlainText("stale")
    panel.signal_scope.pairs[0][0].emit()
    assert panel.output_box.plainText() == "/A"


def test_show_when_choice_field_configured_then_combo_value_is_searched(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    monkeypatch.setitem(module["CHOICES"], 0, ("", "alpha"))
    seen: list[tuple[str, ...]] = []

    def record(fields: tuple[str, ...]) -> Any:
        seen.append(fields)
        return "", ()

    module["search_result"].__globals__["search_result"] = record
    panel = module["show"](env.qt, None)
    panel.input_boxes[0].setCurrentIndex(1)
    panel.refresh_output()
    assert seen == [("",), ("alpha",)]


def test_destroyed_signal_when_emitted_then_panel_unregistered(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.signal_scope.pairs[2][0].emit()
    assert module["_PANELS"] == []
    panel.release_owner()
    assert module["_PANELS"] == []


def test_close_event_when_disconnect_refused_then_kept_until_retry(
    module: dict[str, Any], env: NS
) -> None:
    panel = build(module, env)
    panel.signal_scope.refuse = True
    event = Event()
    panel.closeEvent(event)
    assert event.ignored and not panel.deleted and module["_PANELS"] == [panel]
    panel.signal_scope.refuse = False
    event = Event()
    panel.closeEvent(event)
    assert event.accepted and panel.deleted and module["_PANELS"] == []
    panel.closeEvent(Event())  # already unregistered: still accepted
    assert module["_PANELS"] == []


def test_show_when_panel_show_fails_then_removed_when_clean_and_kept_when_refused(
    module: dict[str, Any], env: NS, monkeypatch: Any
) -> None:
    class Failing(Widget):
        show_error = RuntimeError("cannot show")

    qt = make_qt(Failing)
    install_fly(monkeypatch, qt)
    with pytest.raises(RuntimeError, match="cannot show"):
        module["show"](qt, None)
    assert module["_PANELS"] == [], "cleanly disconnected panel is dropped"
    monkeypatch.setattr(_cov_support.Scope, "refuse_default", True)
    with pytest.raises(RuntimeError, match="cannot show"):
        module["show"](qt, None)
    assert len(module["_PANELS"]) == 1, "an undisconnectable panel stays registered"


def test_main_when_window_available_then_panel_opens(module: dict[str, Any], env: NS) -> None:
    module["main"]()
    assert len(module["_PANELS"]) == 1


@pytest.mark.parametrize("error", [ValueError("no window"), RuntimeError("busy"),
                                   TimeoutError("slow")])
def test_main_when_show_refused_then_message_printed(
    module: dict[str, Any], env: NS, capsys: Any, error: Exception
) -> None:
    def fail() -> Any:
        raise error

    env.fly.root.fl = NS(MainWindow=fail)
    module["main"]()
    assert capsys.readouterr().out == f"Symbol Tag Search: {error}\n"


def test_script_when_run_as_main_then_main_executes(env: NS, capsys: Any) -> None:
    env.fly.root.fl = NS(MainWindow=lambda: (_ for _ in ()).throw(ValueError("no window")))
    runpy.run_path(str(SCRIPT), run_name="__main__")
    assert "Symbol Tag Search: no window" in capsys.readouterr().out
