# this_file: ports/insights/contour-canvas.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/kateliev_TypeRig/Scripts/TypeRig Tools/TR-DeltaPreview.py:21 — source licence unresolved; see catalog/insights.json.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui

    class Canvas(gui.QWidget):
        """Draw an owned synthetic contour; FontLab shapes are never used."""

        def paintEvent(self, event: Any) -> None:
            gui.QWidget.paintEvent(self, event)
            painter = gui.QPainter(self)
            try:
                painter.setRenderHint(gui.QPainter.Antialiasing, True)
                painter.drawPath(self.path)
                self.paint_count += 1
            finally:
                painter.end()

    with owned(Canvas(), "Synthetic contour — QPainterPath") as handle:
        canvas = handle.widget
        canvas.paint_count = 0
        canvas.path = gui.QPainterPath()
        canvas.path.moveTo(60.0, 210.0)
        canvas.path.lineTo(60.0, 90.0)
        canvas.path.cubicTo(60.0, 25.0, 230.0, 25.0, 230.0, 90.0)
        canvas.path.lineTo(230.0, 210.0)
        canvas.path.closeSubpath()
        handle.release.append(lambda: setattr(canvas, "path", None))
        handle.inspect_ui = lambda: {
            "paint_count": canvas.paint_count,
            "path_elements": canvas.path.elementCount(),
            "synthetic": True,
        }
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("contour-canvas")
