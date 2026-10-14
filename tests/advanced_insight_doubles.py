# this_file: tests/advanced_insight_doubles.py
"""Additional native-sealed doubles for loaded forms, menus and metaobjects."""

import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import pytest
from qt_doubles import native_double
from undo_doubles import undo_types


@pytest.fixture
def advanced_qt(insight_qt):
    qt, base = insight_qt, insight_qt.QtGui.QWidget
    qt.deleted_menus = []

    @native_double
    class Widget(base):
        def __init__(self, *args):
            super().__init__(*args)
            self.objectName = ""
            self._children, self._actions = [], []
            del self.actions
            self.pos = qt.QtCore.QPoint(0, 0)
            if isinstance(self.parent, Widget):
                self.parent._children.append(self)

        def children(self):
            return list(self._children)

        def addMenu(self, text):
            menu = Widget(text, self)
            self.menus.append(menu)
            self._actions.append(menu)
            return menu

        def addAction(self, action):
            self._actions.append(action)

        def actions(self):
            return list(self._actions)

        def removeAction(self, action):
            self._actions.remove(action)
            if action in self.menus:
                self.menus.remove(action)

        def menuAction(self):
            return self

        def trigger(self):
            self.triggered.emit(False)

        def deleteLater(self):
            assert not self.triggered.callbacks, (
                "Disconnect before native menu/action deletion"
            )
            for child in self._children:
                assert not child.triggered.callbacks
            self.deleted = True
            qt.deleted_menus.append(self)

        def move(self, point):
            self.pos = point

        def metaObject(self):
            return SimpleNamespace(
                className=lambda: "QLineEdit",
                indexOfSlot=lambda signature: 0 if signature == "clear()" else -1,
            )

    for name in (
        "QWidget",
        "QMainWindow",
        "QPushButton",
        "QLabel",
        "QLineEdit",
        "QSpinBox",
        "QPlainTextEdit",
        "QAction",
    ):
        setattr(qt.QtGui, name, Widget)

    @native_double
    class Loader:
        def __init__(self):
            self.deleted = False
            qt.temporary_objects.append(self)

        def load(self, source, parent):
            xml = ET.fromstring(Path(source.path).read_text(encoding="utf-8"))
            root = Widget(parent)
            root.objectName = xml.find("widget").attrib["name"]
            for node in xml.findall(".//item/widget"):
                child = Widget(root)
                child.objectName = node.attrib["name"]
                for prop in node.findall("property"):
                    if prop.attrib["name"] == "text":
                        child.setText(prop.findtext("string"))
                    elif prop.attrib["name"] == "value":
                        child.setValue(int(prop.findtext("number")))
            return root

        def errorString(self):
            return "Bad owned UI"

        def deleteLater(self):
            self.deleted = True

    qt.QtUiTools.QUiLoader = Loader
    qt.QtGui.QUndoCommand, qt.QtGui.QUndoStack = undo_types(qt, Widget)
    return qt
