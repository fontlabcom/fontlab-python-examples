# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Linear Gradient Swatches.py
"""What: Compare horizontal, vertical and diagonal linear colour blends.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Linear Gradient Swatches'
KEY = 'drawing_linear_gradient_swatches'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for row, end in enumerate(((420.0, 0.0), (0.0, 70.0), (420.0, 70.0))):
        p.save()
        p.translate(30.0, 35.0 + row * 100.0)
        gradient = gui.QLinearGradient(0.0, 0.0, *end)
        gradient.setColorAt(0.0, gui.QColor("#173b75"))
        gradient.setColorAt(0.5, gui.QColor("#26b9bd"))
        gradient.setColorAt(1.0, gui.QColor("#ffe095"))
        p.fillRect(core.QRectF(0.0, 0.0, 420.0, 70.0), gui.QBrush(gradient))
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
