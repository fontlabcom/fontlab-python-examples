# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Drawing/Image PNG Export.py
"""What: Render a gradient and vector curve to QImage, then save a temporary PNG.
Usage: Run from Scripts; the preview reports the absolute temporary filename.
Setup: FontLab 9, Python 3.11, PythonQt, Fly and fontlabapp.
No font is needed or changed. Each run creates one new file in the temp folder.
"""

import os
import tempfile
from typing import Any


def make_image(core: Any, gui: Any) -> Any:
    """Finish painting before either saving or displaying the image."""
    image = gui.QImage(440, 240, gui.QImage.Format_ARGB32_Premultiplied)
    image.fill(gui.QColor("white"))
    painter = gui.QPainter(image)
    try:
        painter.setRenderHint(gui.QPainter.Antialiasing, True)
        gradient = gui.QLinearGradient(0.0, 0.0, 440.0, 240.0)
        gradient.setColorAt(0.0, gui.QColor("#154568"))
        gradient.setColorAt(1.0, gui.QColor("#54c8b8"))
        painter.fillRect(core.QRectF(0.0, 0.0, 440.0, 240.0), gui.QBrush(gradient))
        path = gui.QPainterPath(core.QPointF(30.0, 190.0))
        path.cubicTo(100.0, 0.0, 300.0, 0.0, 410.0, 190.0)
        pen = gui.QPen(gui.QColor("white"))
        pen.setWidthF(8.0)
        painter.setPen(pen)
        painter.drawPath(path)
    finally:
        painter.end()
    return image


def save_png(image: Any) -> str:
    """Use an exclusive temporary file and remove it if Qt cannot encode PNG."""
    descriptor, filename = tempfile.mkstemp(prefix="fontlab-drawing-", suffix=".png")
    os.close(descriptor)
    try:
        if not image.save(filename, "PNG"):
            raise OSError("Qt could not save the temporary PNG.")
    except Exception:
        os.unlink(filename)
        raise
    return filename


def main() -> Any:
    """Display the saved image in an App-owned window."""
    from PythonQt import QtCore, QtGui
    import fly.ap.core.scripting as scripting

    image = make_image(QtCore, QtGui)
    filename = save_png(image)

    class Preview(QtGui.QWidget):
        def __init__(self, parent: Any) -> None:
            QtGui.QWidget.__init__(self, parent, QtCore.Qt.Window)
            self.setWindowTitle("Image PNG Export")
            self.setAttribute(QtCore.Qt.WA_QuitOnClose, False)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
            self.resize(480, 320)
            layout = QtGui.QVBoxLayout(self)
            picture = QtGui.QLabel(self)
            picture.setPixmap(QtGui.QPixmap.fromImage(image))
            layout.addWidget(picture)
            message = QtGui.QLabel(filename, self)
            message.setWordWrap(True)
            message.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            layout.addWidget(message)

    return scripting.show_script_dialog(Preview, "drawing_image_png_export")


if __name__ == "__main__":
    main()
