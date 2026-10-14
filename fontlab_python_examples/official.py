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

    def begin(self, window: Any) -> None:
        if self.handle is None:
            self.handle = ExampleHandle(window, dict)
            self.handle.release.append(self.release)
            self.handle.cleanup.append(lambda: setattr(self, "closing", True))
        elif window is not self.handle.widget:
            from fontlabapp.widgets import OwnedWidget

            self.handle.alerts.append(OwnedWidget(window, window))
        window.setAttribute(self.qt.QtCore.Qt.WA_QuitOnClose, False)
        window.setAttribute(self.qt.QtCore.Qt.WA_DeleteOnClose, False)

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
                if callable(value):
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
