# this_file: ports/multimedia/pyqt-examples/main-1151b1cb878f192a.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/10 QPainter Python example/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from pathlib import Path
from typing import Any

from fontlab_python_examples.editor import build_editor
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui

    class PlainTextEdit(gui.QPlainTextEdit):
        def __init__(self) -> None:
            super().__init__()
            self.holes = []
            self.bullet = gui.QPixmap(
                str(Path(__file__).with_name("bullet-accab87abcc10bea.png"))
            )
            size = self.bullet.size()
            self.offset = qt.QtCore.QPoint(size.width() // 2, size.height() // 2)

        def mousePressEvent(self, event: Any) -> None:
            self.holes.append(event.pos())
            super().mousePressEvent(event)
            self.viewport().update()

        def paintEvent(self, event: Any) -> None:
            super().paintEvent(event)
            painter = gui.QPainter(self.viewport())
            try:
                for hole in self.holes:
                    painter.drawPixmap(hole - self.offset, self.bullet)
            finally:
                painter.end()

    text = PlainTextEdit()
    text.setPlainText("Click with the mouse below to shoot ;-)")
    handle = build_editor(
        qt, text, Path(__file__).with_name("icon-6988c3833303e9d8.svg")
    )
    inspect_editor = handle.inspect_ui
    handle.inspect_ui = lambda: {
        **inspect_editor(),
        "hole_count": len(text.holes),
        "holes": [[point.x(), point.y()] for point in text.holes],
        "bullet_loaded": not text.bullet.isNull(),
        "sound_supported": False,
    }
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("1151b1cb878f192a")
