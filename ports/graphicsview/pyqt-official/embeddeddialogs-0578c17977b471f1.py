# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0578c17977b471f1.md
# this_file: ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py
TITLE = "Embedded dialog field"
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
    gui = s.gui
    scene = s.keep("scene", gui.QGraphicsScene(s.window))
    scene.setSceneRect(0.0, 0.0, 3100.0, 2200.0)
    tile = gui.QPixmap(32, 32)
    tile.fill(gui.QColor("#eee9df"))
    p = gui.QPainter(tile)
    try:
        p.setPen(gui.QPen(gui.QColor("#d9d3c8")))
        p.drawLine(0, 0, 32, 32)
    finally:
        p.end()
    scene.setBackgroundBrush(gui.QBrush(tile))
    view = s.keep("view", gui.QGraphicsView(scene, s.panel))
    s.layout.addWidget(view)
    dialogs = []
    states = []

    class Proxy(gui.QGraphicsProxyWidget):
        def hoverEnterEvent(self, event):
            states[self.index]["target"] = 1.0
            self.setZValue(10.0)
            timer.start(20)
            gui.QGraphicsProxyWidget.hoverEnterEvent(self, event)

        def hoverLeaveEvent(self, event):
            states[self.index]["target"] = 0.0
            timer.start(20)
            gui.QGraphicsProxyWidget.hoverLeaveEvent(self, event)

    for i in range(100):
        dialog = gui.QWidget()
        form = gui.QFormLayout(dialog)
        direction = gui.QComboBox(dialog)
        direction.addItems(["Left to right", "Right to left"])
        font = gui.QFontComboBox(dialog)
        style = gui.QComboBox(dialog)
        style.addItems(["Calm", "Contrast"])
        spacing = gui.QSpinBox(dialog)
        spacing.setRange(0, 20)
        spacing.setValue(6)
        for name, widget in [
            ("Direction", direction),
            ("Font", font),
            ("Style", style),
            ("Spacing", spacing),
        ]:
            form.addRow(name, widget)
        proxy = Proxy()
        proxy.index = i
        proxy.setWidget(dialog)
        proxy.setPos(float(i % 10 * 310), float(i // 10 * 220))
        proxy.setAcceptHoverEvents(True)
        scene.addItem(proxy)
        entry = {
            "progress": 0.0,
            "target": 0.0,
            "direction": 0,
            "style": 0,
            "spacing": 6,
        }
        states.append(entry)
        dialogs.append(proxy)
        s.connect(
            direction,
            "currentIndexChanged(int)",
            lambda choice, d=dialog, e=entry: (
                d.setLayoutDirection(
                    s.core.Qt.RightToLeft if choice else s.core.Qt.LeftToRight
                ),
                e.update(direction=int(choice)),
            ),
        )
        s.connect(
            font,
            "currentFontChanged(QFont)",
            lambda chosen, d=dialog: d.setFont(chosen),
        )
        s.connect(
            style,
            "currentIndexChanged(int)",
            lambda choice, d=dialog, e=entry: (
                d.setStyleSheet("background:#dfecdf" if choice else ""),
                e.update(style=int(choice)),
            ),
        )
        s.connect(
            spacing,
            "valueChanged(int)",
            lambda number, f=form, e=entry: (
                f.setSpacing(int(number)),
                e.update(spacing=int(number)),
            ),
        )

    def tick():
        moving = False
        for proxy, state in zip(dialogs, states):
            progress = state["progress"]
            target = state["target"]
            progress = (
                min(target, progress + 0.08)
                if progress < target
                else max(target, progress - 0.08)
            )
            state["progress"] = progress
            proxy.setScale(1.0 + progress * 0.25)
            proxy.setRotation(progress * 3.0)
            if progress == 0:
                proxy.setZValue(0.0)
            moving = moving or progress != target
        if not moving:
            timer.stop()

    timer = s.timer("hover", tick, 20, start=False)
    s.keep("proxies", dialogs)
    s.keep("states", states)
    s.keep("tick", tick)
    s.state["dialog_count"] = 100
