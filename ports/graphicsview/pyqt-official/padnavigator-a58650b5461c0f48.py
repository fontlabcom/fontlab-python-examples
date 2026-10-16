# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a58650b5461c0f48.md
# this_file: ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py
TITLE = "Icon pad navigation"
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
    scene.setSceneRect(0.0, 0.0, 660.0, 500.0)
    scene.setBackgroundBrush(gui.QBrush(gui.QColor("#273c50")))
    s.state.update(selection=4, back=False, history=[4])
    root = gui.QGraphicsWidget()
    scene.addItem(root)
    front = gui.QWidget()
    grid = gui.QGridLayout(front)
    back = gui.QWidget()
    form = gui.QFormLayout(back)
    title = gui.QLineEdit("Workspace", back)
    date = gui.QDateEdit(back)
    choices = gui.QTreeWidget(back)
    choices.setHeaderLabels(["Preferences"])
    for text in ("Display", "Schedule", "Storage"):
        parent = gui.QTreeWidgetItem([text])
        choices.addTopLevelItem(parent)
        parent.addChild(gui.QTreeWidgetItem(["Enabled"]))
    form.addRow("Title", title)
    form.addRow("Date", date)
    form.addRow("Choices", choices)
    front_proxy = gui.QGraphicsProxyWidget(root)
    front_proxy.setWidget(front)
    back_proxy = gui.QGraphicsProxyWidget(root)
    back_proxy.setWidget(back)
    front_proxy.setPos(30.0, 30.0)
    back_proxy.setPos(30.0, 30.0)
    back_proxy.setVisible(False)
    buttons = []
    for index, text in enumerate(
        [
            "Pages",
            "Brushes",
            "Colors",
            "Notes",
            "Home",
            "Tools",
            "History",
            "Files",
            "Help",
        ]
    ):
        button = gui.QPushButton(text, front)
        icon = gui.QPixmap(40, 40)
        icon.fill(gui.QColor("#e2be63"))
        painter = gui.QPainter(icon)
        try:
            painter.drawEllipse(6 + index % 3, 6, 26, 26)
            painter.drawText(14, 26, str(index + 1))
        finally:
            painter.end()
        button.setIcon(gui.QIcon(icon))
        button.setMinimumSize(160, 120)
        grid.addWidget(button, index // 3, index % 3)
        buttons.append(button)
        s.connect(button, "clicked()", lambda i=index: select(i))
    marker = gui.QGraphicsRectItem(0.0, 0.0, 160.0, 120.0, root)
    marker.setPen(gui.QPen(gui.QColor("#edd888"), 4))
    marker.setBrush(gui.QBrush(core.Qt.NoBrush))
    marker.setZValue(5.0)
    animation = core.QPropertyAnimation(root, core.QByteArray(b"rotation"), s.window)
    animation.setDuration(260)
    s.handle.cleanup.append(animation.stop)
    s.keep("flip_animation", animation)
    selection_animation = core.QPropertyAnimation(
        root, core.QByteArray(b"opacity"), s.window
    )
    selection_animation.setDuration(140)
    s.handle.cleanup.append(selection_animation.stop)
    machine = core.QStateMachine(s.window)
    front_state = core.QState(machine)
    back_state = core.QState(machine)
    front_state.assignProperty(front_proxy, "visible", True)
    front_state.assignProperty(back_proxy, "visible", False)
    back_state.assignProperty(front_proxy, "visible", False)
    back_state.assignProperty(back_proxy, "visible", True)
    machine.setInitialState(front_state)
    front_state.addTransition(front, "windowTitleChanged(QString)", back_state)
    back_state.addTransition(back, "windowTitleChanged(QString)", front_state)
    machine.start()
    s.handle.cleanup.append(machine.stop)
    s.keep("state_machine", machine)

    def select(index):
        s.state["selection"] = max(0, min(8, index))
        marker.setPos(
            30.0 + s.state["selection"] % 3 * 166.0,
            30.0 + s.state["selection"] // 3 * 126.0,
        )
        selection_animation.stop()
        selection_animation.setStartValue(0.7)
        selection_animation.setEndValue(1.0)
        selection_animation.start()

    def flip():
        s.state["back"] = not s.state["back"]
        s.state["history"].append(s.state["selection"])
        animation.stop()
        animation.setStartValue(-7.0 if s.state["back"] else 7.0)
        animation.setEndValue(0.0)
        animation.start()
        front_proxy.setVisible(not s.state["back"])
        back_proxy.setVisible(s.state["back"])
        marker.setVisible(not s.state["back"])
        (front if s.state["back"] else back).setWindowTitle(
            str(len(s.state["history"]))
        )

    class View(gui.QGraphicsView):
        def keyPressEvent(self, event):
            key = event.key()
            index = s.state["selection"]
            if key in (core.Qt.Key_Return, core.Qt.Key_Enter):
                flip()
                event.accept()
                return
            if not s.state["back"]:
                row, column = divmod(index, 3)
                if key == core.Qt.Key_Left:
                    column = max(0, column - 1)
                elif key == core.Qt.Key_Right:
                    column = min(2, column + 1)
                elif key == core.Qt.Key_Up:
                    row = max(0, row - 1)
                elif key == core.Qt.Key_Down:
                    row = min(2, row + 1)
                else:
                    gui.QGraphicsView.keyPressEvent(self, event)
                    return
                select(row * 3 + column)
                event.accept()
                return
            gui.QGraphicsView.keyPressEvent(self, event)

        def resizeEvent(self, event):
            gui.QGraphicsView.resizeEvent(self, event)
            self.fitInView(value(scene, "sceneRect"), core.Qt.KeepAspectRatio)

    view = s.keep("view", View(scene, s.panel))
    s.layout.addWidget(view)
    s.keep("select", select)
    s.keep("flip", flip)
    s.keep("title", title)
    s.keep("date", date)
    s.keep("choices", choices)
    select(4)
