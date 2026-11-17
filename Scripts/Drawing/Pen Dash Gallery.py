# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Pen Dash Gallery.py
"""What: Compare solid, dashed, dotted and custom dash patterns.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Pen Dash Gallery'
KEY = 'drawing_pen_dash_gallery'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for row, style in enumerate((core.Qt.SolidLine, core.Qt.DashLine, core.Qt.DotLine, core.Qt.DashDotLine, core.Qt.DashDotDotLine)):
        pen = gui.QPen(gui.QColor("#265c8e"))
        pen.setWidthF(4.0)
        pen.setStyle(style)
        p.setPen(pen)
        p.drawLine(core.QPointF(35.0, 45.0 + row * 48.0), core.QPointF(465.0, 45.0 + row * 48.0))
    pen.setDashPattern([5.0, 2.0, 1.0, 2.0])
    p.setPen(pen)
    p.drawLine(core.QPointF(35.0, 300.0), core.QPointF(465.0, 300.0))


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
