# this_file: ports/widgets/pyqt-examples/main-a33bb8c2dce4e115.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/09 Qt dark theme/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from pathlib import Path
from typing import Any

from fontlab_python_examples.editor import apply_style, build_editor
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    text = gui.QPlainTextEdit()
    handle = build_editor(
        qt, text, Path(__file__).with_name("icon-3f05f5f2d0cc6df2.svg")
    )
    style = gui.QStyleFactory.create("Fusion")
    style.setParent(handle.widget)
    apply_style(handle.widget, style)
    palette = gui.QPalette()
    for role, color in (
        (gui.QPalette.Window, gui.QColor(53, 53, 53)),
        (gui.QPalette.WindowText, qt.QtCore.Qt.white),
        (gui.QPalette.Base, gui.QColor(25, 25, 25)),
        (gui.QPalette.AlternateBase, gui.QColor(53, 53, 53)),
        (gui.QPalette.ToolTipBase, qt.QtCore.Qt.white),
        (gui.QPalette.ToolTipText, qt.QtCore.Qt.white),
        (gui.QPalette.Text, qt.QtCore.Qt.white),
        (gui.QPalette.Button, gui.QColor(53, 53, 53)),
        (gui.QPalette.ButtonText, qt.QtCore.Qt.white),
        (gui.QPalette.BrightText, qt.QtCore.Qt.red),
        (gui.QPalette.Link, gui.QColor(42, 130, 218)),
        (gui.QPalette.Highlight, gui.QColor(42, 130, 218)),
        (gui.QPalette.HighlightedText, qt.QtCore.Qt.black),
    ):
        palette.setColor(role, color)
    handle.widget.setPalette(palette)
    text.setPalette(palette)
    inspect_editor = handle.inspect_ui
    handle.inspect_ui = lambda: {
        **inspect_editor(),
        "theme": "Fusion dark",
        "window_color": str(handle.widget.palette.color(gui.QPalette.Window).name()),
    }
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("a33bb8c2dce4e115")
