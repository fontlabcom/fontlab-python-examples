# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Painter Opacity Layers.py
"""What: Compare painter opacity on overlapping coloured rectangles.
Usage: Run from FontLab's Scripts menu; close the window when finished.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is required or changed. This is a Qt drawing demonstration.
"""

from typing import Any

TITLE = 'Painter Opacity Layers'
KEY = 'drawing_painter_opacity_layers'


def draw(p: Any, core: Any, gui: Any) -> None:
    """Paint the demonstration in a fixed 500 by 350 logical canvas."""
    for index, opacity in enumerate((1.0, 0.65, 0.3)):
        p.save()
        p.translate(index * 165.0 + 15.0, 75.0)
        p.fillRect(core.QRectF(0.0, 0.0, 110.0, 110.0), gui.QColor("#317e85"))
        p.setOpacity(opacity)
        p.fillRect(core.QRectF(35.0, 55.0, 110.0, 110.0), gui.QColor("#e87855"))
        p.restore()
        p.drawText(core.QPointF(index * 165.0 + 35.0, 290.0), f"Opacity {opacity:g}")


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
