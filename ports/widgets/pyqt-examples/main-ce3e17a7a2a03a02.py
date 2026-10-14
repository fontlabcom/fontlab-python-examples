# this_file: ports/widgets/pyqt-examples/main-ce3e17a7a2a03a02.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/01 PyQt QLabel/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Original Hello World QLabel, using FontLab's existing application loop."""

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    label = qt.QtGui.QLabel("Hello World!")
    return ExampleHandle(label, lambda: {"text": str(label.text)})


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("ce3e17a7a2a03a02")
