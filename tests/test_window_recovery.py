# this_file: tests/test_window_recovery.py
"""Exercise the actual dock controller against retryable shared ownership."""

import pytest

from test_issue122_E6 import TITLES, load
from test_issue122_E6 import host as host


@pytest.mark.parametrize("ending", ["retry", "parent-destruction"])
def test_dock_refused_native_close_keeps_exact_owner_for_retry_or_parent_death(host, monkeypatch, ending):
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)
    dock, content = panel.owned.widget, panel.owned.content
    original = type(dock).close
    monkeypatch.setattr(type(dock), "close", lambda self: False)
    assert panel.close_owned() is False, "A native refusal must not be reported as cleanup success"
    assert panel in module["_PANELS"] and panel.owned.widget is dock and not dock.deleted
    assert "refused" in panel.status_line.text().lower()
    assert not panel.close_owned() and panel in module["_PANELS"], "Repeated refusal retains one owner"
    if ending == "retry":
        monkeypatch.setattr(type(dock), "close", original)
        assert panel.close_owned() and dock.deleted and panel.owned.closed
    else:
        dock.destroyed.emit()
        content.destroyed.emit()
        assert panel.owned.closed and panel.owned.widget is None
        assert panel.close_owned(), "Do not touch a dead wrapper after parent destruction"
    assert panel not in module["_PANELS"]


def test_dock_failed_unregistration_can_complete_without_destroying_parent(host, monkeypatch):
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)
    dock = panel.owned.widget
    original = type(host.parent).removeDockWidget
    calls = []

    def refused(parent, target):
        calls.append(target)
        raise RuntimeError("owned removal refused")

    monkeypatch.setattr(type(host.parent), "removeDockWidget", refused)
    assert not panel.close_owned() and panel.owned.widget is dock
    assert not panel.close_owned() and calls == [dock, dock], "Retry the unfinished native stage"
    monkeypatch.setattr(type(host.parent), "removeDockWidget", original)
    assert panel.close_owned() and dock.deleted and panel.owned.closed
    assert panel not in module["_PANELS"]


@pytest.mark.parametrize("visible", [False, True])
def test_dock_floating_transition_requests_priority_and_preserves_model_and_content(host, visible):
    module = load(TITLES[0])
    host.parent.local_visible = visible
    panel = module["show"](host.qt, host.parent)
    dock, content, model = panel.owned.widget, panel.owned.content, panel.data_model
    dock.setFloating(True)
    assert dock.windowFlags() & host.qt.QtCore.Qt.WindowStaysOnTopHint
    assert dock.local_widget is content and panel.data_model is model
    assert panel.issue_snapshot == module["issue_rows"](host.state.rows)
    assert panel.close_owned() and dock.deleted
