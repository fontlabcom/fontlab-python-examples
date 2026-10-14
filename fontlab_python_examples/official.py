# this_file: fontlab_python_examples/official.py
# SPDX-License-Identifier: GPL-3.0-only
"""Owned PythonQt boundary for the official examples; no alternative Qt runtime."""

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .handle import ExampleHandle


def read(obj: Any, name: str) -> Any:
    """Qt value types have methods where QObject wrappers expose properties."""
    value = getattr(obj, name)
    return value() if callable(value) else value


def describe_control(obj: Any) -> dict:
    """Read scalar UI state only; never activate a control while inspecting."""
    state = {}
    for name in (
        "windowTitle",
        "text",
        "title",
        "currentText",
        "currentIndex",
        "count",
        "rowCount",
        "columnCount",
        "value",
        "checked",
        "enabled",
    ):
        value = getattr(obj, name, None)
        # Only property values: methods may require arguments or have side effects.
        if isinstance(value, (str, int, float, bool)):
            state[name] = value
    if hasattr(obj, "toPlainText"):
        state["plain_text"] = str(obj.toPlainText())
    if hasattr(obj, "isVisible"):
        state["visible"] = bool(obj.isVisible())
    return state


def pack_values(qt: Any, values: list) -> Any:
    """Encode drag values with native QVariant methods, without stream operators."""
    core = qt.QtCore
    buffer = core.QBuffer()
    try:
        if not buffer.open(core.QIODevice.WriteOnly):
            raise OSError("Cannot open the owned drag buffer")
        stream = core.QDataStream(buffer)
        stream.setVersion(core.QDataStream.Qt_5_0)
        for value in values:
            stream.writeQVariant(value)
        if stream.status() != core.QDataStream.Ok:
            raise ValueError("Cannot encode drag data")
        return core.QByteArray(buffer.data().data())
    finally:
        buffer.close()
        buffer.deleteLater()


def unpack_values(qt: Any, data: Any, expected: tuple = ()) -> list:
    """Decode the ports' versioned native drag format; reject truncated values."""
    core = qt.QtCore
    buffer = core.QBuffer()
    try:
        buffer.setData(data)
        if not buffer.open(core.QIODevice.ReadOnly):
            raise OSError("Cannot open the owned drag buffer")
        stream = core.QDataStream(buffer)
        stream.setVersion(core.QDataStream.Qt_5_0)
        values = []
        while not stream.atEnd():
            values.append(stream.readQVariant())
            if stream.status() != core.QDataStream.Ok:
                raise ValueError("Invalid drag data")
        if expected and (
            not values
            or len(values) % len(expected)
            or any(
                not isinstance(value, expected[index % len(expected)])
                for index, value in enumerate(values)
            )
        ):
            raise ValueError("Unexpected drag value types")
        return values
    finally:
        buffer.close()
        buffer.deleteLater()


class Demo:
    """One build's owner, resource root and explicit signal connections."""

    def __init__(self, qt: Any, path: str, source_id: str) -> None:
        self.qt, self.source_id = qt, source_id
        self.assets = Path(path).parent / "assets" / source_id
        self.handle = None
        self.controls = {}
        self.objects = []
        self.links = []
        self.temporary = None
        self._owned_temporary = None
        self.error = ""
        self.closing = False
        self.dragging = False

    def begin(self, window: Any) -> None:
        if self.handle is None:
            self.handle = ExampleHandle(window, dict)
            self.handle.release.append(self.release)
            self.handle.cleanup.append(self.prepare_close)
            self.handle.after_close.append(self.cleanup_temp)
        elif window is not self.handle.widget:
            from fontlabapp.widgets import OwnedWidget

            self.handle.alerts.append(OwnedWidget(window, window))
        if window.inherits("QWidget"):
            window.setAttribute(self.qt.QtCore.Qt.WA_QuitOnClose, False)
            window.setAttribute(self.qt.QtCore.Qt.WA_DeleteOnClose, False)

    def prepare_close(self) -> None:
        """Keep the drag source alive until the native macOS drag returns."""
        if self.dragging:
            raise RuntimeError("Finish or cancel the drag before closing this example")
        self.closing = True

    def defer(self, name: str, callback: Any) -> Any:
        """Run startup work after returning to the host, using an owned timer.

        Unlike QTimer.singleShot, this retains an explicit connection and a timer
        that named close can stop. A stale callback never touches deleted Qt UI.
        """
        timer = self.remember(name, self.qt.QtCore.QTimer(self.handle.widget))
        timer.setSingleShot(True)

        def run() -> None:
            if self.closing or self.handle.owner.closed:
                return
            timer.stop()
            callback()

        self.connect(timer, "timeout()", run)
        self.handle.cleanup.append(timer.stop)
        timer.start(0)
        return timer

    def drag(self, drag: Any, actions: Any, default: Any = None) -> Any:
        """Use QDrag's native operation, never a QApplication or modal dialog loop.

        Qt documents that QDrag.exec keeps the macOS event loop responsive.
        The parent owns the drag and its MIME object; neither has Python slots.
        """
        self.dragging = True
        try:
            return drag.exec(actions, actions if default is None else default)
        finally:
            self.dragging = False
            drag.deleteLater()

    def owned_path(self, path: str) -> Path:
        """Restrict write destinations; read sources need no ownership check."""
        root = Path(self.temp_dir()).resolve()
        result = Path(path).resolve()
        if not result.is_relative_to(root) or result == root:
            raise ValueError("Choose a file inside this example's temporary directory")
        return result

    def remember(self, name: str, obj: Any) -> Any:
        import inspect

        if not hasattr(obj, "deleteLater") and not inspect.isroutine(obj):
            return obj
        self.controls[name] = obj
        if self.handle is not None:
            self.handle.controls[name] = obj
        return obj

    def transient(self, name: str, obj: Any) -> Any:
        """Expose a Qt-owned editor only until its native destroyed notification."""
        self.remember(name, obj)

        def destroyed(*args: Any) -> None:
            # The wrapper is already invalid: remove references without reading it.
            for key, value in list(self.controls.items()):
                if value is obj:
                    self.controls.pop(key)
                    self.handle.controls.pop(key, None)
            self.links[:] = [entry for entry in self.links if entry[0] is not obj]
            self.handle.connections[:] = [
                entry for entry in self.handle.connections if entry[0] is not obj
            ]
            self.objects[:] = [entry for entry in self.objects if entry[0] is not obj]

        self.connect(obj, "destroyed(QObject*)", destroyed)
        return obj

    def track(self, obj: Any, *references: str) -> None:
        """Retain a subclass and only its explicitly declared Python reference fields.

        PythonQt __dict__ includes native properties, so it is not a safe list of
        Python-owned attributes to clear. Callers name fields created by the port.
        """
        self.objects.append((obj, references))

    def connect(self, obj: Any, signature: str, slot: Any) -> None:
        import inspect

        routed = slot
        try:
            parameters = list(inspect.signature(slot).parameters.values())
        except (ValueError, TypeError):
            parameters = None
        if parameters is not None and not any(
            p.kind == p.VAR_POSITIONAL for p in parameters
        ):
            count = len(
                [
                    p
                    for p in parameters
                    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                ]
            )

            def routed(*args: Any) -> Any:
                return slot(*args[:count])

        self.handle.connect_old(obj, signature, routed)
        self.links.append((obj, signature, slot, routed))

    def disconnect(self, obj: Any, signature: str, slot: Any) -> None:
        for entry in list(self.links):
            if entry[:3] == (obj, signature, slot):
                routed = entry[3]
                obj.disconnect(signature, routed)
                self.handle.connections.remove((obj, signature, routed))
                self.links.remove(entry)

    def forget(self, obj: Any) -> None:
        """Disconnect a dynamic editor/action subtree before Qt destroys it."""
        for child in obj.children():
            self.forget(child)
        for entry in list(self.links):
            if entry[0] is obj:
                self.disconnect(*entry[:3])
        for key, value in list(self.controls.items()):
            if value is obj:
                del self.controls[key]
                self.handle.controls.pop(key, None)

    def action(self, *args: Any, **kwargs: Any) -> Any:
        """QAction property keywords and Python callbacks are applied explicitly."""
        slot = kwargs.pop("triggered", None)
        action = self.qt.QtGui.QAction(*args)
        for key, value in kwargs.items():
            if key == "shortcut":
                value = self.qt.QtGui.QKeySequence(value)
            getattr(action, "set" + key[0].upper() + key[1:])(value)
        if slot is not None:
            signature = (
                "triggered(bool)"
                if getattr(slot, "__name__", "")
                in {"changeStyle", "setFallbacksEnabled"}
                else "triggered()"
            )
            self.connect(action, signature, slot)
        return action

    def close_windows(self) -> None:
        """Close only this example's windows; each editor keeps its own prompt."""
        for owner in [self.handle.owner, *self.handle.alerts]:
            if not owner.closed:
                owner.widget.close()

    def asset(self, name: str) -> str:
        return str(self.assets / name.removeprefix(":/"))

    def load_ui(self, name: str) -> Any:
        """Load exact Designer XML with every declared connection owned by us.

        QUiLoader otherwise installs untracked connections from the XML. Remove
        only that section in the in-memory copy, then reconnect through the
        handle. The pinned asset on disk stays byte-identical to the original.
        """
        import xml.etree.ElementTree as ET

        core = self.qt.QtCore
        document = ET.fromstring(Path(self.asset(name)).read_bytes())
        connections = document.find("connections")
        if connections is not None:
            document.remove(connections)
        source = core.QBuffer()
        loader = self.qt.QtUiTools.QUiLoader()
        window = None
        try:
            source.setData(core.QByteArray(ET.tostring(document, encoding="utf-8")))
            if not source.open(core.QIODevice.ReadOnly):
                raise RuntimeError("Cannot open owned Designer buffer")
            window = loader.load(source)
            if window is None:
                raise RuntimeError("Cannot load Designer UI: " + name)
            self.begin(window)
            root_name = document.find("widget").get("name")

            def child(key: str) -> Any:
                obj = (
                    window
                    if key == root_name
                    else window.findChild(self.qt.private.QObject, key)
                )
                if obj is None:
                    raise RuntimeError("Designer UI is missing control: " + key)
                return self.remember(key, obj)

            for node in document.iter("widget"):
                child(node.get("name"))
            for entry in connections if connections is not None else ():
                sender = child(entry.findtext("sender"))
                receiver = child(entry.findtext("receiver"))
                slot = getattr(receiver, entry.findtext("slot").split("(")[0])
                self.connect(sender, entry.findtext("signal"), slot)
            return window
        finally:
            source.close()
            source.deleteLater()
            loader.deleteLater()

    def temp_dir(
        self, *, prefix: str = "fontlab-official-", directory: str | None = None
    ) -> str:
        if self.temporary is None:
            if self.closing:
                raise RuntimeError("This example is closing")
            self.temporary = TemporaryDirectory(prefix=prefix, dir=directory)
            info = Path(self.temporary.name).stat()
            self._owned_temporary = (
                self.temporary,
                self.temporary.name,
                (info.st_dev, info.st_ino),
            )
        return self.temporary.name

    def cleanup_temp(self) -> None:
        """Remove only our exact mkdtemp directory, after owned windows close."""
        if self._owned_temporary is None:
            return
        temporary, name, identity = self._owned_temporary
        if (
            temporary is not self.temporary
            or temporary.name != name
            or Path(name).is_symlink()
        ):
            raise RuntimeError("The example's temporary directory ownership changed")
        if Path(name).exists():
            info = Path(name).stat()
            if (info.st_dev, info.st_ino) != identity:
                raise RuntimeError(
                    "The example's temporary directory ownership changed"
                )
        temporary.cleanup()
        self.temporary = self._owned_temporary = None

    def settings(self, *args: Any) -> Any:
        """All settings scopes, including location previews, stay in owned INIs."""
        import hashlib
        import shutil

        key = hashlib.sha256(repr(args).encode()).hexdigest()[:16]
        target = self.owned_path(str(Path(self.temp_dir()) / (key + ".ini")))
        if (
            args
            and isinstance(args[0], str)
            and Path(args[0]).is_file()
            and not target.exists()
        ):
            shutil.copyfile(args[0], target)
        result = self.qt.QtCore.QSettings(
            str(target), self.qt.QtCore.QSettings.IniFormat
        )
        result.setFallbacksEnabled(False)
        result.setParent(self.handle.widget)
        self.handle.cleanup.append(result.sync)
        return result

    def dialog(self, box: Any, callback: Any = None, *, modal: bool = True) -> Any:
        """Retain every asynchronous dialog until disconnect-before-delete cleanup."""
        from fontlabapp.widgets import OwnedWidget

        if not any(owner.widget is box for owner in self.handle.alerts):
            self.handle.alerts.append(OwnedWidget(box, box))
        self.controls["active_dialog"] = box
        self.handle.controls["active_dialog"] = box
        box.setAttribute(self.qt.QtCore.Qt.WA_DeleteOnClose, False)
        box.setAttribute(self.qt.QtCore.Qt.WA_QuitOnClose, False)
        box.setWindowModality(
            self.qt.QtCore.Qt.WindowModal if modal else self.qt.QtCore.Qt.NonModal
        )
        if callback is not None:
            self.connect(box, "accepted()", callback)
        if modal:
            box.open()
        else:
            box.show()
        return box

    def choose(
        self,
        parent: Any,
        callback: Any,
        mode: str = "open",
        title: str = "",
        directory: str = "",
        filters: str = "",
        native: bool = False,
        owned: bool = False,
    ) -> Any:
        """Choose readable inputs freely; confine saves to the owned directory.

        The owned flag selects the initial directory for open dialogs only.
        """
        gui = self.qt.QtGui
        box = gui.QFileDialog(parent)
        box.setWindowTitle(title or ("Save As" if mode == "save" else "Open"))
        box.setOption(gui.QFileDialog.DontUseNativeDialog, not native)
        box.setFileMode(
            {
                "open": gui.QFileDialog.ExistingFile,
                "many": gui.QFileDialog.ExistingFiles,
                "directory": gui.QFileDialog.Directory,
                "save": gui.QFileDialog.AnyFile,
            }[mode]
        )
        if mode == "save":
            box.setAcceptMode(gui.QFileDialog.AcceptSave)
        if directory or owned or mode == "save":
            box.setDirectory(directory or self.temp_dir())
        if filters:
            box.setNameFilter(filters)

        def selected() -> None:
            paths = list(box.selectedFiles())
            if paths:
                if mode == "save":
                    try:
                        paths = [str(self.owned_path(str(path))) for path in paths]
                    except ValueError as error:
                        self.error = str(error)
                        self.message(parent, "File path refused", self.error)
                        return
                callback(paths if mode == "many" else str(paths[0]))

        return self.dialog(box, selected, modal=False)

    def message(
        self,
        parent: Any,
        title: str,
        text: str,
        buttons: Any = None,
        callback: Any = None,
    ) -> Any:
        gui = self.qt.QtGui
        box = gui.QMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(gui.QMessageBox.Ok if buttons is None else buttons)
        if callback is not None:
            self.connect(
                box,
                "buttonClicked(QAbstractButton*)",
                lambda button: callback(box.standardButton(button)),
            )
        return self.dialog(box)

    def color_dialog(self, parent: Any, color: Any, callback: Any) -> Any:
        """Choose a value colour asynchronously and retain the accepted callback."""
        box = self.qt.QtGui.QColorDialog(parent)
        box.setCurrentColor(color)
        return self.dialog(box, lambda: callback(box.selectedColor()))

    def pdf_printer(self, path: str = "") -> Any:
        """Start every owned print operation with PDF output, never a host printer."""
        gui = self.qt.QtGui
        printer = gui.QPrinter(gui.QPrinter.HighResolution)
        printer.setOutputFormat(gui.QPrinter.PdfFormat)
        printer.setOutputFileName(
            str(self.owned_path(path or str(Path(self.temp_dir()) / "output.pdf")))
        )
        return printer

    def print_dialog(self, parent: Any, render: Any) -> Any:
        """Open an owned print dialog only on explicit action; inspection is inert."""
        box = self.qt.QtGui.QPrintDialog(parent)
        # The dialog owns its native printer until actual deferred destruction.
        printer = box.printer()
        printer.setOutputFormat(self.qt.QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(str(Path(self.temp_dir()) / "output.pdf"))
        return self.dialog(box, lambda: self.render_pdf(parent, printer, render))

    def render_pdf(self, parent: Any, printer: Any, render: Any) -> None:
        """Recheck the output selected in print/preview UI before writing."""
        try:
            self.owned_path(str(read(printer, "outputFileName")))
            if read(printer, "outputFormat") != self.qt.QtGui.QPrinter.PdfFormat:
                raise ValueError(
                    "Choose PDF output inside this example's temporary directory"
                )
        except ValueError as error:
            self.error = str(error)
            self.message(parent, "Print path refused", self.error)
            return
        render(printer)

    def print_document(self, parent: Any, document: Any) -> Any:
        """Preserve document printing through an asynchronous owned print dialog."""
        return self.print_dialog(parent, lambda printer: document.print(printer))

    def finish(self, window: Any, extra: Any = dict) -> ExampleHandle:
        self.begin(window)
        self.handle.controls.update(self.controls)
        self.handle.controls["window"] = window
        self.handle.inspect_ui = lambda: {
            "title": str(
                read(window, "windowTitle" if window.inherits("QWidget") else "title")
            ),
            "width": int(read(window, "width")),
            "height": int(read(window, "height")),
            "controls": {
                name: describe_control(obj) for name, obj in self.controls.items()
            },
            "error": self.error,
            **extra(),
        }
        return self.handle

    def release(self) -> None:
        self.controls.clear()
        self.links.clear()
        # Never enumerate the wrapper's synthetic dictionary or native properties.
        for obj, references in self.objects:
            for key in references:
                value = getattr(obj, key, None)
                # A failed constructor may not yet have shadowed a native method.
                if callable(value) and callable(getattr(type(obj), key, None)):
                    continue
                if isinstance(value, (list, dict)):
                    value.clear()
                elif not isinstance(value, (str, int, float, bool, bytes, type(None))):
                    setattr(obj, key, None)
        self.objects.clear()

    def abort(self) -> None:
        if self.handle is not None:
            self.handle.close()
        elif self.temporary is not None:
            self.cleanup_temp()


class WorkerDelivery:
    """Cancellable Python work with bounded plain-data delivery on the GUI timer.

    Workers receive only an Event and a publishing function. The GUI owns every
    Qt wrapper; stop/join completes before signal disconnection and native deletion.
    """

    def __init__(self, demo: Demo, deliver: Any) -> None:
        from queue import Queue
        from threading import Event

        self.demo, self.deliver = demo, deliver
        self.stop_event = Event()
        self.incoming = Queue(16)
        self.workers = []
        self.phase = "idle"
        self.timer = demo.remember("timer", demo.qt.QtCore.QTimer(demo.handle.widget))
        demo.connect(self.timer, "timeout()", self.drain)
        demo.handle.cleanup.append(self.stop)
        demo.handle.release.append(self.release)

    def publish(self, value: Any) -> bool:
        """Apply backpressure while retaining cooperative cancellation."""
        from queue import Full

        while not self.stop_event.is_set():
            try:
                self.incoming.put(value, timeout=0.03)
                return True
            except Full:
                continue
        return False

    def start(self, *jobs: Any) -> None:
        from queue import Empty
        from threading import Thread

        self.stop()
        while True:
            try:
                self.incoming.get_nowait()
            except Empty:
                break
        self.stop_event.clear()
        self.phase = "running"

        def run(job: Any) -> None:
            try:
                job(self.stop_event, self.publish)
            except Exception as error:  # noqa: BLE001 - report any worker failure across the thread boundary
                self.publish(("error", str(error)))

        self.workers = [
            Thread(target=run, args=(job,), name="official-worker", daemon=True)
            for job in jobs
        ]
        for worker in self.workers:
            worker.start()
        self.timer.start(30)

    def drain(self) -> None:
        from queue import Empty

        for _ in range(16):
            try:
                value = self.incoming.get_nowait()
            except Empty:
                break
            if value[0] == "error":
                self.demo.error = value[1]
                self.phase = "error"
                self.stop()
                return
            self.deliver(value)
        if (
            self.workers
            and not any(w.is_alive() for w in self.workers)
            and self.incoming.empty()
        ):
            self.phase = "done"
            self.timer.stop()

    def stop(self) -> None:
        self.stop_event.set()
        self.timer.stop()
        for worker in self.workers:
            worker.join(1.0)
            if worker.is_alive():
                raise RuntimeError("Worker did not stop; retaining owned UI")
        if self.phase == "running":
            self.phase = "stopped"

    def snapshot(self) -> dict:
        return {
            "phase": self.phase,
            "worker_alive": any(w.is_alive() for w in self.workers),
            "timer_active": bool(self.timer.isActive()),
        }

    def release(self) -> None:
        self.workers.clear()
        self.deliver = None
        self.demo = None


class LocalServer:
    """Owned loopback listener: plain Python sockets in the existing worker drain.

    The handler receives no Qt objects. Listener/client deadlines bound shutdown;
    the worker is joined before disconnection, resource release and widget deletion.
    """

    def __init__(self, demo: Demo, handler: Any, deliver: Any = None) -> None:
        import socket

        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.listener.bind(("127.0.0.1", 0))
            self.listener.listen(8)
            self.listener.settimeout(0.05)
            self.host, self.port = self.listener.getsockname()
            self.delivery = WorkerDelivery(demo, deliver or (lambda value: None))
            demo.handle.cleanup.append(self.listener.close)
            listener = self.listener

            def serve(stop: Any, publish: Any) -> None:
                while not stop.is_set():
                    try:
                        connection, _address = listener.accept()
                    except TimeoutError:
                        continue
                    with connection:
                        connection.settimeout(0.1)
                        try:
                            handler(connection, stop, publish)
                        except (OSError, ValueError) as error:
                            if not stop.is_set():
                                publish(("request_error", str(error)))

            self.delivery.start(serve)
        except BaseException:
            self.listener.close()
            raise

    def validate(self, host: str, port: int) -> None:
        """Accept only this build's numerical address and free port, without DNS."""
        if host != self.host or port != self.port:
            raise ValueError("Use this example's owned 127.0.0.1 endpoint")

    def validate_url(self, url: str) -> None:
        from urllib.parse import urlsplit

        value = urlsplit(url)
        if (
            value.scheme != "http"
            or value.hostname != self.host
            or value.port != self.port
            or value.username is not None
            or value.password is not None
        ):
            raise ValueError("Use this example's owned localhost HTTP URL")

    def snapshot(self) -> dict:
        return {"host": self.host, "port": self.port, **self.delivery.snapshot()}


def fortune_packet(text: str) -> bytes:
    """Qt_4_0 big-endian UInt16 frame plus QString (UTF-16 byte length/data)."""
    import struct

    encoded = text.encode("utf-16-be")
    body = struct.pack(">I", len(encoded)) + encoded
    return struct.pack(">H", len(body)) + body


def receive_fortune(connection: Any, stop: Any) -> str:
    """Read fragmented Qt fortune frames in a cancellable Python worker."""
    import struct
    import time

    deadline = time.monotonic() + 3

    def exact(count: int) -> bytes:
        result = bytearray()
        while len(result) < count:
            if stop.is_set():
                raise InterruptedError("Fortune request cancelled")
            if time.monotonic() >= deadline:
                raise TimeoutError("Fortune request timed out")
            try:
                data = connection.recv(count - len(result))
            except TimeoutError:
                continue
            if not data:
                raise ValueError("Truncated fortune frame")
            result.extend(data)
        return bytes(result)

    body = exact(struct.unpack(">H", exact(2))[0])
    if len(body) < 4:
        raise ValueError("Invalid fortune frame")
    size = struct.unpack(">I", body[:4])[0]
    if size != len(body) - 4 or size % 2:
        raise ValueError("Invalid QString length")
    return body[4:].decode("utf-16-be")


class LocalFortune:
    """One GUI-owned local fortune service; no shared 'fortune' endpoint.

    Accepted sockets remain children of the server until handle cleanup. They
    have no Python signal targets and are aborted before the server is deleted.
    Both IPC demos create this peer so acceptance never needs another process.
    """

    def __init__(
        self, demo: Demo, fortunes: tuple[str, ...], *, frame_bytes: int = 2
    ) -> None:
        # Keep the Unix socket path below macOS's sockaddr_un length limit.
        demo.temp_dir(prefix="fl-ipc-", directory="/tmp")
        self.endpoint = str(Path(demo.temp_dir()) / "fortune")
        self.demo, self.fortunes, self.frame_bytes = demo, fortunes, frame_bytes
        self.clients, self.sent = [], 0
        self.server = demo.remember(
            "server", demo.qt.QtNetwork.QLocalServer(demo.handle.widget)
        )
        demo.handle.cleanup.append(self.close)
        if not self.server.listen(self.endpoint):
            raise OSError(
                "Cannot listen on owned local socket: " + self.server.errorString()
            )
        demo.connect(self.server, "newConnection()", self.send)

    def send(self) -> None:
        import random

        for _ in range(16):
            if not self.server.hasPendingConnections():
                return
            client = self.server.nextPendingConnection()
            if client is None:
                return
            self.clients.append(client)
            packet = fortune_packet(random.choice(self.fortunes))
            if self.frame_bytes == 4:
                packet = (len(packet) - 2).to_bytes(4, "big") + packet[2:]
            if client.write(self.demo.qt.QtCore.QByteArray(packet)) != len(packet):
                self.demo.error = "Cannot queue complete local fortune frame"
                client.abort()
                continue
            client.flush()
            client.disconnectFromServer()
            self.sent += 1

    def close(self) -> None:
        for client in self.clients:
            client.abort()
        self.clients.clear()
        self.server.close()

    def snapshot(self) -> dict:
        return {"listening": bool(self.server.isListening()), "sent": self.sent}


class LocalHttp:
    """Small owned HTTP fixture using LocalServer's existing cancellable worker."""

    def __init__(self, demo: Demo, respond: Any) -> None:
        import time

        def serve(connection: Any, stop: Any, publish: Any) -> None:
            data = bytearray()
            deadline = time.monotonic() + 1.0
            while b"\r\n\r\n" not in data:
                if stop.is_set() or time.monotonic() > deadline or len(data) > 65536:
                    return
                try:
                    chunk = connection.recv(4096)
                except TimeoutError:
                    continue
                if not chunk:
                    return
                data.extend(chunk)
            head, body = bytes(data).split(b"\r\n\r\n", 1)
            lines = head.split(b"\r\n")
            method, path, _version = lines[0].decode("ascii").split(" ", 2)
            length = 0
            for line in lines[1:]:
                key, value = line.split(b":", 1)
                if key.lower() == b"content-length":
                    length = int(value.strip())
            if length < 0 or length > 65536:
                raise ValueError("Invalid owned HTTP request size")
            while len(body) < length:
                if stop.is_set() or time.monotonic() > deadline:
                    return
                try:
                    chunk = connection.recv(min(4096, length - len(body)))
                except TimeoutError:
                    continue
                if not chunk:
                    return
                body += chunk
            response, content_type = respond(method, path, body[:length])
            connection.sendall(
                b"HTTP/1.1 200 OK\r\nContent-Type: "
                + content_type.encode("ascii")
                + b"\r\nContent-Length: "
                + str(len(response)).encode("ascii")
                + b"\r\nConnection: close\r\n\r\n"
                + response
            )
            publish(("served", len(response)))

        self.endpoint = LocalServer(demo, serve)

    def url(self, path: str) -> str:
        return f"http://{self.endpoint.host}:{self.endpoint.port}{path}"


def build_chat(qt: Any, path: str, source_id: str, variant: str) -> ExampleHandle:
    """Preserve the three chat delivery patterns against an owned HTTP peer.

    Single-threaded keeps bounded synchronous local requests on its GUI timer;
    multithreaded/threadutil deliver plain results through WorkerDelivery instead
    of PyQt custom signals. Neither worker retains or touches a native wrapper.
    """
    from http.client import HTTPConnection
    from queue import Empty, Queue
    from threading import Lock
    from urllib.parse import parse_qs, urlencode

    demo = Demo(qt, path, source_id)
    gui, core = qt.QtGui, qt.QtCore
    window = gui.QWidget()
    demo.begin(window)
    try:
        window.setWindowTitle("PyQt Thread " + variant)
        layout = gui.QVBoxLayout(window)
        name = demo.remember("name", gui.QLineEdit("Example user", window))
        text_area = demo.remember("text_area", gui.QPlainTextEdit(window))
        text_area.setFocusPolicy(core.Qt.NoFocus)
        message = demo.remember("message", gui.QLineEdit(window))
        for control in (name, text_area, message):
            layout.addWidget(control)
        pending, lock = [], Lock()

        def respond(method: str, route: str, body: bytes) -> tuple[bytes, str]:
            if route != "/chat":
                raise ValueError("Unknown owned chat route")
            with lock:
                if method == "POST":
                    values = parse_qs(body.decode("utf-8"))
                    pending.append(
                        values.get("name", [""])[0]
                        + ": "
                        + values.get("message", [""])[0]
                    )
                    return b"", "text/plain; charset=utf-8"
                if method != "GET":
                    raise ValueError("Unknown owned chat method")
                result = "\n".join(pending)
                pending.clear()
                return result.encode("utf-8"), "text/plain; charset=utf-8"

        server = LocalHttp(demo, respond)
        host, port = server.endpoint.host, server.endpoint.port
        state = {"received": 0, "sent": 0}
        outgoing = Queue(16)

        def request(method: str, body: str | None = None) -> str:
            connection = HTTPConnection(host, port, timeout=0.25)
            try:
                connection.request(
                    method,
                    "/chat",
                    body=body,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response = connection.getresponse()
                if response.status != 200:
                    raise OSError("Owned chat HTTP status " + str(response.status))
                return response.read(65536).decode("utf-8")
            finally:
                connection.close()

        def deliver(value: Any) -> None:
            if value[0] == "messages" and value[1]:
                text_area.appendPlainText(value[1])
                state["received"] += 1
            elif value[0] == "sent":
                state["sent"] += 1

        worker = WorkerDelivery(demo, deliver)

        def poll(stop: Any, publish: Any) -> None:
            while not stop.is_set():
                try:
                    body = outgoing.get_nowait()
                except Empty:
                    body = None
                if body is not None:
                    request("POST", body)
                    publish(("sent", None))
                publish(("messages", request("GET")))
                if stop.wait(0.5):
                    return

        timer = demo.remember("pollTimer", core.QTimer(window))
        demo.handle.cleanup.append(timer.stop)

        def display() -> None:
            try:
                deliver(("messages", request("GET")))
            except (OSError, ValueError) as error:
                demo.error = str(error)

        def send() -> None:
            body = urlencode(
                {"name": str(read(name, "text")), "message": str(read(message, "text"))}
            )
            if variant == "single_threaded":
                try:
                    request("POST", body)
                    state["sent"] += 1
                except (OSError, ValueError) as error:
                    demo.error = str(error)
                    return
            else:
                from queue import Full

                try:
                    outgoing.put_nowait(body)
                except Full:
                    demo.error = "Owned chat send queue is full"
                    return
            message.clear()

        demo.connect(message, "returnPressed()", send)
        demo.connect(timer, "timeout()", display)
        if variant == "single_threaded":
            timer.start(1000)
        else:
            worker.start(poll)
            # Original 02 drains once per second; 03 threadutil dispatches promptly.
            worker.timer.setInterval(1000 if variant == "multithreaded" else 30)
        demo.remember("send_message", send)
        return demo.finish(
            window,
            lambda: {
                **state,
                "variant": variant,
                "name": str(read(name, "text")),
                "message": str(read(message, "text")),
                "text": str(text_area.toPlainText()),
                "endpoint": server.url("/chat"),
                "worker": worker.snapshot(),
                "poll_timer_active": bool(timer.isActive()),
                "owned_endpoint": True,
            },
        )
    except BaseException:
        demo.abort()
        raise
