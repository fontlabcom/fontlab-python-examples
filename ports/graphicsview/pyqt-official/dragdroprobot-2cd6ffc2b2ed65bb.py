# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/2cd6ffc2b2ed65bb.md
# this_file: ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
TITLE = "Articulated color robot"
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


import math


def configure(s):
    gui, core = s.gui, s.core
    scene = s.keep("scene", gui.QGraphicsScene(s.window))
    scene.setSceneRect(-340.0, -260.0, 680.0, 520.0)
    view = s.keep("view", gui.QGraphicsView(scene, s.panel))
    s.layout.addWidget(view)
    s.state.update(frame=0, colors={}, hover=None)
    parts = []
    swatches = []

    class Part(gui.QGraphicsRectItem):
        def dragEnterEvent(self, event):
            mime = event.mimeData()
            if mime.hasColor() or (self.cr_name == "head" and mime.hasImage()):
                event.acceptProposedAction()
            else:
                event.ignore()

        def dragMoveEvent(self, event):
            self.dragEnterEvent(event)

        def dropEvent(self, event):
            mime = event.mimeData()
            if mime.hasColor():
                color = gui.QColor(mime.colorData())
                self.setBrush(gui.QBrush(color))
                s.state["colors"][self.cr_name] = str(color.name())
                event.acceptProposedAction()
            elif self.cr_name == "head" and mime.hasImage():
                pixmap = gui.QPixmap.fromImage(gui.QImage(mime.imageData()))
                if self.cr_picture is None:
                    self.cr_picture = gui.QGraphicsPixmapItem(self)
                self.cr_picture.setPixmap(
                    pixmap.scaled(
                        70, 55, core.Qt.KeepAspectRatio, core.Qt.SmoothTransformation
                    )
                )
                self.cr_picture.setPos(-35.0, -25.0)
                event.acceptProposedAction()
            else:
                event.ignore()

        def hoverEnterEvent(self, event):
            self.setOpacity(0.75)
            gui.QGraphicsRectItem.hoverEnterEvent(self, event)

        def hoverLeaveEvent(self, event):
            self.setOpacity(1.0)
            gui.QGraphicsRectItem.hoverLeaveEvent(self, event)

    specs = [
        ("body", 0, 0, 85, 100),
        ("head", 0, -90, 80, 60),
        ("left arm", -80, -15, 35, 95),
        ("right arm", 80, -15, 35, 95),
        ("left leg", -28, 115, 35, 95),
        ("right leg", 28, 115, 35, 95),
    ]
    for name, x, y, w, h in specs:
        part = Part(-w / 2, -h / 2, w, h)
        part.cr_name = name
        part.cr_picture = None
        part.setPos(float(x), float(y))
        part.setAcceptDrops(True)
        part.setAcceptHoverEvents(True)
        part.setBrush(gui.QBrush(gui.QColor("#b6c8c8")))
        scene.addItem(part)
        parts.append(part)
    # A new geometric face, painted as children of the head.
    head = parts[1]
    for x in (-20.0, 12.0):
        eye = gui.QGraphicsEllipseItem(x, -12.0, 9.0, 9.0, head)
        eye.setBrush(gui.QBrush(gui.QColor("#34434e")))
    mouth = gui.QGraphicsLineItem(-20.0, 14.0, 20.0, 14.0, head)
    mouth.setPen(gui.QPen(gui.QColor("#34434e"), 3))
    palette = [
        "#c46862",
        "#d29e49",
        "#c4bd55",
        "#6ea56c",
        "#4ba4a4",
        "#5e8dbb",
        "#8670b5",
        "#ad6b9f",
        "#815e50",
        "#6b7b86",
    ]

    class Swatch(gui.QGraphicsEllipseItem):
        def hoverEnterEvent(self, event):
            s.state["hover"] = self.cr_color
            self.setToolTip(self.cr_color)
            gui.QGraphicsEllipseItem.hoverEnterEvent(self, event)

        def hoverLeaveEvent(self, event):
            s.state["hover"] = None
            gui.QGraphicsEllipseItem.hoverLeaveEvent(self, event)

        def mousePressEvent(self, event):
            mime = core.QMimeData()
            mime.setColorData(gui.QColor(self.cr_color))
            drag = gui.QDrag(view)
            drag.setMimeData(mime)
            swatch = gui.QPixmap(32, 32)
            swatch.fill(gui.QColor(self.cr_color))
            drag.setPixmap(swatch)
            s.state["dragging"] = True
            try:
                drag.exec(core.Qt.CopyAction)
            finally:
                s.state["dragging"] = False
                drag.deleteLater()

    for index, color in enumerate(palette):
        angle = index * math.tau / 10
        swatch = Swatch(-18.0, -18.0, 36.0, 36.0)
        swatch.cr_color = color
        swatch.setBrush(gui.QBrush(gui.QColor(color)))
        swatch.setPos(math.cos(angle) * 280, math.sin(angle) * 210)
        swatch.setAcceptHoverEvents(True)
        scene.addItem(swatch)
        swatches.append(swatch)

    def tick():
        s.state["frame"] += 1
        phase = s.state["frame"] * 0.05
        for index, part in enumerate(parts):
            part.setRotation(math.sin(phase + index) * (0.8 if index == 0 else 15))
            part.setScale(1.0 + math.sin(phase + index) * 0.025)

    s.timer("animation", tick, 30)
    s.keep("parts", parts)
    s.keep("tick", tick)
    s.keep("swatches", swatches)
