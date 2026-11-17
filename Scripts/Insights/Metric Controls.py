# this_file: Scripts/Insights/Metric Controls.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/kateliev_TypeRig/Lib/typerig/proxy/fl/gui/widgets.py:327 — source licence unresolved; see catalog/insights.json.
"""Demonstrate metric controls with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with S.Session(qt, "Sample advance — synchronized controls", gui.QWidget()) as session:
        handle = session.h
        window = handle.widget
        spin = gui.QSpinBox(window)
        slider = gui.QSlider(qt.QtCore.Qt.Horizontal, window)
        layout = gui.QVBoxLayout(window)
        for control in (spin, slider):
            control.setRange(0, 2000)
            control.setValue(600)
            layout.addWidget(control)
        state = {"updates": 0}

        def mirror(target: Any, value: int) -> None:
            previous = target.blockSignals(True)
            try:
                target.setValue(value)
                state["updates"] += 1
            finally:
                target.blockSignals(previous)

        handle.connect(spin.valueChanged, lambda value: mirror(slider, value))
        handle.connect(slider.valueChanged, lambda value: mirror(spin, value))
        handle.controls.update(spin=spin, slider=slider)
        handle.inspect_ui = lambda: {
            "spin": int(S.value(spin, "value")),
            "slider": int(S.value(slider, "value")),
            **state,
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_metric-controls", "Metric Controls")


if __name__ == "__main__":
    main()
