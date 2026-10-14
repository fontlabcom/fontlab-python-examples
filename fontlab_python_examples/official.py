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
        self.error = ""
        self.closing = False
        self.dragging = False

    def begin(self, window: Any) -> None:
        if self.handle is None:
            self.handle = ExampleHandle(window, dict)
            self.handle.release.append(self.release)
            self.handle.cleanup.append(self.prepare_close)
        elif window is not self.handle.widget:
            from fontlabapp.widgets import OwnedWidget

            self.handle.alerts.append(OwnedWidget(window, window))
        window.setAttribute(self.qt.QtCore.Qt.WA_QuitOnClose, False)
        window.setAttribute(self.qt.QtCore.Qt.WA_DeleteOnClose, False)

    def prepare_close(self) -> None:
        """Keep the drag source alive until the native macOS drag returns."""
        if self.dragging:
            raise RuntimeError("Finish or cancel the drag before closing this example")
        self.closing = True

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
        """Address-book persistence accepts only paths in this build's directory."""
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

    def temp_dir(self) -> str:
        if self.temporary is None:
            self.temporary = TemporaryDirectory(prefix="fontlab-official-")
        return self.temporary.name

    def settings(self, *args: Any) -> Any:
        """All settings scopes, including location previews, stay in owned INIs."""
        import hashlib
        import shutil

        key = hashlib.sha256(repr(args).encode()).hexdigest()[:16]
        target = Path(self.temp_dir()) / (key + ".ini")
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

    def dialog(self, box: Any, callback: Any = None) -> Any:
        """Retain every asynchronous dialog until disconnect-before-delete cleanup."""
        from fontlabapp.widgets import OwnedWidget

        if not any(owner.widget is box for owner in self.handle.alerts):
            self.handle.alerts.append(OwnedWidget(box, box))
        self.controls["active_dialog"] = box
        self.handle.controls["active_dialog"] = box
        box.setAttribute(self.qt.QtCore.Qt.WA_DeleteOnClose, False)
        box.setAttribute(self.qt.QtCore.Qt.WA_QuitOnClose, False)
        box.setWindowModality(self.qt.QtCore.Qt.WindowModal)
        if callback is not None:
            self.connect(box, "accepted()", callback)
        box.open()
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
    ) -> Any:
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
        if directory:
            box.setDirectory(directory)
        if filters:
            box.setNameFilter(filters)

        def selected() -> None:
            paths = list(box.selectedFiles())
            if paths:
                callback(paths if mode == "many" else str(paths[0]))

        return self.dialog(box, selected)

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
        printer.setOutputFileName(path or str(Path(self.temp_dir()) / "output.pdf"))
        return printer

    def print_dialog(self, parent: Any, render: Any) -> Any:
        """Open an owned print dialog only on explicit action; inspection is inert."""
        box = self.qt.QtGui.QPrintDialog(parent)
        # The dialog owns its native printer until actual deferred destruction.
        printer = box.printer()
        printer.setOutputFormat(self.qt.QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(str(Path(self.temp_dir()) / "output.pdf"))
        return self.dialog(box, lambda: render(printer))

    def print_document(self, parent: Any, document: Any) -> Any:
        """Preserve document printing through an asynchronous owned print dialog."""
        return self.print_dialog(parent, lambda printer: document.print(printer))

    def finish(self, window: Any, extra: Any = dict) -> ExampleHandle:
        self.begin(window)
        self.handle.controls.update(self.controls)
        self.handle.controls["window"] = window
        self.handle.inspect_ui = lambda: {
            "title": str(read(window, "windowTitle")),
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
        if self.temporary is not None:
            self.temporary.cleanup()
            self.temporary = None

    def abort(self) -> None:
        if self.handle is not None:
            self.handle.close()
        elif self.temporary is not None:
            self.temporary.cleanup()


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
