# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Path Fill Rules.py
"""What: Compare odd-even and winding fills for nested same-direction contours.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Path Fill Rules'
KEY = 'drawing_path_fill_rules'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for index, (rule, label) in enumerate(((core.Qt.OddEvenFill, "Odd-even"), (core.Qt.WindingFill, "Winding"))):
        path = gui.QPainterPath()
        path.addEllipse(core.QRectF(30.0 + index * 250.0, 55.0, 190.0, 190.0))
        path.addEllipse(core.QRectF(75.0 + index * 250.0, 100.0, 100.0, 100.0))
        path.setFillRule(rule)
        p.fillPath(path, gui.QBrush(gui.QColor("#398d9a")))
        p.drawText(core.QPointF(75.0 + index * 250.0, 290.0), label)


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
