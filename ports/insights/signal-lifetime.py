# this_file: ports/insights/signal-lifetime.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/jcfr_PythonQt/examples/PyGettingStarted/GettingStarted.py:21 — source licence unresolved; see catalog/insights.json.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with owned(gui.QWidget(), "Advance preview — tracked signals") as handle:
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
        handle.inspect_ui = lambda: {**state, "text": str(label.text)}
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("signal-lifetime")
