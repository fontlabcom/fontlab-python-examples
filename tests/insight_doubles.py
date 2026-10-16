# this_file: tests/insight_doubles.py
"""Scoped additions to existing doubles for insight-only Qt contracts."""

from types import SimpleNamespace

import pytest
from qt_doubles import Signal, native_double


@pytest.fixture
def insight_qt(batch_qt):
    qt = batch_qt
    base = qt.QtGui.QWidget

    @native_double
    class Widget(base):
        def __init__(self, *args):
            super().__init__(*args)
            self.valueChanged = Signal()
            self.blocked = False
            self.props = {}
            self.filters = []
            del self.items
            self.scene_items = []
            self.parent = next((a for a in args if isinstance(a, base)), None)

        def resize(self, width, height):
            object.__setattr__(self, "size", (width, height))

        def connect(self, signature, callback):
            assert signature == "clicked()", "Use the exact no-argument signature"
            self.clicked.connect(callback)

        def disconnect(self, signature, callback):
            assert signature == "clicked()"
            self.clicked.disconnect(callback)

        def blockSignals(self, blocked):
            previous, self.blocked = self.blocked, blocked
            return previous

        def setValue(self, value):
            changed = value != self.value
            self.value = value
            if changed and not self.blocked:
                self.valueChanged.emit(value)

        def setProperty(self, name, value):
            self.props[name] = value
            return False  # Qt returns false for newly added dynamic properties.

        def property(self, name):
            return self.props[name]

        def installEventFilter(self, obj):
            self.filters.append(obj)

        def removeEventFilter(self, obj):
            self.filters.remove(obj)

        def addDockWidget(self, area, dock):
            object.__setattr__(self, "dock", dock)

        def setWidget(self, widget):
            object.__setattr__(self, "content", widget)

        def setVisible(self, visible):
            self.visible = visible

        def items(self):
            return self.scene_items

        def addPath(self, path):
            self.scene_items.append(path)
            return SimpleNamespace()

        def addLine(self, *args):
            self.scene_items.append(args)
            return SimpleNamespace()

    for name in (
        "QWidget",
        "QLabel",
        "QPushButton",
        "QLineEdit",
        "QSpinBox",
        "QSlider",
        "QListView",
        "QTableView",
        "QMainWindow",
        "QDockWidget",
        "QGraphicsView",
        "QGraphicsScene",
    ):
        setattr(qt.QtGui, name, Widget)
    Widget.ScrollHandDrag = 1
    qt.QtCore.QTimer.isActive = lambda self: self.active
    qt.QtGui.QStringListModel.setStringList = lambda self, strings: setattr(
        self, "strings", strings
    )
    qt.private = SimpleNamespace(QObject=Widget)
    qt.QtCore.QEvent = SimpleNamespace(KeyPress=6)
    qt.QtCore.Qt.RightDockWidgetArea = 2

    @native_double
    class PathDouble:
        def __init__(self):
            self.commands = []

        def moveTo(self, *args):
            self.commands.append(("move", args))

        def lineTo(self, *args):
            self.commands.append(("line", args))

        def cubicTo(self, *args):
            self.commands.append(("cubic", args))

        def closeSubpath(self):
            self.commands.append(("close", ()))

        def elementCount(self):
            return len(self.commands)

    qt.QtGui.QPainterPath = PathDouble
    qt.paint_events = []

    @native_double
    class Painter:
        Antialiasing = 1

        def __init__(self, widget):
            qt.paint_events.append("begin")

        def setRenderHint(self, *args):
            pass

        def drawPath(self, path):
            qt.paint_events.append("draw")

        def end(self):
            qt.paint_events.append("end")

    qt.QtGui.QPainter = Painter
    qt.settings_store, qt.settings_writes = {}, []

    @native_double
    class Settings:
        NoError = 0

        def __init__(self, organization, application, parent):
            assert organization == "FontLabPythonExamples"
            assert application == "InsightsSandbox"
            self.parent = parent

        def setFallbacksEnabled(self, enabled):
            assert enabled is False

        def value(self, key, default):
            return qt.settings_store.get(key, default)

        def setValue(self, key, value):
            qt.settings_store[key] = value
            qt.settings_writes.append(key)

        def remove(self, key):
            qt.settings_store.pop(key, None)
            qt.settings_writes.append(key)

        def sync(self):
            pass

        def status(self):
            return self.NoError

    qt.QtCore.QSettings = Settings
    yield qt
    from fontlab_python_examples import available, close

    for record in available():
        if "slug" in record:
            close(record["slug"])
