# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Path Stroke Outline.py
"""What: Convert an open curve stroke into a filled outline using QPainterPathStroker.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Path Stroke Outline'
KEY = 'drawing_path_stroke_outline'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    path = gui.QPainterPath(core.QPointF(40.0, 240.0))
    path.cubicTo(100.0, 20.0, 390.0, 20.0, 460.0, 240.0)
    stroker = gui.QPainterPathStroker()
    stroker.setWidth(35.0)
    stroker.setCapStyle(core.Qt.RoundCap)
    outline = stroker.createStroke(path)
    p.fillPath(outline, gui.QBrush(gui.QColor("#a6d6d8")))
    p.setPen(gui.QColor("#226577"))
    p.drawPath(outline)
    p.setPen(gui.QColor("#d56843"))
    p.drawPath(path)
    p.drawText(core.QPointF(85.0, 300.0), "Filled stroke boundary and original centreline")


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
