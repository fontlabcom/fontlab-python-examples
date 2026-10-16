# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/60d40ce5671653cf.md
# this_file: ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
TITLE = "Menu actions"
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


def configure(s):
    gui, core = s.gui, s.core
    report = s.keep("report", gui.QLabel("Choose an action", s.panel))
    report.setTextFormat(core.Qt.PlainText)
    s.layout.addWidget(report)
    bar = s.window.menuBar()
    file = bar.addMenu("File")
    edit = bar.addMenu("Edit")
    help_menu = bar.addMenu("Help")

    def show(text):
        report.setText(text)
        s.state["report"] = text

    for name in ("New", "Open", "Save", "Print"):
        s.action(file, name, lambda n=name: show("File / " + n))
    s.action(file, "Exit", s.handle.close)
    for name in ("Undo", "Redo", "Cut", "Copy", "Paste"):
        s.action(edit, name, lambda n=name: show("Edit / " + n))
    format_menu = edit.addMenu("Format")
    for name in ("Bold", "Italic"):
        action = s.action(format_menu, name, lambda n=name: show("Format / " + n), True)
        s.connect(
            action,
            "toggled(bool)",
            lambda checked, n=name: s.state.update({n: bool(checked)}),
        )
    group = s.keep("alignment", gui.QActionGroup(s.window))
    group.setExclusive(True)
    for name in ("Left", "Center", "Right", "Justify"):
        action = s.action(
            format_menu, name, lambda n=name: show("Alignment / " + n), True
        )
        group.addAction(action)
        s.connect(
            action, "triggered(bool)", lambda *args, n=name: s.state.update(alignment=n)
        )
        if name == "Left":
            action.setChecked(True)
    for name in ("Increase spacing", "Decrease spacing"):
        s.action(format_menu, name, lambda n=name: show("Format / " + n))
    s.action(
        help_menu,
        "About",
        lambda: s.message("Menu roles and independent formatting choices."),
    )
    menu = s.keep("context", gui.QMenu(s.window))
    for name in ("Cut", "Copy", "Paste"):
        s.action(menu, name + " context", lambda n=name: show("Context / " + n))
    s.panel.setContextMenuPolicy(core.Qt.CustomContextMenu)
    s.connect(
        s.panel,
        "customContextMenuRequested(QPoint)",
        lambda point: menu.popup(s.panel.mapToGlobal(point)),
    )
