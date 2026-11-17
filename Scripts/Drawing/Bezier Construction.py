# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Bezier Construction.py
"""What: Draw a cubic Bezier together with its control polygon and handles.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Bezier Construction'
KEY = 'drawing_bezier_construction'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    points = (core.QPointF(40.0, 270.0), core.QPointF(90.0, 30.0), core.QPointF(400.0, 40.0), core.QPointF(460.0, 270.0))
    p.setPen(gui.QPen(gui.QColor("#9aa7b4")))
    for start, end in zip(points, points[1:]):
        p.drawLine(start, end)
    path = gui.QPainterPath(points[0])
    path.cubicTo(*points[1:])
    pen = gui.QPen(gui.QColor("#235e96"))
    pen.setWidthF(5.0)
    p.setPen(pen)
    p.drawPath(path)
    p.setBrush(gui.QBrush(gui.QColor("#eb8656")))
    for point in points:
        p.drawEllipse(point, 6.0, 6.0)


def panel_type(core: Any, gui: Any) -> type:
    """Bind the example to the host Qt without creating an application."""
    class Canvas(gui.QWidget):
        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.setAttribute(core.Qt.WA_DeleteOnClose, True)
            self.setFixedSize(500, 350)

        def paintEvent(self, event: Any) -> None:
            painter = gui.QPainter(self)
            try:
                painter.fillRect(core.QRectF(0.0, 0.0, 500.0, 350.0), gui.QColor("white"))
                painter.setRenderHint(gui.QPainter.Antialiasing, True)
                painter.setPen(gui.QColor("#283747"))
                draw(painter, core, gui)
            except Exception as error:  # Never unwind through a native paint callback.
                print(f"{TITLE}: {error}")
            finally:
                painter.end()

    return Canvas


def main() -> Any:
    """Let App parent and retain the modeless window across script runs."""
    from PythonQt import QtCore, QtGui
    import fly.ap.core.scripting as scripting

    return scripting.show_script_dialog(panel_type(QtCore, QtGui), KEY)


if __name__ == "__main__":
    main()
