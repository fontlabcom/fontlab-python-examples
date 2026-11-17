# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Antialiasing Comparison.py
"""What: Compare identical small curves and diagonals with antialiasing off and on.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Antialiasing Comparison'
KEY = 'drawing_antialiasing_comparison'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for index, enabled in enumerate((False, True)):
        p.save()
        p.translate(30.0 + index * 250.0, 65.0)
        p.setRenderHint(gui.QPainter.Antialiasing, enabled)
        p.setPen(gui.QPen(gui.QColor("#24445b")))
        for offset in range(0, 90, 9):
            p.drawEllipse(core.QRectF(float(offset), float(offset), 100.0, 100.0))
        p.drawLine(core.QPointF(0.0, 190.0), core.QPointF(180.0, 10.0))
        p.drawText(core.QPointF(0.0, 230.0), "Antialiasing on" if enabled else "Antialiasing off")
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
