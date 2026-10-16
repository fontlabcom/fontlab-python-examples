# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a96a7978c0b9f6ee.md
# this_file: ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
TITLE = "Shared-edge button layout"
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
    scene = s.keep("scene", gui.QGraphicsScene(s.window))
    scene.setSceneRect(0.0, 0.0, 900.0, 650.0)
    scene.setBackgroundBrush(gui.QBrush(gui.QColor("#173f32")))
    view = s.keep("view", gui.QGraphicsView(scene, s.panel))
    s.layout.addWidget(view)
    container = gui.QWidget()
    container.setMinimumSize(320, 300)
    container.resize(540, 300)
    buttons = []
    for text in ("North", "East", "Center", "West", "Low", "Near", "Far"):
        button = gui.QPushButton(text, container)
        buttons.append(button)

    def arrange(width):
        width = max(320, min(570, int(width)))
        split = max(width - 300, width // 3)
        center_right = min(300, split + max(30, min(300, width // 3)))
        geometry = [
            (0, 0, split, 100),
            (split, 0, width - split, 100),
            (split, 100, center_right - split, 100),
            (0, 200, center_right, 100),
            (center_right, 200, width - center_right, 100),
            (0, 100, split, 50),
            (0, 150, split, 50),
        ]
        for button, (x, y, w, h) in zip(buttons, geometry):
            button.setGeometry(x, y, w, h)
        s.state["rectangles"] = geometry

    proxy = gui.QGraphicsProxyWidget()
    proxy.setWidget(container)
    scene.addItem(proxy)
    proxy.setWindowFlags(core.Qt.Window)
    proxy.setPos(35.0, 35.0)
    proxy.setMinimumSize(core.QSizeF(320, 300))
    proxy.setMaximumSize(core.QSizeF(570, 300))

    class ResizeFilter(s.qt.private.QObject):
        def eventFilter(self, obj, event):
            if event.type() == core.QEvent.Resize:
                arrange(int(value(container, "width")))
            return False

    watcher = ResizeFilter(s.window)
    container.installEventFilter(watcher)
    s.handle.cleanup.append(lambda: container.removeEventFilter(watcher))
    s.keep("resize_filter", watcher)
    s.keep("subwindow", proxy)
    s.keep("buttons", buttons)
    s.keep("arrange", arrange)
    arrange(540)
