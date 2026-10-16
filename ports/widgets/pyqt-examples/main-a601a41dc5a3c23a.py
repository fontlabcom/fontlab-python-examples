# this_file: ports/widgets/pyqt-examples/main-a601a41dc5a3c23a.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/07 Qt Text Editor/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from pathlib import Path
from typing import Any

from fontlab_python_examples.editor import build_editor
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    text = gui.QPlainTextEdit()
    handle = build_editor(
        qt, text, Path(__file__).with_name("icon-adeb6eaa0049d0d3.svg")
    )
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("a601a41dc5a3c23a")
