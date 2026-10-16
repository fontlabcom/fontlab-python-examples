# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/409f3d46a9555f23.md
# this_file: ports/network/pyqt-official/http-409f3d46a9555f23.py
TITLE = "Owned sample download"
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


import zlib
from urllib.parse import urlsplit

FIXTURE = ("An owned local sample.\nNo outside service is contacted.\n" * 96).encode(
    "utf-8"
)


def tile_png(x, y):
    width = height = 128
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        for column in range(width):
            road = column in range(56, 64) or row in range(76, 84)
            raw.extend(
                (225, 207, 154)
                if road
                else (170 + (x % 4) * 12, 200 + (y % 3) * 10, 180)
            )

    def chunk(kind, data):
        return (
            struct.pack("!I", len(data))
            + kind
            + data
            + struct.pack("!I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw)))
        + chunk(b"IEND", b"")
    )


def http_peer(s):
    def serve(connection, stop, publish):
        incoming = bytearray()
        deadline = time.monotonic() + 2
        while b"\r\n\r\n" not in incoming:
            if stop.is_set() or time.monotonic() > deadline:
                return
            try:
                data = connection.recv(4096)
            except TimeoutError:
                continue
            if not data or len(incoming) > 16384:
                return
            incoming.extend(data)
        parts = bytes(incoming).split(b"\r\n", 1)[0].decode("ascii").split()
        route = parts[1]
        status = "200 OK"
        content_type = "text/plain; charset=utf-8"
        headers = b""
        body = FIXTURE
        if route.startswith("/tile/"):
            pieces = route.split("/")
            try:
                body = tile_png(int(pieces[-2]), int(pieces[-1]))
            except (ValueError, IndexError):
                status = "400 Bad Request"
                body = b"Invalid tile"
            content_type = "image/png"
        elif route == "/redirect":
            status = "302 Found"
            body = b""
            headers = b"Location: https://example.invalid/\r\n"
        elif route == "/error":
            status = "503 Service Unavailable"
            body = b"Owned failure"
        elif route != "/sample":
            status = "404 Not Found"
            body = b"Unknown owned route"
        connection.sendall(
            b"HTTP/1.1 "
            + status.encode()
            + b"\r\nContent-Type: "
            + content_type.encode()
            + b"\r\n"
            + headers
            + b"Content-Length: "
            + str(len(body)).encode()
            + b"\r\nConnection: close\r\n\r\n"
        )
        for offset in range(0, len(body), 1024):
            if stop.is_set():
                return
            connection.sendall(body[offset : offset + 1024])
        publish(("http", route))

    return attach_peer(s, serve)


def local_url(text, peer):
    url = urlsplit(str(text))
    if (
        url.scheme != "http"
        or url.hostname != peer.host
        or url.port != peer.port
        or url.username is not None
        or url.password is not None
        or url.fragment
    ):
        raise ValueError("Use this example's numeric HTTP endpoint")
    return url


def network_manager(s):
    manager = s.qt.QtNetwork.QNetworkAccessManager(s.window)
    manager.setProxy(s.qt.QtNetwork.QNetworkProxy(s.qt.QtNetwork.QNetworkProxy.NoProxy))
    return s.keep("network_manager", manager)


def request_for(s, text):
    request = s.qt.QtNetwork.QNetworkRequest(s.core.QUrl(text))
    request.setAttribute(s.qt.QtNetwork.QNetworkRequest.FollowRedirectsAttribute, False)
    return request


def retire_reply(s, reply):
    for obj, signature, slot in list(s.handle.connections):
        if obj is reply:
            obj.disconnect(signature, slot)
            s.handle.connections.remove((obj, signature, slot))
    reply.deleteLater()


def configure(s):
    peer = http_peer(s)
    manager = network_manager(s)
    base = "http://" + peer.host + ":" + str(peer.port)
    url_control = s.keep("url", s.gui.QLineEdit(base + "/sample", s.panel))
    s.layout.addWidget(url_control)
    status = s.keep("status", s.gui.QLabel("Ready", s.panel))
    s.layout.addWidget(status)
    s.state.update(active=False, bytes=0, error="", output=None)
    active = [None]
    output = [None]
    progress = [None]
    stream = [None]

    def cancel():
        reply = active[0]
        active[0] = None
        if reply is not None:
            reply.abort()
            retire_reply(s, reply)
        if stream[0] is not None:
            stream[0].close()
            stream[0] = None
        if output[0] is not None:
            output[0].unlink(missing_ok=True)
        if progress[0] is not None:
            progress[0].hide()
        s.state["active"] = False
        button.setEnabled(True)

    def fail(message):
        cancel()
        s.state["error"] = message
        status.setText(message)

    def download(text=None):
        if s.state["active"]:
            return False
        text = str(value(url_control, "text")) if text is None else str(text)
        try:
            parsed = local_url(text, peer)
            if parsed.path not in ("/sample", "/error", "/redirect") or parsed.query:
                raise ValueError("Unknown owned download")
        except (ValueError, TypeError) as error:
            fail(str(error))
            return False
        s.state.update(active=True, bytes=0, error="", output=None)
        button.setEnabled(False)
        output[0] = s.root() / "sample.part"
        try:
            stream[0] = output[0].open("wb")
        except OSError as error:
            fail(str(error))
            return False
        box = s.gui.QProgressDialog("Receiving local sample", "Cancel", 0, 0, s.window)
        box.setAutoClose(False)
        progress[0] = box
        s.connect(box, "canceled()", cancel)
        s.dialog(box)
        try:
            reply = manager.get(request_for(s, text))
        except (OSError, ValueError, RuntimeError) as error:
            fail(str(error))
            return False
        active[0] = reply

        def consume():
            if active[0] is not reply:
                return
            data = reply.readAll().data()
            try:
                stream[0].write(data)
            except OSError as error:
                fail(str(error))
                return
            s.state["bytes"] += len(data)

        def finish():
            if active[0] is not reply:
                return
            consume()
            if active[0] is not reply:
                return
            redirect = reply.attribute(
                s.qt.QtNetwork.QNetworkRequest.RedirectionTargetAttribute
            )
            if redirect or reply.error():
                return fail("Download rejected a redirect or HTTP failure")
            final = s.root() / "sample.txt"
            try:
                stream[0].close()
                stream[0] = None
                output[0].replace(final)
            except OSError as error:
                fail(str(error))
                return
            output[0] = None
            active[0] = None
            retire_reply(s, reply)
            box.hide()
            s.state.update(active=False, output=str(final))
            button.setEnabled(True)
            status.setText("Saved " + str(s.state["bytes"]) + " bytes")

        s.connect(reply, "readyRead()", consume)
        s.connect(reply, "finished()", finish)
        deadline.start(3000)
        return True

    button = s.button("Download", download)
    s.button("Quit", s.handle.close)
    deadline = s.timer(
        "deadline",
        lambda: fail("Download timed out") if s.state["active"] else None,
        3000,
        start=False,
        once=True,
    )
    s.handle.cleanup.insert(1, cancel)
    s.keep("download", download)
    s.keep("cancel", cancel)
