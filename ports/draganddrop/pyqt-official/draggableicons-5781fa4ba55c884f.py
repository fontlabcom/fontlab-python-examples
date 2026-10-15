# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/5781fa4ba55c884f.md
# this_file: ports/draganddrop/pyqt-official/draggableicons-5781fa4ba55c884f.py
TITLE = "Drag tiles"
MAIN = False
KIND = "pictures"

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


import json

MIME = "application/x-fontlab-owned-tile"
WORDS = [
    "river",
    "amber",
    "quiet",
    "orchard",
    "lantern",
    "copper",
    "meadow",
    "small",
    "drift",
    "silver",
    "bright",
    "rain",
    "window",
    "paper",
    "bird",
    "moss",
    "open",
    "gentle",
    "cloud",
    "stone",
    "warm",
    "bridge",
    "thread",
    "blue",
    "hill",
    "field",
    "sail",
    "round",
    "leaf",
    "listen",
    "walk",
    "evening",
    "morning",
    "soft",
    "grain",
    "ink",
    "clear",
    "line",
    "spring",
    "moon",
    "tree",
    "wave",
    "nest",
    "seed",
    "lake",
    "wind",
    "sun",
    "book",
    "path",
    "green",
]


def configure(s):
    gui, core = s.gui, s.core
    s.state.update(count=0, dragging=False, drops=0)
    labels = []
    pictures = []
    for index in range(3):
        pixmap = gui.QPixmap(72, 72)
        pixmap.fill(gui.QColor(["#d9ead1", "#e7d9b3", "#d9dfef"][index]))
        painter = gui.QPainter(pixmap)
        try:
            painter.setBrush(
                gui.QBrush(gui.QColor(["#3d8d7d", "#c27c42", "#7466a0"][index]))
            )
            if index == 0:
                painter.drawEllipse(12, 10, 48, 48)
                painter.drawLine(12, 52, 60, 52)
            elif index == 1:
                painter.drawRoundedRect(core.QRectF(10, 24, 52, 32), 8.0, 8.0)
                painter.drawEllipse(15, 52, 14, 14)
                painter.drawEllipse(43, 52, 14, 14)
            else:
                painter.drawEllipse(16, 20, 40, 44)
                painter.drawEllipse(10, 6, 20, 28)
                painter.drawEllipse(42, 6, 20, 28)
        finally:
            painter.end()
        pictures.append(pixmap)

    def payload(mime):
        if mime.hasFormat(MIME):
            try:
                data = json.loads(mime.data(MIME).data().decode("utf-8"))
                offset = data.get("offset", [0, 0])
                if (
                    not isinstance(offset, list)
                    or len(offset) != 2
                    or any(type(n) is not int or abs(n) > 10000 for n in offset)
                ):
                    offset = [0, 0]
                return data, offset
            except (ValueError, TypeError, AttributeError):
                pass
        return {}, [0, 0]

    def begin(label, event):
        point = event.pos()
        offset = [int(point.x()), int(point.y())]
        mime = core.QMimeData()
        data = {"offset": offset}
        if KIND == "pictures":
            mime.setImageData(value(label, "pixmap").toImage())
            data["picture"] = True
        else:
            data["text"] = str(value(label, "text"))
            mime.setText(data["text"])
        mime.setData(MIME, core.QByteArray(json.dumps(data).encode("utf-8")))
        drag = gui.QDrag(label)
        drag.setMimeData(mime)
        drag.setPixmap(label.grab())
        drag.setHotSpot(core.QPoint(*offset))
        s.state["dragging"] = True
        try:
            result = drag.exec(
                core.Qt.CopyAction | core.Qt.MoveAction, core.Qt.MoveAction
            )
            if result == core.Qt.MoveAction and label in labels:
                labels.remove(label)
                label.hide()
                label.deleteLater()
                s.state["count"] = len(labels)
        finally:
            s.state["dragging"] = False
            drag.deleteLater()

    class Tile(gui.QLabel):
        def mousePressEvent(self, event):
            if event.button() == core.Qt.LeftButton:
                begin(self, event)
            else:
                gui.QLabel.mousePressEvent(self, event)

    def add(panel, text, x, y, picture=None):
        label = Tile(panel)
        if picture is not None:
            label.setPixmap(picture)
        else:
            label.setTextFormat(core.Qt.PlainText)
            label.setText(text)
            if KIND == "magnets":
                label.setStyleSheet(
                    "QLabel { background: #e3edda; border: 1px solid #9baa90; border-radius: 8px; padding: 6px; }"
                )
            else:
                label.setStyleSheet("QLabel { background: #e8e3d5; padding: 4px; }")
        label.adjustSize()
        label.move(max(0, int(x)), max(0, int(y)))
        label.show()
        labels.append(label)
        s.state["count"] = len(labels)
        return label

    def accepts(mime):
        return (
            mime.hasFormat(MIME) and mime.hasImage()
            if KIND == "pictures"
            else mime.hasText()
        )

    class Panel(gui.QFrame):
        def dragEnterEvent(self, event):
            if accepts(event.mimeData()):
                event.acceptProposedAction()
            else:
                event.ignore()

        def dragMoveEvent(self, event):
            self.dragEnterEvent(event)

        def dropEvent(self, event):
            mime = event.mimeData()
            if not accepts(mime):
                event.ignore()
                return
            _data, offset = payload(mime)
            point = event.pos()
            x, y = int(point.x()) - offset[0], int(point.y()) - offset[1]
            if KIND == "pictures":
                picture = gui.QPixmap.fromImage(gui.QImage(mime.imageData()))
                add(self, "", x, y, picture)
            else:
                for word in str(mime.text()).split():
                    label = add(self, word, x, y)
                    x += int(value(label, "width")) + 6
                    if x > int(value(self, "width")) - 80:
                        x, y = 8, y + 38
            s.state["drops"] += 1
            if mime.hasFormat(MIME) and event.proposedAction() != core.Qt.CopyAction:
                event.setDropAction(core.Qt.MoveAction)
                event.accept()
            else:
                event.acceptProposedAction()

    row = gui.QHBoxLayout()
    s.layout.addLayout(row)
    panels = []
    for index in range(2 if KIND == "pictures" else 1):
        panel = s.keep("panel" + str(index), Panel(s.panel))
        panel.setFrameShape(gui.QFrame.StyledPanel)
        panel.setMinimumSize(340, 400)
        panel.setAcceptDrops(True)
        row.addWidget(panel)
        panels.append(panel)
    if KIND == "pictures":
        for i, picture in enumerate(pictures):
            add(panels[0], "", 15 + i * 95, 25, picture)
    else:
        x, y = 8, 8
        for word in WORDS[: 50 if KIND == "magnets" else 40]:
            label = add(panels[0], word, x, y)
            x += int(value(label, "width")) + 6
            if x > 560:
                x, y = 8, y + 40
    s.keep("labels", labels)
    s.keep("add", add)
    s.keep("payload", payload)

    def check_drag():
        if s.state["dragging"]:
            raise RuntimeError("Finish the drag before closing")
        s.closing = True

    s.handle.cleanup[0] = check_drag
