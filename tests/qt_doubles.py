# this_file: tests/qt_doubles.py
"""Owned Qt boundary doubles: call contracts, not a runtime or native proof."""

import sys
from functools import wraps
from types import SimpleNamespace


def native_double(cls):
    """Seal native instance fields after construction; Python subclasses stay open."""
    initialize = cls.__init__

    @wraps(initialize)
    def init(self, *args, **kwargs):
        previous = self.__dict__.get("_native_initializing", False)
        object.__setattr__(self, "_native_initializing", True)
        try:
            initialize(self, *args, **kwargs)
        finally:
            object.__setattr__(self, "_native_initializing", previous)

    def assign(self, name, value):
        if (
            type(self).__dict__.get("_native_double", False)
            and not self.__dict__.get("_native_initializing", False)
            and name not in self.__dict__
            and not hasattr(type(self), name)
        ):
            raise AttributeError(
                f"{name!r} does not exist; native instances reject new attributes"
            )
        object.__setattr__(self, name, value)

    cls.__init__, cls.__setattr__ = init, assign
    cls._native_double = True
    return cls


class Signal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def disconnect(self, callback):
        self.callbacks.remove(callback)

    def __getitem__(self, signature):
        return self

    def emit(self, *args):
        for callback in self.callbacks:
            callback(*args)


def fake_host(monkeypatch):
    qt = SimpleNamespace(fail_show=False, temporary_objects=[])
    owners = []

    @native_double
    class Widget:
        def __init__(self, text="", parent=None):
            self.text, self.parent = text, parent
            self.clicked = Signal()
            self.visible = self.deleted = self.opened = False
            self.layout = self.attribute = self.modality = self.loaded_path = None
            self.modal = False

        def inherits(self, name):
            return name in {"QWidget", "QObject"}

        def setAttribute(self, attribute, value):
            self.attribute = (attribute, value)

        def show(self):
            if qt.fail_show:
                raise RuntimeError("show failed")
            self.visible = True

        def isVisible(self):
            return self.visible

        def setModal(self, value):
            self.modal = value

        def setWindowModality(self, value):
            self.modality = value

        def setText(self, text):
            self.text = text

        def open(self):
            self.visible = self.opened = True

        def result(self):
            return 0

    @native_double
    class MessageBox(Widget):
        def __init__(self, parent):
            super().__init__(parent=parent)

    @native_double
    class Layout:
        def __init__(self, parent):
            self.widgets = []
            parent.layout = self

        def addWidget(self, widget):
            self.widgets.append(widget)

    class OwnedWidget:
        def __init__(self, widget, content):
            self.widget, self.content = widget, content
            self.closed = False
            owners.append(self)

        def close(self):
            if not self.closed:
                self.closed = self.widget.deleted = True
                self.widget.visible = False
                self.widget = self.content = None

    @native_double
    class File:
        def __init__(self, path):
            self.path, self.deleted = path, False
            qt.temporary_objects.append(self)

        def open(self, mode):
            return True

        def close(self):
            pass

        def deleteLater(self):
            self.deleted = True

    @native_double
    class Loader:
        def __init__(self):
            self.deleted = False
            qt.temporary_objects.append(self)

        def load(self, source):
            window = Widget()
            window.loaded_path = source.path
            return window

        def deleteLater(self):
            self.deleted = True

    qt.QtGui = SimpleNamespace(
        QLabel=Widget,
        QWidget=Widget,
        QPushButton=Widget,
        QVBoxLayout=Layout,
        QMessageBox=MessageBox,
        QApplication=SimpleNamespace(instance=lambda: object()),
    )
    qt.QtCore = SimpleNamespace(
        Qt=SimpleNamespace(
            WindowModal=1, WA_QuitOnClose=2, WA_DeleteOnClose=3, NonModal=0
        ),
        QFile=File,
        QIODevice=SimpleNamespace(ReadOnly=1),
    )
    qt.QtUiTools = SimpleNamespace(QUiLoader=Loader)
    monkeypatch.setitem(sys.modules, "PythonQt", qt)
    monkeypatch.setitem(sys.modules, "fontlab", SimpleNamespace())
    monkeypatch.setitem(
        sys.modules, "fontlabapp.widgets", SimpleNamespace(OwnedWidget=OwnedWidget)
    )
    return qt, owners
