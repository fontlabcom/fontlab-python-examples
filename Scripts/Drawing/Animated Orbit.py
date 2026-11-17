# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Animated Orbit.py
"""What: Animate a dot around an ellipse with a widget-owned Qt timer.
Usage: Run from Scripts; closing stops the animation.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is needed or changed. No blocking loop or sleep is used.
"""

import math
from time import monotonic
from typing import Any


def orbit_position(seconds: float) -> tuple[float, float]:
    """One orbit takes four seconds; return canvas coordinates."""
    angle = seconds * math.tau / 4.0
    return 250.0 + 180.0 * math.cos(angle), 175.0 + 110.0 * math.sin(angle)


def panel_type(core: Any, gui: Any) -> type:
    class Canvas(gui.QWidget):
        def __init__(self, parent: Any) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.setWindowTitle("Animated Orbit")
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.setAttribute(core.Qt.WA_DeleteOnClose, True)
            self.setFixedSize(500, 350)
            self.orbit_started = monotonic()
            self.orbit_timer_id = self.startTimer(33)

        def timerEvent(self, event: Any) -> None:
            try:
                self.update()
            except Exception as error:
                self.killTimer(self.orbit_timer_id)
                self.orbit_timer_id = 0
                print(f"Animated Orbit: {error}")

        def closeEvent(self, event: Any) -> None:
            if self.orbit_timer_id:
                self.killTimer(self.orbit_timer_id)
                self.orbit_timer_id = 0
            event.accept()

        def paintEvent(self, event: Any) -> None:
            painter = gui.QPainter(self)
            try:
                painter.fillRect(core.QRectF(0.0, 0.0, 500.0, 350.0), gui.QColor("white"))
                painter.setRenderHint(gui.QPainter.Antialiasing, True)
                painter.setPen(gui.QColor("#a0b6c5"))
                painter.drawEllipse(core.QRectF(70.0, 65.0, 360.0, 220.0))
                painter.setBrush(gui.QBrush(gui.QColor("#e87951")))
                x, y = orbit_position(monotonic() - self.orbit_started)
                painter.drawEllipse(core.QPointF(x, y), 15.0, 15.0)
            except Exception as error:
                print(f"Animated Orbit: {error}")
            finally:
                painter.end()

    return Canvas


def main() -> Any:
    from PythonQt import QtCore, QtGui
    import fly.ap.core.scripting as scripting

    return scripting.show_script_dialog(panel_type(QtCore, QtGui), "drawing_animated_orbit")


if __name__ == "__main__":
    main()
