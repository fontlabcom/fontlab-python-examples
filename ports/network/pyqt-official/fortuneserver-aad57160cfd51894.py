# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/aad57160cfd51894.md
# this_file: ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py
TITLE = "Loopback fortunes"
MAIN = False
MODE = "server"

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


def configure(s):
    import random

    gui, core, network = s.gui, s.core, s.qt.QtNetwork

    def serve(connection, stop, publish):
        packet = fortune_frame(random.choice(FORTUNES))
        # Deliberately fragment both framing and text.
        for index in range(0, len(packet), 3):
            if stop.is_set():
                return
            connection.sendall(packet[index : index + 3])
        publish(("served", len(packet)))

    peer = attach_peer(s, serve)
    status = s.keep(
        "status",
        gui.QLabel("Loopback peer at " + peer.host + ":" + str(peer.port), s.panel),
    )
    status.setTextFormat(core.Qt.PlainText)
    s.layout.addWidget(status)
    s.state.update(fortune="", error="", requests=0, busy=False)
    buffer = bytearray()
    client = [None]
    worker = [None]
    cancel_event = threading.Event()
    worker_results = queue.Queue(1)
    deadline = [0.0]

    def result(text):
        s.state.update(fortune=text, error="", busy=False)
        status.setText(text)
        if client[0] is not None:
            client[0].abort()
        if request_button[0]:
            request_button[0].setEnabled(True)

    def fail(message):
        s.state.update(error=message, busy=False)
        status.setText(message)
        if client[0] is not None:
            client[0].abort()
        if request_button[0]:
            request_button[0].setEnabled(True)

    def receive(data):
        buffer.extend(data)
        try:
            text = take_frame(buffer)
        except (ValueError, UnicodeError) as error:
            fail(str(error))
            return
        if text is not None:
            result(text)

    def cancel():
        cancel_event.set()
        if client[0] is not None:
            client[0].abort()
        if worker[0] is not None:
            worker[0].join(1)
            if worker[0].is_alive():
                raise RuntimeError("Fortune reader has not stopped")
            worker[0] = None
        s.state["busy"] = False

    def blocking_read(host, port, stop, output):
        connection = None
        try:
            connection = socket.create_connection((host, port), timeout=0.2)
            connection.settimeout(0.1)
            received = bytearray()
            end = time.monotonic() + 3
            while not stop.is_set() and time.monotonic() < end:
                try:
                    data = connection.recv(4096)
                except TimeoutError:
                    continue
                if not data:
                    raise ValueError("Peer ended before a complete fortune")
                received.extend(data)
                text = take_frame(received)
                if text is not None:
                    output.put(("fortune", text))
                    return
            if not stop.is_set():
                output.put(("error", "The fortune request timed out"))
        except (OSError, ValueError, UnicodeError) as error:
            if not stop.is_set():
                output.put(("error", str(error)))
        finally:
            if connection is not None:
                connection.close()

    def request(host=None, port=None):
        if s.state["busy"]:
            return False
        host = host if host is not None else str(value(host_control, "text"))
        port = port if port is not None else str(value(port_control, "text"))
        if host != peer.host or str(port) != str(peer.port):
            fail("Use the displayed owned numeric endpoint.")
            return False
        cancel()
        cancel_event.clear()
        buffer.clear()
        while not worker_results.empty():
            worker_results.get_nowait()
        s.state.update(busy=True, requests=s.state["requests"] + 1)
        deadline[0] = time.monotonic() + 3
        if request_button[0]:
            request_button[0].setEnabled(False)
        if MODE == "blocking":
            worker[0] = threading.Thread(
                target=blocking_read,
                args=(peer.host, peer.port, cancel_event, worker_results),
                name="owned-fortune-reader",
                daemon=True,
            )
            worker[0].start()
        else:
            if client[0] is None:
                native = network.QTcpSocket(s.window)
                native.setProxy(network.QNetworkProxy(network.QNetworkProxy.NoProxy))
                client[0] = s.keep("socket", native)
                s.connect(
                    native, "readyRead()", lambda: receive(native.readAll().data())
                )
                s.connect(
                    native,
                    "error(QAbstractSocket::SocketError)",
                    lambda *args: (
                        fail(str(native.errorString())) if s.state["busy"] else None
                    ),
                )
                s.handle.cleanup.append(native.abort)
            client[0].connectToHost(peer.host, peer.port)
        return True

    def poll():
        for _ in range(16):
            try:
                kind, data = worker_results.get_nowait()
            except queue.Empty:
                break
            if kind == "fortune":
                result(data)
            else:
                fail(data)
        if s.state["busy"] and time.monotonic() > deadline[0]:
            cancel()
            fail("The fortune request timed out")

    request_button = [None]
    host_control = s.keep("host", gui.QLineEdit(peer.host, s.panel))
    port_control = s.keep("port", gui.QLineEdit(str(peer.port), s.panel))
    if MODE in ("client", "blocking"):
        s.layout.addWidget(host_control)
        s.layout.addWidget(port_control)
        request_button[0] = s.button("Get Fortune", request)

        def valid(*args):
            request_button[0].setEnabled(
                not s.state["busy"]
                and str(value(host_control, "text")) == peer.host
                and str(value(port_control, "text")) == str(peer.port)
            )

        s.connect(host_control, "textChanged(QString)", valid)
        s.connect(port_control, "textChanged(QString)", valid)
    else:
        host_control.hide()
        port_control.hide()
    s.button("Quit", s.handle.close)
    s.timer("delivery", poll, 30)
    # Cancel readers before stopping the service or deleting their native peers.
    s.handle.cleanup.insert(1, cancel)
    s.keep("request", request)
    s.keep("receive", receive)
    s.keep("poll", poll)
    s.keep("cancel", cancel)
