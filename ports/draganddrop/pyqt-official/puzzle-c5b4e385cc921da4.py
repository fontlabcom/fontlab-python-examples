# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c5b4e385cc921da4.md
# this_file: ports/draganddrop/pyqt-official/puzzle-c5b4e385cc921da4.py
TITLE = "Picture assembly"
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
import random


def configure(s):
    gui, core = s.gui, s.core
    size = 64
    mime_type = "application/x-fontlab-puzzle"
    tiles = {}
    board = {}
    order = []
    s.state.update(correct=0, completed=False, dragging=False)
    original = gui.QPixmap(320, 320)
    original.fill(gui.QColor("#e5dfc5"))
    painter = gui.QPainter(original)
    try:
        for y in range(5):
            for x in range(5):
                painter.fillRect(
                    x * 64,
                    y * 64,
                    64,
                    64,
                    gui.QColor(35 + x * 40, 50 + y * 38, 180 - x * 16),
                )
                painter.drawText(x * 64 + 12, y * 64 + 36, str(y * 5 + x + 1))
        painter.drawEllipse(70, 45, 190, 230)
    finally:
        painter.end()

    def make_tiles(picture):
        scaled = picture.scaled(
            320, 320, core.Qt.KeepAspectRatioByExpanding, core.Qt.SmoothTransformation
        )
        ox = (int(value(scaled, "width")) - 320) // 2
        oy = (int(value(scaled, "height")) - 320) // 2
        for index in range(25):
            tiles[index] = scaled.copy(
                ox + index % 5 * 64, oy + index // 5 * 64, 64, 64
            )

    def restart():
        completion.stop()
        board.clear()
        order[:] = list(range(25))
        random.shuffle(order)
        s.state.update(correct=0, completed=False)
        board_view.update()
        tray.update()

    def place(tile, cell):
        if not 0 <= tile < 25 or not 0 <= cell < 25:
            return False
        if cell in board and board[cell] != tile:
            return False
        for old in [k for k, v in board.items() if v == tile]:
            del board[old]
        if tile in order:
            order.remove(tile)
        board[cell] = tile
        count = sum(k == v for k, v in board.items())
        s.state["correct"] = count
        if count == 25 and not s.state["completed"]:
            s.state["completed"] = True
            completion.start(0)
        board_view.update()
        tray.update()
        return True

    def return_tile(tile):
        for cell in [k for k, v in board.items() if v == tile]:
            del board[cell]
        if tile not in order:
            order.append(tile)
        s.state.update(correct=sum(k == v for k, v in board.items()), completed=False)
        board_view.update()
        tray.update()

    class Surface(gui.QWidget):
        def __init__(self, parent, is_board):
            gui.QWidget.__init__(self, parent)
            self.is_board = is_board
            self.hover_cell = None
            self.setAcceptDrops(True)
            self.setFixedSize(320, 320)

        def paintEvent(self, event):
            gui.QWidget.paintEvent(self, event)
            p = gui.QPainter(self)
            try:
                p.fillRect(value(self, "rect"), gui.QColor("#f4f0e5"))
                mapping = board if self.is_board else dict(enumerate(order))
                for cell in range(25):
                    x, y = cell % 5 * size, cell // 5 * size
                    p.drawRect(x, y, size, size)
                    if cell in mapping:
                        p.drawPixmap(x, y, tiles[mapping[cell]])
                if self.hover_cell is not None:
                    p.setPen(gui.QPen(gui.QColor("#e8a72d"), 3))
                    p.drawRect(
                        self.hover_cell % 5 * size,
                        self.hover_cell // 5 * size,
                        size,
                        size,
                    )
            finally:
                p.end()

        def mousePressEvent(self, event):
            pos = event.pos()
            cell = int(pos.y()) // size * 5 + int(pos.x()) // size
            mapping = board if self.is_board else dict(enumerate(order))
            if cell not in mapping:
                return
            tile = mapping[cell]
            mime = core.QMimeData()
            mime.setData(
                mime_type, core.QByteArray(json.dumps({"tile": tile}).encode())
            )
            drag = gui.QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(tiles[tile])
            s.state["dragging"] = True
            try:
                drag.exec(core.Qt.MoveAction)
            finally:
                s.state["dragging"] = False
                drag.deleteLater()

        def dragEnterEvent(self, event):
            if event.mimeData().hasFormat(mime_type):
                event.acceptProposedAction()
            else:
                event.ignore()

        def dragMoveEvent(self, event):
            pos = event.pos()
            cell = int(pos.y()) // size * 5 + int(pos.x()) // size
            self.hover_cell = cell
            self.update()
            if self.is_board and cell in board:
                event.ignore()
            else:
                event.acceptProposedAction()

        def dragLeaveEvent(self, event):
            self.hover_cell = None
            self.update()
            event.accept()

        def dropEvent(self, event):
            self.hover_cell = None
            try:
                tile = json.loads(event.mimeData().data(mime_type).data().decode())[
                    "tile"
                ]
                if type(tile) is not int or not 0 <= tile < 25:
                    raise ValueError("Invalid tile")
            except (ValueError, TypeError, KeyError):
                event.ignore()
                return
            pos = event.pos()
            cell = int(pos.y()) // size * 5 + int(pos.x()) // size
            if self.is_board and not place(tile, cell):
                event.ignore()
                return
            if not self.is_board:
                return_tile(tile)
            event.setDropAction(core.Qt.MoveAction)
            event.accept()
            self.update()

    row = gui.QHBoxLayout()
    s.layout.addLayout(row)
    tray = s.keep("tray", Surface(s.panel, False))
    board_view = s.keep("board", Surface(s.panel, True))
    row.addWidget(tray)
    row.addWidget(board_view)
    completion = s.timer(
        "completion",
        lambda: (
            s.message("All twenty-five pieces are home.")
            if s.state["completed"]
            else None
        ),
        0,
        start=False,
        once=True,
    )
    file = s.window.menuBar().addMenu("File")

    def open_file(filename):
        picture = gui.QPixmap(filename)
        if picture.isNull():
            raise ValueError("Cannot decode this puzzle picture")
        make_tiles(picture)
        restart()

    s.action(file, "Open", lambda: s.choose(False, open_file))
    s.action(file, "Exit", s.handle.close)
    s.action(s.window.menuBar().addMenu("Game"), "Restart", restart)
    for name, obj in {
        "place": place,
        "return_tile": return_tile,
        "restart": restart,
        "positions": board,
        "order": order,
    }.items():
        s.keep(name, obj)
    make_tiles(original)
    restart()
