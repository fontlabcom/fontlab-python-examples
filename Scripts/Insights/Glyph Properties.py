# this_file: Scripts/Insights/Glyph Properties.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/Belsepubi_naali/bin/pymodules/core/componentpropertyadder.py:53 — source licence unresolved; see catalog/insights.json.
"""Demonstrate glyph properties with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Synthetic glyph — Qt properties", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        label = gui.QLabel("A: default", window)
        button = gui.QPushButton("Toggle glyph role", window)
        layout = gui.QVBoxLayout(window)
        layout.addWidget(label)
        layout.addWidget(button)
        label.setProperty("glyphRole", "default")

        def toggle() -> None:
            role = (
                "alternate"
                if str(label.property("glyphRole")) == "default"
                else "default"
            )
            label.setProperty("glyphRole", role)
            label.setText(f"A: {role}")

        handle.connect_old(button, "clicked()", toggle)
        handle.controls.update(button=button, label=label)
        handle.inspect_ui = lambda: {
            "glyph_role": str(label.property("glyphRole")),
            "text": str(S.value(label, "text")),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_glyph-properties", "Glyph Properties")


if __name__ == "__main__":
    main()
