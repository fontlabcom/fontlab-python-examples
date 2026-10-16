# this_file: ports/insights/glyph-properties.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/Belsepubi_naali/bin/pymodules/core/componentpropertyadder.py:53 — source licence unresolved; see catalog/insights.json.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with owned(gui.QWidget(), "Synthetic glyph — Qt properties") as handle:
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
            label.text = f"A: {role}"

        handle.connect_old(button, "clicked()", toggle)
        handle.controls.update(button=button, label=label)
        handle.inspect_ui = lambda: {
            "glyph_role": str(label.property("glyphRole")),
            "text": str(label.text),
        }
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("glyph-properties")
