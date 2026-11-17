# SPDX-License-Identifier: Apache-2.0
# Clean-room implementations retained from the licensed network ports.
# this_file: lessons/src/fontlab_python_lessons/network_demos.py
"""Owned local peers and lifecycle support for standalone network examples."""
import queue
import socket
import struct
import threading
import time
import zlib
import math
from urllib.parse import urlsplit
from fontlab_python_lessons import qt_demos as S
from fontlab_python_lessons.qt_demos import value


class Session(S.Session):
    """Adapt historical network controls to the current Lessons owner."""

    def __init__(self, qt, title, main=False):
        if not hasattr(qt, "QtNetwork"):
            from PythonQt import QtNetwork
            from types import SimpleNamespace
            qt = SimpleNamespace(QtCore=qt.QtCore, QtGui=qt.QtGui, QtNetwork=QtNetwork)
        super().__init__(qt, title)
        self.gui, self.core = self.g, self.c
        self.handle, self.panel = self.h, self.window
        self.pending = []
        self.vertical()

    def connect(self, obj, signature, callback):
        return self.link(obj, signature, callback)

    def button(self, name, callback, layout=None):
        return super().button(name, name, callback, layout)

    def combo(self, name, items, callback, layout=None):
        control = super().combo(name, items, layout)
        self.link(control, "currentIndexChanged(int)", lambda i: callback(int(i)))
        return control

    def timer(self, name, callback, interval, start=True, once=False):
        return super().timer(name, interval, callback, once, start)

    def root(self):
        return self.temp()

    def dialog(self, dialog):
        self.alert(dialog)
        self.pending.append(dialog)
        dialog.open()
        return dialog

    def message(self, text):
        box = self.gui.QMessageBox(self.window)
        box.setText(str(text))
        return self.dialog(box)

    def finish(self):
        return self.handle

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

def mercator(latitude, longitude, zoom):
    latitude = max(-85.05112878, min(85.05112878, float(latitude)))
    longitude = (float(longitude) + 180) % 360 - 180
    scale = 2**zoom
    sine = math.sin(math.radians(latitude))
    return (longitude + 180) / 360 * scale, (
        1 - math.log((1 + sine) / (1 - sine)) / (2 * math.pi)
    ) / 2 * scale


def build_chat(qt, variant):
    """Compare GUI polling and worker delivery of owned local UDP messages."""
    with S.Session(qt, "Local Chat — " + variant) as s:
        s.vertical()
        name = s.line("name", "Example user")
        message = s.line("message")
        text = s.keep("messages", s.g.QPlainTextEdit(s.window))
        text.setReadOnly(True)
        s.add(text)
        status = s.label("Messages travel only to this panel's loopback socket.")
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.h.cleanup.append(receiver.close)
        receiver.bind(("127.0.0.1", 0))
        receiver.settimeout(0.05)
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.h.cleanup.append(sender.close)
        endpoint = receiver.getsockname()
        received = queue.Queue(64)
        stop = threading.Event()
        s.state.update(variant=variant, sent=0, received=0, endpoint=endpoint)

        def read_one():
            try:
                data, _ = receiver.recvfrom(8192)
                received.put_nowait(data.decode("utf-8"))
            except (TimeoutError, queue.Full):
                pass

        def run():
            while not stop.is_set():
                try:
                    read_one()
                except OSError:
                    return

        def send():
            data = (str(value(name, "text")) + ": " + str(value(message, "text"))).encode("utf-8")
            if len(data) > 8192:
                status.setText("Keep each message below 8192 UTF-8 bytes.")
                return
            try:
                sender.sendto(data, endpoint)
            except OSError as error:
                status.setText(str(error))
                return
            s.state["sent"] += 1
            message.clear()

        def poll():
            if variant == "single_threaded":
                read_one()
            for _ in range(64):
                try:
                    line = received.get_nowait()
                except queue.Empty:
                    break
                text.appendPlainText(line)
                s.state["received"] += 1

        if variant != "single_threaded":
            worker = threading.Thread(target=run, name="local-chat", daemon=True)
            worker.start()

            def close_worker():
                stop.set()
                worker.join(1)
                if worker.is_alive():
                    raise RuntimeError("Chat worker has not stopped")

            s.h.cleanup.insert(0, close_worker)
            s.keep("worker", worker)
        s.link(message, "returnPressed()", send)
        s.button("send", "Send", send)
        s.timer("delivery", 30 if variant == "threadutil" else 1000, poll)
        s.keep("send_message", send)
        s.keep("poll", poll)
        return s.h


FORTUNES = (
    "A clean curve begins with a patient eye.",
    "Leave space for the next good idea.",
    "Tiny proofs prevent large surprises.",
    "Tomorrow may bring a gentler baseline.",
    "A well placed pause can change a page.",
    "Zażółć the quiet corner with a little colour.",
    "One small revision is still progress. 🌿",
)

FIXTURE = ("An owned local sample.\nNo outside service is contacted.\n" * 96).encode(
    "utf-8"
)

TOTAL = 50 * 1024 * 1024

CHUNK = b"FontLab loopback\n" * (65536 // 17) + b"x" * (65536 % 17)
