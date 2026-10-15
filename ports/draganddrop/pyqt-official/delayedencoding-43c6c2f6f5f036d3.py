# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/43c6c2f6f5f036d3.md
# this_file: ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py
TITLE = "Deferred picture export"
MAIN = False

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


def configure(s):
    gui, core = s.gui, s.core
    s.state.update(encodings=0, dragging=False)

    def picture():
        pixmap = gui.QPixmap(220, 160)
        pixmap.fill(gui.QColor("#f0ead7"))
        p = gui.QPainter(pixmap)
        try:
            p.setBrush(gui.QBrush(gui.QColor("#2b8d91")))
            p.drawEllipse(50, 25, 120, 90)
            p.drawLine(20, 130, 200, 130)
            p.drawText(68, 145, "Small planet")
        finally:
            p.end()
        return pixmap

    class DeferredMime(core.QMimeData):
        def __init__(self):
            core.QMimeData.__init__(self)
            self.cached_png = None

        def formats(self):
            return ["image/png"]

        def hasFormat(self, name):
            return str(name) == "image/png"

        def retrieveData(self, name, preferred):
            if str(name) != "image/png":
                return core.QByteArray()
            if self.cached_png is None:
                buffer = core.QBuffer()
                try:
                    buffer.open(core.QIODevice.WriteOnly)
                    if not picture().save(buffer, "PNG"):
                        raise ValueError("Could not encode the drag picture")
                    self.cached_png = core.QByteArray(buffer.data().data())
                    s.state["encodings"] += 1
                finally:
                    buffer.close()
                    buffer.deleteLater()
            return self.cached_png

    class Export(gui.QPushButton):
        def mousePressEvent(self, event):
            mime = DeferredMime()
            drag = gui.QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(picture())
            s.state["dragging"] = True
            try:
                drag.exec(core.Qt.CopyAction)
            finally:
                s.state["dragging"] = False
                drag.deleteLater()

    preview = s.keep("preview", gui.QLabel(s.panel))
    preview.setPixmap(picture())
    s.layout.addWidget(preview)
    instructions = gui.QLabel(
        "Drag Export to an image target; pixels are prepared on demand.", s.panel
    )
    s.layout.addWidget(instructions)
    button = s.keep("Export", Export("Export", s.panel))
    s.layout.addWidget(button)
    s.keep("mime_factory", DeferredMime)

    def check_drag():
        if s.state["dragging"]:
            raise RuntimeError("Finish the drag before closing")
        s.closing = True

    s.handle.cleanup[0] = check_drag
