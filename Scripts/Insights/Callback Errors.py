# this_file: Scripts/Insights/Callback Errors.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/RobotLocomotion_director/src/python/director/asynctaskqueue.py:72 — source licence unresolved; see catalog/insights.json.
"""Demonstrate callback errors with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Sample advance — callback errors", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        editor = gui.QLineEdit(window)
        editor.setText("600")
        apply = gui.QPushButton("Apply sample advance (0–2000)", window)
        label = gui.QLabel("Advance: 600", window)
        layout = gui.QVBoxLayout(window)
        for control in (editor, apply, label):
            layout.addWidget(control)
        state = {"advance": 600, "error": ""}

        def update() -> None:
            try:
                advance = int(str(S.value(editor, "text")))
                if not 0 <= advance <= 2000:
                    raise ValueError("Advance must be between 0 and 2000")
            except ValueError:
                state["error"] = "Enter an integer from 0 to 2000"
                label.setText(state["error"])
                return
            state.update(advance=advance, error="")
            label.setText(f"Advance: {advance}")

        handle.connect_old(apply, "clicked()", update)
        handle.controls.update(input=editor, apply=apply)
        handle.inspect_ui = lambda: {**state, "text": str(S.value(label, "text"))}
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_callback-errors", "Callback Errors")


if __name__ == "__main__":
    main()
