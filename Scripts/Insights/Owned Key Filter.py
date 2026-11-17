# this_file: Scripts/Insights/Owned Key Filter.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/RobotLocomotion_director/docs/sphinx/tutorials/robot/normalSelectionWidget.py:28 — source licence unresolved; see catalog/insights.json.
"""Demonstrate owned key filter with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui, core = qt.QtGui, qt.QtCore

    class KeyObserver(qt.private.QObject):
        """Observe keys only in one owned input, without consuming events."""

        def eventFilter(self, watched: Any, event: Any) -> bool:
            if watched is self.target and event.type() == core.QEvent.KeyPress:
                self.keys.append(str(event.text()))
                del self.keys[:-20]
                self.label.setText("Keys: " + " · ".join(self.keys))
            return False

        def release(self) -> None:
            self.target = self.label = None

    with S.Session(qt, "Owned glyph-name key observer", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        editor = gui.QLineEdit(window)
        editor.setPlaceholderText("Type a glyph name here")
        label = gui.QLabel("Keys: ", window)
        layout = gui.QVBoxLayout(window)
        layout.addWidget(editor)
        layout.addWidget(label)
        observer = KeyObserver(window)
        observer.target, observer.label, observer.keys = editor, label, []
        handle.release.append(observer.release)
        handle.cleanup.append(
            lambda: (
                editor.removeEventFilter(observer) if not handle.owner.closed else None
            )
        )
        editor.installEventFilter(observer)
        handle.controls.update(editor=editor, filter=observer, label=label)
        handle.inspect_ui = lambda: {
            "keys": list(observer.keys),
            "text": str(S.value(editor, "text")),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_owned-key-filter", "Owned Key Filter")


if __name__ == "__main__":
    main()
