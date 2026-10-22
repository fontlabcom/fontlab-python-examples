# this_file: tests/_cov_support.py
# SPDX-License-Identifier: Apache-2.0
"""Small Qt/Fly doubles shared by the coverage tests (no FontLab host needed)."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace as NS
from typing import Any


class Signal:
    """Minimal Qt signal: connect, disconnect and emit."""

    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


class Widget:
    """Permissive widget: text/list state is real, other setters are no-ops."""

    show_error: Exception | None = None

    def __init__(self, *args: Any) -> None:
        self._text = args[0] if args and isinstance(args[0], str) else ""
        self._plain = ""
        self._rows: list[str] = []
        self._choice = ""
        self.destroyed, self.clicked = Signal(), Signal()
        self.returnPressed = Signal()
        self.deleted = False
        self.shown = 0

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *args, **kwargs: None

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text

    def plainText(self) -> str:
        return self._plain

    def setPlainText(self, text: str) -> None:
        self._plain = text

    def currentText(self) -> str:
        return self._choice

    def value(self) -> float:
        return float(self._text or 0)

    def setValue(self, number: float) -> None:
        self._text = str(number)

    def addItems(self, rows: list[str]) -> None:
        self._rows.extend(rows)

    def setCurrentIndex(self, index: int) -> None:
        self._choice = self._rows[index]

    def count(self) -> int:
        return len(self._rows)

    def item(self, index: int) -> Widget:
        return Widget(self._rows[index])

    def clear(self) -> None:
        self._text = self._plain = ""
        self._rows = []

    def show(self) -> None:
        self.shown += 1
        if self.show_error is not None:
            raise self.show_error

    def deleteLater(self) -> None:
        self.deleted = True


class Event:
    """Close/drop/mouse event double recording accept and ignore."""

    def __init__(self, mime: Any = None, *, point: tuple[int, int] = (0, 0),
                 button: int = 1, buttons: int = 1) -> None:
        self.mime, self.point, self._button, self._buttons = mime, point, button, buttons
        self.accepted = self.ignored = False
        self.action: Any = None

    def mimeData(self) -> Any:
        return self.mime

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True

    def setDropAction(self, action: Any) -> None:
        self.action = action

    def pos(self) -> Any:
        return NS(x=lambda: self.point[0], y=lambda: self.point[1])

    def button(self) -> int:
        return self._button

    def buttons(self) -> int:
        return self._buttons


class Scope:
    """Signal-scope double matching fly.ap.draft_signals.Scope's used surface."""

    refuse_default = False

    def __init__(self, failure: Any) -> None:
        self.pairs: list[Any] = []
        self.failure, self.refuse = failure, type(self).refuse_default

    def connect(self, signal: Any, fn: Any) -> None:
        def guard(*args: Any) -> None:
            try:
                fn(*args)
            except Exception as error:  # noqa: BLE001 - emulate the App callback boundary
                self.failure(error)

        signal.connect(guard)
        self.pairs.append((signal, guard))

    def finish(self, *, destroyed: bool = False) -> bool:
        if self.refuse:
            return False
        if not destroyed:
            for signal, fn in self.pairs:
                signal.disconnect(fn)
        self.pairs.clear()
        return True


def read_property(obj: Any, key: str) -> Any:
    """Match fly.ap.qt_properties.value for plain attributes and methods."""
    found = getattr(obj, key)
    return found() if callable(found) else found


def make_qt(widget: type = Widget) -> NS:
    """Build a fake ``fly.qt`` with a clipboard and recorded drags/mime data."""
    clipboard = Widget()
    drags: list[Any] = []

    class Drag:
        failure: Exception | None = None

        def __init__(self, parent: Any) -> None:
            self.parent, self.deleted, self.mime = parent, False, None
            drags.append(self)

        def setMimeData(self, mime: Any) -> None:
            self.mime = mime

        def exec(self, action: Any) -> None:
            if Drag.failure is not None:
                raise Drag.failure

        def deleteLater(self) -> None:
            self.deleted = True

    class Application:
        startDragDistance = 4

    Application.clipboard = staticmethod(lambda: clipboard)

    class MimeData:
        def __init__(self) -> None:
            self.value = ""

        def setText(self, text: str) -> None:
            self.value = text

    gui = NS(
        QWidget=widget, QListWidget=widget, QLabel=widget, QLineEdit=widget,
        QPlainTextEdit=widget, QPushButton=widget, QComboBox=widget,
        QVBoxLayout=widget, QHBoxLayout=widget, QDoubleSpinBox=widget,
        QAbstractItemView=NS(ExtendedSelection=3), QApplication=Application, QDrag=Drag,
    )
    core = NS(Qt=NS(CopyAction=1, Window=2, WA_QuitOnClose=3, LeftButton=1,
                    Tool=4, PlainText=5, WindowFlags=int), QMimeData=MimeData)
    return NS(QtGui=gui, QtCore=core, clipboard=clipboard, drags=drags, Drag=Drag)


def install_fly(monkeypatch: Any, qt: NS) -> NS:
    """Replace the ``fly`` package with doubles; return handles tests can tune."""
    names = ("fly", "fly.ap", "fly.ap.draft_signals", "fly.ap.qt_properties",
             "fly.ap.character_map_capture", "fly.ap.scripting", "fly.ap.glyph_catalog")
    modules = {name: ModuleType(name) for name in names}
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    root, ap = modules["fly"], modules["fly.ap"]
    root.ap, root.qt = ap, qt
    root.fl = NS(MainWindow=lambda: "main-window")
    for short in ("draft_signals", "qt_properties", "character_map_capture",
                  "scripting", "glyph_catalog"):
        setattr(ap, short, modules["fly.ap." + short])
    modules["fly.ap.draft_signals"].Scope = Scope
    modules["fly.ap.qt_properties"].value = read_property
    return NS(root=root, scripting=modules["fly.ap.scripting"],
              catalog=modules["fly.ap.glyph_catalog"],
              capture_module=modules["fly.ap.character_map_capture"])
