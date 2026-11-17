# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Painter Transform Gallery.py
"""What: Compare rotation, scale and shear with a fixed source rectangle.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Painter Transform Gallery'
KEY = 'drawing_painter_transform_gallery'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for index in range(3):
        p.save()
        p.translate(85.0 + index * 165.0, 170.0)
        if index == 0:
            p.rotate(30.0)
        elif index == 1:
            p.scale(0.65, 1.5)
        else:
            p.shear(0.5, 0.0)
        p.setBrush(gui.QBrush(gui.QColor("#63b5ae")))
        p.drawRect(core.QRectF(-45.0, -45.0, 90.0, 90.0))
        p.restore()
    for index, label in enumerate(("Rotate 30°", "Scale", "Shear")):
        p.drawText(core.QPointF(40.0 + index * 165.0, 290.0), label)


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
