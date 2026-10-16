# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/fa6823667fdb918f.md
# this_file: ports/draganddrop/pyqt-official/dropsite-fa6823667fdb918f.py
TITLE = "Drop inspector"
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
    s.state.update(highlight=False, formats=[])
    table = s.keep("formats", gui.QTableWidget(0, 2, s.panel))
    table.setHorizontalHeaderLabels(["MIME type", "Preview"])

    def inspect_mime(mime):
        formats = [str(f) for f in mime.formats()]
        table.setRowCount(len(formats))
        for i, format_name in enumerate(formats):
            raw = mime.data(format_name).data()
            preview = raw[:160].decode("utf-8", errors="replace")
            table.setItem(i, 0, gui.QTableWidgetItem(format_name))
            table.setItem(i, 1, gui.QTableWidgetItem(preview))
        s.state["formats"] = formats
        if mime.hasImage():
            area.setPixmap(gui.QPixmap.fromImage(gui.QImage(mime.imageData())))
        elif mime.hasHtml():
            area.setTextFormat(core.Qt.RichText)
            area.setText(str(mime.html()))
        elif mime.hasText():
            area.setTextFormat(core.Qt.PlainText)
            area.setText(str(mime.text()))
        elif mime.hasUrls():
            area.setTextFormat(core.Qt.PlainText)
            area.setText("\n".join(str(url.toString()) for url in mime.urls()))
        else:
            area.setTextFormat(core.Qt.PlainText)
            area.setText("Binary data received")

    class Area(gui.QLabel):
        def dragEnterEvent(self, event):
            s.state["highlight"] = True
            self.setStyleSheet("background: #dcebd4; padding: 24px")
            event.acceptProposedAction()

        def dragLeaveEvent(self, event):
            s.state["highlight"] = False
            self.setStyleSheet("")
            event.accept()

        def dropEvent(self, event):
            self.clear()
            inspect_mime(event.mimeData())
            s.state["highlight"] = False
            self.setStyleSheet("")
            event.acceptProposedAction()

    area = s.keep("area", Area("Drop content here", s.panel))
    area.setMinimumHeight(200)
    area.setAcceptDrops(True)
    s.layout.addWidget(area)
    s.layout.addWidget(table)

    def clear():
        area.clear()
        table.setRowCount(0)
        s.state.update(highlight=False, formats=[])

    s.button("Clear", clear)
    s.button("Quit", s.handle.close)
    s.keep("inspect_mime", inspect_mime)
