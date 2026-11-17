# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Picture Recording.py
"""What: Record vector drawing commands in QPicture and replay them at two scales.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Picture Recording'
KEY = 'drawing_picture_recording'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    picture = gui.QPicture()
    recorder = gui.QPainter(picture)
    try:
        recorder.setPen(gui.QPen(gui.QColor("#315e73")))
        recorder.setBrush(gui.QBrush(gui.QColor("#8bc8c2")))
        recorder.drawRoundedRect(core.QRectF(0.0, 0.0, 100.0, 100.0), 20.0, 20.0)
        recorder.drawLine(core.QPointF(20.0, 75.0), core.QPointF(80.0, 25.0))
    finally:
        recorder.end()
    p.drawPicture(core.QPointF(35.0, 110.0), picture)
    p.save()
    p.translate(240.0, 65.0)
    p.scale(2.0, 2.0)
    p.drawPicture(core.QPointF(0.0, 0.0), picture)
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
