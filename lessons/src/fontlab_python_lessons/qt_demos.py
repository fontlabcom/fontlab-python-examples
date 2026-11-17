# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/2f94fe07de765888.md
# this_file: lessons/src/fontlab_python_lessons/qt_demos.py
"""Shared lifetime and controls retained from the licensed visual demos."""

from pathlib import Path
from tempfile import TemporaryDirectory
from collections.abc import Callable
from typing import Any


class ExampleHandle:
    """Hold native UI/callbacks alive until named cleanup or native destruction."""

    def __init__(self, widget: Any, inspect_ui: Callable[[], dict]) -> None:
        from fly.ap.qt.widgets import OwnedWidget

        self.owner = OwnedWidget(widget, widget)
        self.inspect_ui = inspect_ui
        self.callbacks: list[Callable] = []
        self.alerts: list[Any] = []
        self.cleanup: list[Callable] = []
        self.connections: list[tuple[Any, str | None, Callable]] = []
        self.release: list[Callable] = []
        self.after_close: list[Callable] = []
        self.model: Any = None
        self.controls: dict[str, Any] = {}

    def connect(self, signal: Any, slot: Callable) -> None:
        """Retain the exact signal/slot pair until explicit disconnection."""
        if signal.connect(slot) is False:
            raise RuntimeError("Signal connection refused")
        self.connections.append((signal, None, slot))

    def connect_old(self, obj: Any, signature: str, slot: Callable) -> None:
        """Record PythonQt's string-signature connection without a bound disconnector."""
        if obj.connect(signature, slot) is False:
            raise RuntimeError("Signal connection refused")
        self.connections.append((obj, signature, slot))

    def disconnect(self, signal: Any, slot: Callable) -> None:
        """Disconnect a tracked pair before dynamically unloading owned actions."""
        pair = (signal, None, slot)
        if pair not in self.connections:
            raise ValueError("Signal/slot pair is not tracked by this handle")
        if not self.owner.closed:
            signal.disconnect(slot)
        self.connections.remove(pair)

    def _disconnect(self) -> None:
        while self.connections:
            obj, signature, slot = self.connections[-1]
            if not self.owner.closed:
                if signature is None:
                    if obj.disconnect(slot) is False:
                        raise RuntimeError("Signal disconnection refused")
                else:
                    if obj.disconnect(signature, slot) is False:
                        raise RuntimeError("Signal disconnection refused")
            self.connections.pop()

    @property
    def widget(self) -> Any:
        return self.owner.widget

    def snapshot(self) -> dict:
        state = {"launched": True, "closed": self.owner.closed}
        if not self.owner.closed:
            state.update(visible=bool(self.widget.isVisible()))
            state.update(self.inspect_ui())
        return state

    def close(self) -> None:
        while self.cleanup:
            self.cleanup[0]()
            self.cleanup.pop(0)
        self._disconnect()
        while self.release:
            self.release.pop(0)()
        for alert in self.alerts:
            alert.close()
        self.alerts.clear()
        if self.owner.close() is False:
            raise RuntimeError("The example refused Close; finish its active operation first")
        self.callbacks.clear()
        self.inspect_ui = dict
        self.model = None
        self.controls.clear()
        while self.after_close:
            self.after_close[0]()
            self.after_close.pop(0)


def value(obj, name):
    result = getattr(obj, name)
    return result() if callable(result) else result

class Session:
    """Keep Python state outside wrappers and close partially built UI."""

    def __init__(self, qt, title, window=None):
        self.qt, self.g, self.c = qt, qt.QtGui, qt.QtCore
        self.window = window if window is not None else self.g.QWidget()
        self.h = ExampleHandle(self.window, self.snapshot)
        self.state, self.controls = {}, self.h.controls
        self._temp, self.layout = None, None
        self.window.setWindowTitle(title)
        self.window.setAttribute(self.c.Qt.WA_QuitOnClose, False)
        self.window.setAttribute(self.c.Qt.WA_DeleteOnClose, False)
        self.window.resize(640, 460)

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        if kind:
            self.h.close()

    def snapshot(self):
        result = dict(self.state)
        for key, obj in self.controls.items():
            for name in ("text", "value", "currentIndex", "checked"):
                prop = getattr(obj, name, None)
                if isinstance(prop, (str, int, float, bool)):
                    result[key + "_" + name] = prop
        return result

    def keep(self, key, obj):
        self.controls[key] = obj
        return obj

    def link(self, obj, signal, callback):
        def routed(*args):
            if not self.h.owner.closed:
                callback(*args)

        self.h.connect_old(obj, signal, routed)
        return routed

    def vertical(self, parent=None):
        parent = self.window if parent is None else parent
        layout = self.g.QVBoxLayout(parent)
        if parent is self.window:
            self.layout = layout
        return layout

    def add(self, obj, layout=None):
        (layout if layout is not None else self.layout).addWidget(obj)
        return obj

    def label(self, text, layout=None):
        return self.add(self.g.QLabel(text, self.window), layout)

    def line(self, key, text="", layout=None):
        return self.add(self.keep(key, self.g.QLineEdit(text, self.window)), layout)

    def check(self, key, text, checked=False, layout=None):
        obj = self.keep(key, self.g.QCheckBox(text, self.window))
        obj.setChecked(checked)
        return self.add(obj, layout)

    def spin(self, key, low=0, high=99, initial=0, layout=None, decimal=False):
        obj = self.keep(
            key, (self.g.QDoubleSpinBox if decimal else self.g.QSpinBox)(self.window)
        )
        obj.setRange(low, high)
        obj.setValue(initial)
        return self.add(obj, layout)

    def combo(self, key, items, layout=None):
        obj = self.keep(key, self.g.QComboBox(self.window))
        obj.addItems(list(items))
        return self.add(obj, layout)

    def button(self, key, text, callback=None, layout=None):
        obj = self.keep(key, self.g.QPushButton(text, self.window))
        self.add(obj, layout)
        if callback is not None:
            self.link(obj, "clicked()", lambda *a: callback())
        return obj

    def timer(self, key, interval, callback, single=False, start=True):
        timer = self.keep(key, self.c.QTimer(self.window))
        timer.setSingleShot(single)
        self.link(timer, "timeout()", lambda *a: callback())
        self.h.cleanup.append(lambda: timer.stop() if not self.h.owner.closed else None)
        if start:
            timer.start(interval)
        return timer

    def temp(self):
        if self._temp is None:
            self._temp = TemporaryDirectory(prefix="fontlab-example-")
            self.h.after_close.append(self._temp.cleanup)
        return Path(self._temp.name)

    def alert(self, dialog):
        from fly.ap.qt.widgets import OwnedWidget

        dialog.setAttribute(self.c.Qt.WA_QuitOnClose, False)
        dialog.setAttribute(self.c.Qt.WA_DeleteOnClose, False)
        self.h.alerts.append(OwnedWidget(dialog, dialog))
        return dialog

    def choose(self, callback, save=False, directory=False):
        dialog = self.keep("file_dialog", self.alert(self.g.QFileDialog(self.window)))
        dialog.setOption(self.g.QFileDialog.DontUseNativeDialog, True)
        if directory:
            dialog.setFileMode(self.g.QFileDialog.Directory)
        elif save:
            dialog.setAcceptMode(self.g.QFileDialog.AcceptSave)
        else:
            dialog.setFileMode(self.g.QFileDialog.ExistingFile)
        dialog.setDirectory(str(self.temp()))

        def selected(*args):
            files = list(dialog.selectedFiles())
            if files:
                try:
                    callback(str(files[0]))
                except (OSError, ValueError) as error:
                    self.state["error"] = str(error)

        self.link(dialog, "accepted()", selected)
        dialog.open()
        return dialog

    def menu(self, title, entries):
        if "menu_bar" not in self.controls:
            bar = self.keep("menu_bar", self.g.QMenuBar(self.window))
            self.layout.setMenuBar(bar)
        menu = self.controls["menu_bar"].addMenu(title)
        for label, callback in entries:
            action = self.g.QAction(label, self.window)
            menu.addAction(action)
            self.keep("action_" + label, action)
            self.link(action, "triggered()", lambda *a, cb=callback: cb())
        return menu

    def table(self, key, headers, rows, layout=None):
        table = self.keep(
            key, self.g.QTableWidget(len(rows), len(headers), self.window)
        )
        table.setHorizontalHeaderLabels(headers)
        for r, row in enumerate(rows):
            for col, cell in enumerate(row):
                table.setItem(r, col, self.g.QTableWidgetItem(str(cell)))
        return self.add(table, layout)

    def model(self, headers, rows):
        model = self.g.QStandardItemModel(self.window)
        model.setHorizontalHeaderLabels(headers)
        for row in rows:
            model.appendRow([self.g.QStandardItem(str(cell)) for cell in row])
        self.h.model = model
        return self.keep("model", model)

    def view(self, key, model, kind="QTableView", layout=None):
        view = self.keep(key, getattr(self.g, kind)(self.window))
        view.setModel(model)
        self.add(view, layout)
        self.h.release.append(
            lambda: view.setModel(None) if not self.h.owner.closed else None
        )
        return view

    def local_style(self, name, widgets=None):
        style = self.g.QStyleFactory.create(name)
        if style is not None:
            style.setParent(self.window)
            self.keep("style", style)
            for widget in widgets or [self.window]:
                widget.setStyle(style)

def canvas(s, paint, events=None):
    events = events or {}
    g = s.g

    class Surface(g.QWidget):
        def paintEvent(self, event):
            painter = g.QPainter(self)
            try:
                painter.setRenderHint(g.QPainter.Antialiasing)
                paint(painter, int(value(self, "width")), int(value(self, "height")))
            except Exception as error:
                print("Drawing failed:", error)
            finally:
                painter.end()

        def mousePressEvent(self, event):
            if "press" in events:
                events["press"](event)
            else:
                g.QWidget.mousePressEvent(self, event)

        def mouseMoveEvent(self, event):
            if "move" in events:
                events["move"](event)
            else:
                g.QWidget.mouseMoveEvent(self, event)

        def mouseReleaseEvent(self, event):
            if "release" in events:
                events["release"](event)
            else:
                g.QWidget.mouseReleaseEvent(self, event)

        def resizeEvent(self, event):
            g.QWidget.resizeEvent(self, event)
            if "resize" in events:
                events["resize"](event)

        def keyPressEvent(self, event):
            if "key" in events:
                events["key"](event)
            else:
                g.QWidget.keyPressEvent(self, event)

        def contextMenuEvent(self, event):
            if "context" in events:
                events["context"](event)
            else:
                g.QWidget.contextMenuEvent(self, event)

    surface = s.keep("canvas", Surface(s.window))
    surface.setMinimumSize(100, 100)
    surface.setMouseTracking(True)
    surface.setFocusPolicy(s.c.Qt.StrongFocus)
    s.h.callbacks.extend([paint, *events.values()])
    return surface


def apply_style(widget, style):
    """Apply a local style only to this demo subtree."""
    if widget.inherits("QWidget"):
        widget.setStyle(style)
    for child in widget.children():
        apply_style(child, style)


def launch(build, key, title):
    """Use the existing App parent and registry for a historical demo builder."""
    from PythonQt import QtCore, QtGui, private
    from types import SimpleNamespace

    qt = SimpleNamespace(QtCore=QtCore, QtGui=QtGui, private=private)
    import fly.ap.core.scripting as scripting

    class Panel(qt.QtGui.QWidget):
        def __init__(self, parent):
            qt.QtGui.QWidget.__init__(self, parent, qt.QtCore.Qt.Window)
            self.setWindowTitle(title)
            self.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
            self.resize(680, 520)
            self.handle = build(qt)
            shaped = bool(self.handle.widget.windowFlags() & qt.QtCore.Qt.FramelessWindowHint)
            if shaped:
                self.setWindowFlags(self.windowFlags() | qt.QtCore.Qt.FramelessWindowHint)
            self.handle.widget.setParent(self)
            if shaped:
                self.handle.widget.clearMask()
            layout = qt.QtGui.QVBoxLayout(self)
            layout.addWidget(self.handle.widget)

        def closeEvent(self, event):
            try:
                can_close = self.handle.controls.get("can_close")
                if can_close is not None and not can_close():
                    event.ignore()
                    return
                self.handle.close()
            except Exception as error:
                print("Cannot close example:", error)
                event.ignore()
                return
            event.accept()
            self.deleteLater()

    return scripting.show_script_dialog(Panel, key)
