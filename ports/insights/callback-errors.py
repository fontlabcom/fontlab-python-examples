# this_file: ports/insights/callback-errors.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/RobotLocomotion_director/src/python/director/asynctaskqueue.py:72 — source licence unresolved; see catalog/insights.json.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with owned(gui.QWidget(), "Sample advance — callback errors") as handle:
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
                advance = int(str(editor.text))
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
        handle.inspect_ui = lambda: {**state, "text": str(label.text)}
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("callback-errors")
