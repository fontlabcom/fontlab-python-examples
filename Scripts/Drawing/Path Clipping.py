# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Path Clipping.py
"""What: Clip coloured stripes to a rounded path with a circular cutout.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Path Clipping'
KEY = 'drawing_path_clipping'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    clip = gui.QPainterPath()
    clip.addRoundedRect(core.QRectF(65.0, 45.0, 370.0, 250.0), 40.0, 40.0)
    clip.addEllipse(core.QRectF(180.0, 105.0, 140.0, 140.0))
    clip.setFillRule(core.Qt.OddEvenFill)
    p.setClipPath(clip)
    for index in range(20):
        colour = gui.QColor.fromHsv(index * 18, 150, 220)
        p.fillRect(core.QRectF(index * 25.0, 0.0, 25.0, 350.0), colour)
    p.setClipping(False)
    p.drawPath(clip)


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
