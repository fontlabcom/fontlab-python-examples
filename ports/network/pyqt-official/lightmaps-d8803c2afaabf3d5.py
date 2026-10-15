# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/d8803c2afaabf3d5.md
# this_file: ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py
TITLE = "Local schematic map"
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


import math


def mercator(latitude, longitude, zoom):
    latitude = max(-85.05112878, min(85.05112878, float(latitude)))
    longitude = (float(longitude) + 180) % 360 - 180
    scale = 2**zoom
    sine = math.sin(math.radians(latitude))
    return (longitude + 180) / 360 * scale, (
        1 - math.log((1 + sine) / (1 - sine)) / (2 * math.pi)
    ) / 2 * scale


def configure(s):
    gui, core = s.gui, s.core
    peer = http_peer(s)
    manager = network_manager(s)
    cache = {}
    replies = {}
    presets = [
        ("Harbour", 53.4, -3.0),
        ("Hill town", 45.7, 7.7),
        ("Garden city", 35.7, 139.7),
    ]
    s.state.update(
        zoom=5,
        center=list(mercator(53.4, -3.0, 5)),
        night=False,
        magnifier=False,
        requests=0,
        cache=0,
    )
    pointer = [core.QPoint(200, 180)]
    drag_origin = [None]

    def request_tile(x, y):
        key = (x % (2 ** s.state["zoom"]), max(0, min(2 ** s.state["zoom"] - 1, y)))
        if key in cache or key in replies:
            return
        text = (
            "http://"
            + peer.host
            + ":"
            + str(peer.port)
            + "/tile/"
            + str(key[0])
            + "/"
            + str(key[1])
        )
        local_url(text, peer)
        reply = manager.get(request_for(s, text))
        replies[key] = reply
        s.state["requests"] += 1

        def done():
            if replies.get(key) is not reply:
                return
            if not reply.error() and not reply.attribute(
                s.qt.QtNetwork.QNetworkRequest.RedirectionTargetAttribute
            ):
                image = gui.QImage()
                if image.loadFromData(core.QByteArray(reply.readAll().data()), "PNG"):
                    cache[key] = gui.QPixmap.fromImage(image)
            replies.pop(key, None)
            retire_reply(s, reply)
            s.state["cache"] = len(cache)
            canvas.update()

        s.connect(reply, "finished()", done)

    def fetch():
        cx, cy = s.state["center"]
        for dy in range(-2, 3):
            for dx in range(-3, 4):
                request_tile(int(cx) + dx, int(cy) + dy)

    def pan(dx, dy):
        center = s.state["center"]
        center[0] += dx / 128
        center[1] += dy / 128
        center[1] = max(0, min(2 ** s.state["zoom"] - 1, center[1]))
        fetch()
        canvas.update()

    class Canvas(gui.QWidget):
        def paintEvent(self, event):
            gui.QWidget.paintEvent(self, event)
            p = gui.QPainter(self)
            try:
                p.fillRect(
                    value(self, "rect"),
                    gui.QColor("#172535" if s.state["night"] else "#dce8df"),
                )
                cx, cy = s.state["center"]
                for (x, y), picture in cache.items():
                    px = (x - cx) * 128 + int(value(self, "width")) / 2
                    py = (y - cy) * 128 + int(value(self, "height")) / 2
                    p.drawPixmap(int(px), int(py), 128, 128, picture)
                if s.state["night"]:
                    p.fillRect(value(self, "rect"), gui.QColor(0, 20, 55, 110))
                if s.state["magnifier"]:
                    x, y = float(pointer[0].x()), float(pointer[0].y())
                    p.save()
                    clip = gui.QPainterPath()
                    clip.addEllipse(core.QPointF(x, y), 80.0, 80.0)
                    p.setClipPath(clip)
                    p.translate(x, y)
                    p.scale(2.0, 2.0)
                    p.translate(-x, -y)
                    for (tx, ty), picture in cache.items():
                        p.drawPixmap(
                            int((tx - cx) * 128 + int(value(self, "width")) / 2),
                            int((ty - cy) * 128 + int(value(self, "height")) / 2),
                            128,
                            128,
                            picture,
                        )
                    p.restore()
                    feather = gui.QRadialGradient(x, y, 84.0)
                    feather.setColorAt(0.8, gui.QColor(255, 255, 255, 0))
                    feather.setColorAt(1.0, gui.QColor(40, 50, 60, 180))
                    p.setBrush(gui.QBrush(feather))
                    p.drawEllipse(core.QPointF(x, y), 84.0, 84.0)
            finally:
                p.end()

        def mousePressEvent(self, event):
            pointer[0] = event.pos()
            drag_origin[0] = event.pos()
            hold.start(400)

        def mouseMoveEvent(self, event):
            if drag_origin[0] is not None:
                point = event.pos()
                old = drag_origin[0]
                dx, dy = int(old.x()) - int(point.x()), int(old.y()) - int(point.y())
                if abs(dx) + abs(dy) > 2:
                    hold.stop()
                    s.state["magnifier"] = False
                pan(dx, dy)
                drag_origin[0] = point
                pointer[0] = point

        def mouseReleaseEvent(self, event):
            hold.stop()
            drag_origin[0] = None
            s.state["magnifier"] = False
            self.update()

        def keyPressEvent(self, event):
            moves = {
                core.Qt.Key_Left: (-64, 0),
                core.Qt.Key_Right: (64, 0),
                core.Qt.Key_Up: (0, -64),
                core.Qt.Key_Down: (0, 64),
            }
            if event.key() in moves:
                pan(*moves[event.key()])
                event.accept()
            else:
                gui.QWidget.keyPressEvent(self, event)

    canvas = s.keep("map", Canvas(s.panel))
    canvas.setMinimumSize(560, 360)
    canvas.setFocusPolicy(core.Qt.StrongFocus)
    s.layout.addWidget(canvas)

    def magnify():
        s.state["magnifier"] = True
        canvas.update()

    hold = s.timer("hold", magnify, 400, start=False, once=True)

    def city(index):
        _, lat, lon = presets[index]
        s.state["center"] = list(mercator(lat, lon, s.state["zoom"]))
        fetch()
        canvas.update()

    s.combo("City", [entry[0] for entry in presets], city)

    def night():
        s.state["night"] = not s.state["night"]
        canvas.update()

    s.button("Night", night)
    s.button(
        "Information",
        lambda: s.message(
            "Illustrative map tiles served by this example's local peer."
        ),
    )

    def cancel_replies():
        for reply in list(replies.values()):
            reply.abort()
        replies.clear()

    s.handle.cleanup.append(cancel_replies)
    s.keep("pan", pan)
    s.keep("city", city)
    s.keep("fetch", fetch)
    s.keep("cache", cache)
    s.timer("initial_tiles", fetch, 0, once=True)
