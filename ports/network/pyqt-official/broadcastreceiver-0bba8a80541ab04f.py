# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0bba8a80541ab04f.md
# this_file: ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py
TITLE = "Local datagrams"
MAIN = False
MODE = "receiver"

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


import socket


def configure(s):
    gui, core = s.gui, s.core
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("127.0.0.1", 0))
    receiver.setblocking(False)
    s.handle.cleanup.append(receiver.close)
    host, port = receiver.getsockname()
    sender = s.qt.QtNetwork.QUdpSocket(s.window)
    sender.setProxy(s.qt.QtNetwork.QNetworkProxy(s.qt.QtNetwork.QNetworkProxy.NoProxy))
    s.handle.cleanup.append(sender.close)
    s.keep("sender", sender)
    s.keep("receiver", receiver)
    status = s.keep("status", gui.QLabel("Waiting for local datagrams", s.panel))
    s.layout.addWidget(status)
    messages = []
    s.state.update(endpoint=[host, port], sent=0, received=0, messages=messages)

    def sample_send():
        s.state["sent"] += 1
        text = "Local note " + str(s.state["sent"]) + ": a small signal arrives."
        data = core.QByteArray(text.encode("utf-8"))
        address = s.qt.QtNetwork.QHostAddress(s.qt.QtNetwork.QHostAddress.LocalHost)
        if sender.writeDatagram(data, address, port) < 0:
            s.state["error"] = str(sender.errorString())
        if MODE == "sender":
            status.setText("Sent " + str(s.state["sent"]))

    def poll():
        for _ in range(16):
            try:
                data, _peer = receiver.recvfrom(65536)
            except BlockingIOError:
                break
            text = data.decode("utf-8", errors="replace")
            messages.append(text)
            del messages[:-100]
            s.state["received"] += 1
            if MODE == "receiver":
                status.setText(text)

    interval = s.timer("send_timer", sample_send, 1000, start=False)
    if MODE == "sender":

        def start():
            if interval.isActive():
                return
            interval.start(1000)
            start_button.setEnabled(False)

        start_button = s.button("Start", start)
        s.keep("start", start)
    s.timer("receive_timer", poll, 30)
    s.button("Quit", s.handle.close)
    s.keep("sample_send", sample_send)
    s.keep("poll", poll)
