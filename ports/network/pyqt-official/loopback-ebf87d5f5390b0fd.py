# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ebf87d5f5390b0fd.md
# this_file: ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py
TITLE = "Fifty mebibyte loopback"
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


import queue
import socket
import struct
import threading
import time


class Listener:
    """Bounded serial loopback peer; no native object crosses the thread boundary."""

    def __init__(self, serve):
        self.stop = threading.Event()
        self.events = queue.Queue(32)
        self.lock = threading.Lock()
        self.active = set()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind(("127.0.0.1", 0))
            self.socket.listen(8)
            self.socket.settimeout(0.1)
        except BaseException:
            self.socket.close()
            raise
        self.host, self.port = self.socket.getsockname()
        self.serve = serve
        self.thread = threading.Thread(
            target=self.run, name="owned-loopback-peer", daemon=True
        )

    def publish(self, item):
        try:
            self.events.put_nowait(item)
        except queue.Full:
            try:
                self.events.get_nowait()
            except queue.Empty:
                pass
            try:
                self.events.put_nowait(item)
            except queue.Full:
                pass

    def run(self):
        while not self.stop.is_set():
            try:
                connection, _ = self.socket.accept()
            except TimeoutError:
                continue
            except OSError:
                break
            with self.lock:
                if self.stop.is_set():
                    connection.close()
                    break
                self.active.add(connection)
            try:
                connection.settimeout(0.1)
                self.serve(connection, self.stop, self.publish)
            except (OSError, ValueError, UnicodeError) as error:
                if not self.stop.is_set():
                    self.publish(("error", str(error)))
            finally:
                with self.lock:
                    self.active.discard(connection)
                connection.close()

    def start(self):
        self.thread.start()
        return self

    def close(self):
        self.stop.set()
        self.socket.close()
        with self.lock:
            for connection in self.active:
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                connection.close()
        if self.thread.ident is not None:
            self.thread.join(2)
            if self.thread.is_alive():
                raise RuntimeError("The owned peer has not stopped")


FORTUNES = (
    "A clean curve begins with a patient eye.",
    "Leave space for the next good idea.",
    "Tiny proofs prevent large surprises.",
    "Tomorrow may bring a gentler baseline.",
    "A well placed pause can change a page.",
    "Zażółć the quiet corner with a little colour.",
    "One small revision is still progress. 🌿",
)


def fortune_frame(text):
    encoded = text.encode("utf-16-be")
    body = struct.pack("!I", len(encoded)) + encoded
    if len(body) > 65535:
        raise ValueError("Fortune is too large")
    return struct.pack("!H", len(body)) + body


def take_frame(buffer):
    if len(buffer) < 2:
        return None
    length = struct.unpack("!H", buffer[:2])[0]
    if length < 4:
        raise ValueError("Invalid fortune length")
    if len(buffer) < length + 2:
        return None
    body = buffer[2 : 2 + length]
    count = struct.unpack("!I", body[:4])[0]
    if count != length - 4 or count % 2:
        raise ValueError("Invalid Unicode payload")
    text = bytes(body[4:]).decode("utf-16-be")
    del buffer[: length + 2]
    return text


def attach_peer(s, serve):
    peer = Listener(serve)
    s.handle.cleanup.append(peer.close)
    s.keep("peer", peer)
    peer.start()
    s.state["endpoint"] = [peer.host, peer.port]
    return peer


TOTAL = 50 * 1024 * 1024
CHUNK = b"FontLab loopback\n" * (65536 // 17) + b"x" * (65536 % 17)


def configure(s):
    gui, core, network = s.gui, s.core, s.qt.QtNetwork

    def serve(connection, stop, publish):
        count = 0
        deadline = time.monotonic() + 15
        while count < TOTAL and not stop.is_set() and time.monotonic() < deadline:
            try:
                data = connection.recv(min(65536, TOTAL - count))
            except TimeoutError:
                continue
            if not data:
                if count < TOTAL:
                    publish(("error", "Sender closed early"))
                return
            count += len(data)
            publish(("received", count))
        if count == TOTAL:
            publish(("complete", count))

    peer = attach_peer(s, serve)
    s.state.update(sent=0, received=0, active=False, error="")
    labels = []
    bars = []
    for text in ("Client", "Server"):
        label = gui.QLabel(text + ": idle", s.panel)
        s.layout.addWidget(label)
        labels.append(label)
        bar = s.keep(text, gui.QProgressBar(s.panel))
        bar.setRange(0, TOTAL)
        s.layout.addWidget(bar)
        bars.append(bar)
    client = network.QTcpSocket(s.window)
    client.setProxy(network.QNetworkProxy(network.QNetworkProxy.NoProxy))
    s.keep("socket", client)
    s.handle.cleanup.append(client.abort)
    offset = [0]
    pending = [b""]
    connected = [False]
    outstanding = [0]

    def failure(message):
        client.abort()
        connected[0] = False
        sender.stop()
        s.state.update(active=False, error=message)
        start_button.setEnabled(True)
        labels[0].setText(message)

    s.connect(client, "connected()", lambda: connected.__setitem__(0, True))
    s.connect(
        client,
        "error(QAbstractSocket::SocketError)",
        lambda *args: failure(str(client.errorString())) if s.state["active"] else None,
    )

    def write():
        if not s.state["active"]:
            return
        if (
            not connected[0]
            and client.state() != network.QAbstractSocket.ConnectedState
        ):
            return
        connected[0] = True
        for _ in range(4):
            if offset[0] >= TOTAL:
                sender.stop()
                break
            if outstanding[0] >= 262144:
                break
            data = pending[0] or CHUNK[: min(65536, TOTAL - offset[0])]
            count = int(client.write(core.QByteArray(data)))
            if count < 0:
                failure(str(client.errorString()))
                return
            if count == 0:
                break
            offset[0] += count
            outstanding[0] += count
            pending[0] = data[count:]
        s.state["sent"] = offset[0]
        bars[0].setValue(offset[0])
        labels[0].setText("Sent " + str(offset[0]))

    def acknowledged(count):
        outstanding[0] = max(0, outstanding[0] - int(count))

    s.connect(client, "bytesWritten(qint64)", acknowledged)

    def poll():
        for _ in range(32):
            try:
                kind, data = peer.events.get_nowait()
            except queue.Empty:
                break
            if kind in ("received", "complete"):
                s.state["received"] = data
                bars[1].setValue(data)
                labels[1].setText("Received " + str(data))
            if kind == "complete":
                s.state["active"] = False
                start_button.setEnabled(True)
                sender.stop()
                client.abort()
            elif kind == "error":
                failure(data)

    def start():
        if s.state["active"]:
            return False
        client.abort()
        offset[0] = 0
        pending[0] = b""
        connected[0] = False
        outstanding[0] = 0
        while not peer.events.empty():
            peer.events.get_nowait()
        s.state.update(sent=0, received=0, active=True, error="")
        start_button.setEnabled(False)
        client.connectToHost(peer.host, peer.port)
        sender.start(1)
        return True

    sender = s.timer("send", write, 1, start=False)
    s.timer("progress", poll, 30)
    start_button = s.button("Start", start)
    s.button("Quit", s.handle.close)
    s.keep("start", start)
    s.keep("write", write)
    s.keep("poll", poll)
