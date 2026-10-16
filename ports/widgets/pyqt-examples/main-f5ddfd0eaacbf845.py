# this_file: ports/widgets/pyqt-examples/main-f5ddfd0eaacbf845.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/03 QVBoxLayout PyQt6/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Original two buttons, arranged Top then Bottom in QVBoxLayout."""

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    window = qt.QtGui.QWidget()
    buttons = []
    handle = ExampleHandle(
        window, lambda: {"buttons": [str(item.text) for item in buttons]}
    )
    try:
        layout = qt.QtGui.QVBoxLayout(window)
        for text in ("Top", "Bottom"):
            button = qt.QtGui.QPushButton(text, window)
            buttons.append(button)
            layout.addWidget(button)
    except BaseException:
        handle.close()
        raise
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("f5ddfd0eaacbf845")
