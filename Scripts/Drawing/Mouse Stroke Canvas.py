# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Mouse Stroke Canvas.py
"""What: Draw freehand strokes with the left mouse button on a small canvas.
Usage: Drag to draw; right-click to clear. The drawing is not saved.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is needed or changed. Paths belong only to this window.
"""

from typing import Any


def panel_type(core: Any, gui: Any) -> type:
    """Keep strokes on a Python widget subclass, not a native wrapper."""
    class Canvas(gui.QWidget):
        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.setWindowTitle("Mouse Stroke Canvas — right-click to clear")
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.setAttribute(core.Qt.WA_DeleteOnClose, True)
            self.setFixedSize(500, 350)
            self.stroke_path = gui.QPainterPath()
            self.drawing_stroke = False

        def mousePressEvent(self, event: Any) -> None:
            try:
                if event.button() == core.Qt.RightButton:
                    self.stroke_path = gui.QPainterPath()
                    self.drawing_stroke = False
                elif event.button() == core.Qt.LeftButton:
                    self.stroke_path.moveTo(core.QPointF(event.pos()))
                    self.drawing_stroke = True
                self.update()
            except Exception as error:
                print(f"Mouse Stroke Canvas: {error}")

        def mouseMoveEvent(self, event: Any) -> None:
            try:
                if self.drawing_stroke:
                    self.stroke_path.lineTo(core.QPointF(event.pos()))
                    self.update()
            except Exception as error:
                self.drawing_stroke = False
                print(f"Mouse Stroke Canvas: {error}")

        def mouseReleaseEvent(self, event: Any) -> None:
            self.drawing_stroke = False

        def paintEvent(self, event: Any) -> None:
            painter = gui.QPainter(self)
            try:
                painter.fillRect(core.QRectF(0.0, 0.0, 500.0, 350.0), gui.QColor("white"))
                painter.setRenderHint(gui.QPainter.Antialiasing, True)
                pen = gui.QPen(gui.QColor("#235e96"))
                pen.setWidthF(3.0)
                pen.setCapStyle(core.Qt.RoundCap)
                pen.setJoinStyle(core.Qt.RoundJoin)
                painter.setPen(pen)
                painter.drawPath(self.stroke_path)
            except Exception as error:
                print(f"Mouse Stroke Canvas: {error}")
            finally:
                painter.end()

    return Canvas


def main() -> Any:
    from PythonQt import QtCore, QtGui
    import fly.ap.core.scripting as scripting

    return scripting.show_script_dialog(panel_type(QtCore, QtGui), "drawing_mouse_stroke_canvas")


if __name__ == "__main__":
    main()
