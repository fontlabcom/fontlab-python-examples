# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Radial Gradient Light.py
"""What: Move the focal point inside three radial gradients to suggest lighting.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Radial Gradient Light'
KEY = 'drawing_radial_gradient_light'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for index, offset in enumerate((-35.0, 0.0, 35.0)):
        x = 85.0 + index * 155.0
        gradient = gui.QRadialGradient(x, 175.0, 65.0, x + offset, 145.0)
        gradient.setColorAt(0.0, gui.QColor("#ffffff"))
        gradient.setColorAt(0.3, gui.QColor("#7bc9ed"))
        gradient.setColorAt(1.0, gui.QColor("#183c73"))
        p.setBrush(gui.QBrush(gradient))
        p.drawEllipse(core.QRectF(x - 65.0, 110.0, 130.0, 130.0))


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
