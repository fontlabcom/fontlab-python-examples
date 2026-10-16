# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/2d36e0fe43f5d49a.md
# this_file: ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
TITLE = "CMY channel studio"
MAIN = True

from pathlib import Path
from tempfile import TemporaryDirectory

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    result = getattr(obj, name)
    return result() if callable(result) else result


class Session:
    """One example lifetime; Python state stays off native wrappers."""

    def __init__(self, qt, title, main=False):
        self.qt, self.gui, self.core = qt, qt.QtGui, qt.QtCore
        self.state = {}
        self.pending = []
        self.temporary = None
        self.closing = False
        self.before_close = None
        session = self
        base = self.gui.QMainWindow if main else self.gui.QWidget

        class Window(base):
            def closeEvent(self, event):
                if session.state.get("dragging", False):
                    event.ignore()
                    return
                if session.closing:
                    event.accept()
                elif session.before_close:
                    event.ignore()
                    session.before_close()
                else:
                    event.ignore()
                    session.handle.close()

        self.window = Window()
        self.window.setWindowTitle(title)
        self.window.setAttribute(self.core.Qt.WA_QuitOnClose, False)
        self.window.setAttribute(self.core.Qt.WA_DeleteOnClose, False)
        self.window.resize(760, 560)
        self.handle = ExampleHandle(self.window, self.snapshot)
        self.handle.controls["controller"] = self
        self.handle.cleanup.append(self.prepare_close)
        self.handle.after_close.append(self.dispose)
        self.panel = self.gui.QWidget(self.window) if main else self.window
        if main:
            self.window.setCentralWidget(self.panel)
        self.layout = self.gui.QVBoxLayout(self.panel)

    def snapshot(self):
        return dict(self.state)

    def prepare_close(self):
        if self.state.get("dragging", False):
            raise RuntimeError("Finish the drag before closing this example")
        self.closing = True

    def dispose(self):
        if self.temporary is not None:
            self.temporary.cleanup()
            self.temporary = None
        self.pending.clear()

    def keep(self, name, obj):
        self.handle.controls[name] = obj
        return obj

    def connect(self, obj, signature, callback):
        def route(*args):
            if not self.closing:
                callback(*args)

        self.handle.connect_old(obj, signature, route)
        return route

    def button(self, name, callback, layout=None):
        button = self.keep(name, self.gui.QPushButton(name, self.panel))
        (layout or self.layout).addWidget(button)
        self.connect(button, "clicked()", lambda *args: callback())
        return button

    def combo(self, name, items, callback, layout=None):
        combo = self.keep(name, self.gui.QComboBox(self.panel))
        combo.addItems(items)
        (layout or self.layout).addWidget(combo)
        self.connect(combo, "currentIndexChanged(int)", lambda i: callback(int(i)))
        return combo

    def timer(self, name, callback, interval, start=True, once=False):
        timer = self.keep(name, self.core.QTimer(self.window))
        timer.setSingleShot(once)
        self.connect(timer, "timeout()", lambda: callback())
        self.handle.cleanup.append(timer.stop)
        if start:
            timer.start(interval)
        return timer

    def root(self):
        if self.temporary is None:
            self.temporary = TemporaryDirectory(prefix="fontlab-example-")
        return Path(self.temporary.name)

    def path(self, filename):
        root = self.root().resolve()
        result = Path(filename).resolve()
        if result == root or not result.is_relative_to(root):
            raise ValueError("Choose a file within the example folder")
        return result

    def dialog(self, dialog):
        from fontlabapp.widgets import OwnedWidget

        dialog.setAttribute(self.core.Qt.WA_QuitOnClose, False)
        self.handle.alerts.append(OwnedWidget(dialog, dialog))
        self.pending.append(dialog)
        dialog.open()
        return dialog

    def message(self, text):
        box = self.gui.QMessageBox(self.window)
        box.setText(str(text))
        return self.dialog(box)

    def choose(self, saving, callback, pattern="All files (*)"):
        box = self.gui.QFileDialog(self.window)
        box.setDirectory(str(self.root()))
        box.setNameFilter(pattern)
        box.setAcceptMode(box.AcceptSave if saving else box.AcceptOpen)

        def selected(filename):
            try:
                callback(str(filename))
            except (OSError, ValueError, UnicodeError) as error:
                self.state["error"] = str(error)
                self.message(str(error))

        self.connect(box, "fileSelected(QString)", selected)
        return self.dialog(box)

    def action(self, menu, name, callback, check=False):
        action = self.keep(name, self.gui.QAction(name, self.window))
        action.setCheckable(check)
        icon = self.gui.QPixmap(24, 24)
        icon.fill(self.gui.QColor("#f0eadc"))
        painter = self.gui.QPainter(icon)
        try:
            painter.setPen(self.gui.QPen(self.gui.QColor("#36516d"), 2))
            painter.drawRoundedRect(self.core.QRectF(4, 3, 16, 18), 2.0, 2.0)
            painter.drawText(7, 17, name[:1])
        finally:
            painter.end()
        action.setIcon(self.gui.QIcon(icon))
        menu.addAction(action)
        self.connect(action, "triggered(bool)", lambda *args: callback())
        return action

    def finish(self):
        return self.handle


def build(qt):
    session = Session(qt, TITLE, MAIN)
    try:
        configure(session)
        return session.finish()
    except BaseException:
        session.handle.close()
        raise


def separate_pixels(pixels, colors, inverted, brightness):
    """CMY darkness multiplies the selected per-channel transmittances."""
    output = []
    for rgb in pixels:
        inks = [(255 - component) / 255.0 for component in rgb]
        inks = [1.0 - ink if inverted[i] else ink for i, ink in enumerate(inks)]
        components = []
        for component in range(3):
            transmission = 1.0
            for channel, ink in enumerate(inks):
                transmission *= 1.0 - ink * (1.0 - colors[channel][component] / 255.0)
            components.append(max(0, min(255, round(255 * transmission * brightness))))
        output.append(tuple(components))
    return output


def configure(s):
    gui = s.gui
    s.state.update(
        colors=[(0, 255, 255), (255, 0, 255), (255, 255, 0)],
        inverted=[False] * 3,
        brightness=1.0,
    )
    image = [gui.QImage(120, 90, gui.QImage.Format_ARGB32)]
    for y in range(90):
        for x in range(120):
            image[0].setPixel(
                x, y, (255 << 24) | (x * 255 // 119 << 16) | (y * 255 // 89 << 8) | 180
            )
    previews = []

    class Preview(gui.QLabel):
        def mousePressEvent(self, event):
            mime = s.core.QMimeData()
            mime.setImageData(value(self, "pixmap").toImage())
            drag = gui.QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(value(self, "pixmap"))
            s.state["dragging"] = True
            try:
                drag.exec(s.core.Qt.CopyAction)
            finally:
                s.state["dragging"] = False
                drag.deleteLater()

    row = gui.QHBoxLayout()
    s.layout.addLayout(row)
    for index in range(5):
        label = s.keep("preview" + str(index), Preview(s.panel))
        row.addWidget(label)
        previews.append(label)
    combined = [None]

    def recombine():
        source = image[0]
        width, height = int(value(source, "width")), int(value(source, "height"))
        pixels = [
            tuple((int(source.pixel(x, y)) >> shift) & 255 for shift in (16, 8, 0))
            for y in range(height)
            for x in range(width)
        ]
        combined[0] = gui.QImage(width, height, gui.QImage.Format_ARGB32)
        channel_images = [
            gui.QImage(width, height, gui.QImage.Format_ARGB32) for _ in range(3)
        ]
        result = separate_pixels(
            pixels, s.state["colors"], s.state["inverted"], s.state["brightness"]
        )
        for i, rgb in enumerate(result):
            x, y = i % width, i // width
            combined[0].setPixel(
                x, y, (255 << 24) | (rgb[0] << 16) | (rgb[1] << 8) | rgb[2]
            )
            for channel in range(3):
                ink = (255 - pixels[i][channel]) / 255
                if s.state["inverted"][channel]:
                    ink = 1 - ink
                tint = s.state["colors"][channel]
                rgb_ink = [round(255 * (1 - ink) + c * ink) for c in tint]
                channel_images[channel].setPixel(
                    x,
                    y,
                    (255 << 24) | (rgb_ink[0] << 16) | (rgb_ink[1] << 8) | rgb_ink[2],
                )
        for label, picture in zip(previews, [source] + channel_images + [combined[0]]):
            label.setPixmap(gui.QPixmap.fromImage(picture))
        s.state["size"] = [width, height]

    def open_file(filename):
        candidate = gui.QImage(str(filename))
        if candidate.isNull():
            raise ValueError("Cannot decode the image")
        image[0] = candidate
        recombine()

    def save_file(filename):
        if not combined[0].save(str(filename), "PNG"):
            raise OSError("Cannot save the combined image")

    def invert(channel):
        s.state["inverted"][channel] = not s.state["inverted"][channel]
        recombine()

    def modify(channel):
        dialog = gui.QColorDialog(gui.QColor(*s.state["colors"][channel]), s.window)

        def selected(color):
            s.state["colors"][channel] = tuple(
                int(value(color, c)) for c in ("red", "green", "blue")
            )
            recombine()

        s.connect(dialog, "colorSelected(QColor)", selected)
        s.dialog(dialog)

    for channel in range(3):
        s.button("Modify " + str(channel + 1), lambda i=channel: modify(i))
        s.button("Invert " + str(channel + 1), lambda i=channel: invert(i))
    file = s.window.menuBar().addMenu("File")
    s.action(file, "Open", lambda: s.choose(False, open_file))
    s.action(file, "Save", lambda: s.choose(True, save_file, "PNG (*.png)"))
    s.action(file, "Exit", s.handle.close)
    brightness = s.window.menuBar().addMenu("Brightness")

    def set_brightness(number):
        s.state["brightness"] = number
        recombine()

    for percent in (0, 25, 50, 75, 100, 125, 150):
        s.action(
            brightness, str(percent) + "%", lambda p=percent: set_brightness(p / 100)
        )
    s.keep("recombine", recombine)
    s.keep("open_file", open_file)
    s.keep("save_file", save_file)
    s.keep("invert", invert)
    recombine()
