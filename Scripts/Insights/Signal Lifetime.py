# this_file: Scripts/Insights/Signal Lifetime.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/jcfr_PythonQt/examples/PyGettingStarted/GettingStarted.py:21 — source licence unresolved; see catalog/insights.json.
"""Demonstrate signal lifetime with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Advance preview — tracked signals", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        layout = gui.QVBoxLayout(window)
        label = gui.QLabel("Advance: 600", window)
        button = gui.QPushButton("Add 10 units", window)
        layout.addWidget(label)
        layout.addWidget(button)
        state = {"advance": 600, "clicks": 0}

        def increment() -> None:
            state["advance"] += 10
            state["clicks"] += 1
            label.setText(f"Advance: {state['advance']}")

        handle.connect_old(button, "clicked()", increment)
        handle.controls.update(button=button, label=label)
        handle.inspect_ui = lambda: {**state, "text": str(S.value(label, "text"))}
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_signal-lifetime", "Signal Lifetime")


if __name__ == "__main__":
    main()
