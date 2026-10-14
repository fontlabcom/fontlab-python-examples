# this_file: ports/graphics-painting/eyllanesc/main-b1c25455dbcb6bac.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/qpa/windows/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-


from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import Demo, read

COLORS = ("#f09f8f", "#a2bff2", "#c0ef8f")


def build(qt: Any) -> ExampleHandle:
    demo = Demo(qt, __file__, "b1c25455dbcb6bac")
    gui, core = qt.QtGui, qt.QtCore
    windows, stores = [], []

    class Window(gui.QWindow):
        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            if not windows:
                demo.begin(self)
            self._text = ""
            self._last = None
            self._image = gui.QImage()
            self._color = COLORS[(len(windows) + 1) % len(COLORS)]
            self._backing = gui.QBackingStore(self)
            stores.append(self._backing)
            windows.append(self)
            demo.track(self, "_image", "_last", "_backing", "_timer")
            self._timer = core.QTimer(self)
            self._timer.setSingleShot(True)
            demo.connect(self._timer, "timeout()", self.render)
            demo.handle.cleanup.append(self._timer.stop)
            if parent is None:
                self.setFlags(
                    read(self, "flags")
                    | core.Qt.WindowTitleHint
                    | core.Qt.WindowSystemMenuHint
                    | core.Qt.WindowMinMaxButtonsHint
                    | core.Qt.WindowCloseButtonHint
                )
                self.setGeometry(0, 0, 640, 480)
                self.setSizeIncrement(core.QSize(10, 10))
                self.setBaseSize(core.QSize(640, 480))
                self.setMinimumSize(core.QSize(240, 160))
                self.setMaximumSize(core.QSize(800, 600))
            else:
                self.setGeometry(160, 120, 320, 240)
            self.create()
            self.resizeEvent(None)

        def scheduleRender(self) -> None:
            if not demo.closing:
                self._timer.start(1)

        def exposeEvent(self, event: Any) -> None:
            self.scheduleRender()

        def resizeEvent(self, event: Any) -> None:
            if demo.closing or not hasattr(self, "_image"):
                return
            width = max(int(read(self, "width")), int(read(self._image, "width")))
            height = max(int(read(self, "height")), int(read(self._image, "height")))
            if width > int(read(self._image, "width")) or height > int(
                read(self._image, "height")
            ):
                old = self._image
                self._image = gui.QImage(width, height, gui.QImage.Format_RGB32)
                self._image.fill(gui.QColor(self._color).rgba())
                painter = gui.QPainter(self._image)
                try:
                    painter.drawImage(0, 0, old)
                finally:
                    painter.end()
            self.scheduleRender()

        def stroke(self, event: Any) -> None:
            if self._last is not None:
                painter = gui.QPainter(self._image)
                try:
                    painter.setRenderHint(gui.QPainter.Antialiasing)
                    painter.drawLine(self._last, event.pos())
                finally:
                    painter.end()
                self._last = event.pos()
                self.scheduleRender()

        def mousePressEvent(self, event: Any) -> None:
            self._last = event.pos()

        def mouseMoveEvent(self, event: Any) -> None:
            self.stroke(event)

        def mouseReleaseEvent(self, event: Any) -> None:
            self.stroke(event)
            self._last = None

        def keyPressEvent(self, event: Any) -> None:
            if event.key() == core.Qt.Key_Backspace:
                # Preserve the source's rule: a final single character remains.
                if len(self._text) > 1:
                    self._text = self._text[:-1]
            elif event.key() in (core.Qt.Key_Enter, core.Qt.Key_Return):
                self._text += "\n"
            else:
                self._text += event.text()
            self.scheduleRender()

        def render(self) -> None:
            if demo.closing or not self.isExposed():
                return
            self._timer.stop()
            rect = core.QRect(0, 0, int(read(self, "width")), int(read(self, "height")))
            region = gui.QRegion(rect)
            self._backing.resize(rect.size())
            self._backing.beginPaint(region)
            try:
                painter = gui.QPainter(self._backing.paintDevice())
                try:
                    painter.drawImage(0, 0, self._image)
                    font = gui.QFont()
                    font.setPixelSize(32)
                    painter.setFont(font)
                    painter.drawText(rect, 0, self._text)
                finally:
                    painter.end()
            finally:
                self._backing.endPaint()
            self._backing.flush(region)

    try:
        a = Window()
        a.setFramePosition(core.QPoint(10, 10))
        a.setTitle("Window A")
        a.setObjectName("Window A")
        b = Window()
        demo.begin(b)
        b.setFramePosition(core.QPoint(100, 100))
        b.setTitle("Window B")
        b.setObjectName("Window B")
        child = Window(b)
        child.setObjectName("ChildOfB")
        screens = gui.QApplication.screens()

        def screen_key(screen: Any) -> tuple:
            geometry = read(screen, "geometry")
            return (
                str(read(screen, "name")),
                tuple(
                    int(read(geometry, key)) for key in ("x", "y", "width", "height")
                ),
            )

        primary_key = screen_key(screens[0]) if screens else None
        for screen in screens:
            if screen_key(screen) == primary_key:
                continue
            window = Window()
            demo.begin(window)
            window.setScreen(screen)
            geometry = read(window, "geometry")
            geometry.moveCenter(read(screen, "availableGeometry").center())
            window.setGeometry(
                geometry.x(), geometry.y(), geometry.width(), geometry.height()
            )
            window.setTitle(str(read(screen, "name")))
        for index, window in enumerate(windows):
            demo.remember("window" + str(index), window)
            demo.remember("renderTimer" + str(index), window._timer)
            if window is not a:
                window.show()

        def release_stores() -> None:
            for store in stores:
                store.delete()
            stores.clear()
            windows.clear()

        demo.handle.release.append(release_stores)
        return demo.finish(
            a,
            lambda: {
                "window_count": len(windows),
                "windows": [
                    {
                        "title": str(read(w, "title")),
                        "text": w._text,
                        "color": w._color,
                        "geometry": [
                            int(read(w, "geometry").x()),
                            int(read(w, "geometry").y()),
                            int(read(w, "width")),
                            int(read(w, "height")),
                        ],
                        "image_size": [
                            int(read(w._image, "width")),
                            int(read(w._image, "height")),
                        ],
                    }
                    for w in windows
                ],
            },
        )
    except BaseException:
        # Stores are non-QObjects, with explicit deletion rather than deleteLater.
        demo.abort()
        for store in stores:
            store.delete()
        stores.clear()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("b1c25455dbcb6bac")
