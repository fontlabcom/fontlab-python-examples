# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Text Along A Curve.py
"""What: Place individual system-font characters along a Bezier tangent.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Text Along A Curve'
KEY = 'drawing_text_along_a_curve'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    path = gui.QPainterPath(core.QPointF(35.0, 260.0))
    path.cubicTo(120.0, 20.0, 330.0, 20.0, 465.0, 240.0)
    p.setPen(gui.QColor("#c2ced7"))
    p.drawPath(path)
    p.setFont(gui.QFont("Sans Serif", 18))
    p.setPen(gui.QColor("#235e96"))
    text = "Drawing along a curve"
    for index, letter in enumerate(text):
        fraction = (index + 0.5) / len(text)
        point = path.pointAtPercent(fraction)
        p.save()
        p.translate(point)
        p.rotate(-path.angleAtPercent(fraction))
        p.drawText(core.QPointF(0.0, 0.0), letter)
        p.restore()


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
