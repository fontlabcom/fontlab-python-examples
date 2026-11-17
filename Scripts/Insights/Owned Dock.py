# this_file: Scripts/Insights/Owned Dock.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/RobotLocomotion_director/src/python/director/applogic.py:78 — source licence unresolved; see catalog/insights.json.
"""Demonstrate owned dock with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Owned metrics workspace", gui.QMainWindow()) as session:
        handle = session.h
        window = handle.widget
        toggle = gui.QPushButton("Show / hide sample metrics", window)
        window.setCentralWidget(toggle)
        dock = gui.QDockWidget("Sample glyph metrics", window)
        label = gui.QLabel("A: advance 600, LSB 40", dock)
        dock.setWidget(label)
        window.addDockWidget(qt.QtCore.Qt.RightDockWidgetArea, dock)

        def toggle_dock() -> None:
            dock.setVisible(not dock.isVisible())

        handle.connect_old(toggle, "clicked()", toggle_dock)
        handle.controls.update(toggle=toggle, dock=dock)
        handle.inspect_ui = lambda: {
            "dock_visible": bool(dock.isVisible()),
            "metrics": str(S.value(label, "text")),
            "scope": "owned main window",
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_owned-dock", "Owned Dock")


if __name__ == "__main__":
    main()
