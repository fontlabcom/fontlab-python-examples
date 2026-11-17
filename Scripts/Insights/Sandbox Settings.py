# this_file: Scripts/Insights/Sandbox Settings.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/RobotLocomotion_director/src/python/director/robotposegui.py:610 — source licence unresolved; see catalog/insights.json.
"""Demonstrate sandbox settings with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui, core = qt.QtGui, qt.QtCore
    key = "proof/sample"
    with S.Session(qt, "Owned proof sample — isolated settings", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        settings = core.QSettings(str(session.temp() / "sample.ini"), core.QSettings.IniFormat, window)
        settings.setFallbacksEnabled(False)
        editor = gui.QLineEdit(window)
        editor.setText(str(settings.value(key, "Hamburgefontsiv")))
        save = gui.QPushButton("Save sample", window)
        reset = gui.QPushButton("Reset owned sample", window)
        label = gui.QLabel("Temporary INI file; removed when this example closes", window)
        layout = gui.QVBoxLayout(window)
        for control in (editor, save, reset, label):
            layout.addWidget(control)
        state = {"error": ""}

        def persist(remove: bool = False) -> None:
            if remove:
                settings.remove(key)
                editor.setText("Hamburgefontsiv")
            else:
                settings.setValue(key, str(S.value(editor, "text")))
            settings.sync()
            state["error"] = (
                "Settings write failed"
                if settings.status() != core.QSettings.NoError
                else ""
            )
            label.setText(state["error"] or ("Reset" if remove else "Saved"))

        handle.connect_old(save, "clicked()", persist)
        handle.connect_old(reset, "clicked()", lambda: persist(True))
        handle.controls.update(input=editor, save=save, reset=reset)
        handle.inspect_ui = lambda: {
            "sample": str(S.value(editor, "text")),
            "saved": str(settings.value(key, "Hamburgefontsiv")),
            "settings_file": str(settings.fileName()),
            "temporary": True,
            **state,
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_sandbox-settings", "Sandbox Settings")


if __name__ == "__main__":
    main()
