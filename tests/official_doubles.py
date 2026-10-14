# this_file: tests/official_doubles.py
"""Strict stub-member doubles with small, explicit UI/data behavior.

The captured contract lists actual exported host names, not speculative Qt APIs.
Rendering, overload dispatch and native virtual callbacks need FontLab acceptance.
"""

import inspect
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from typing import ClassVar

from tests.qt_doubles import Signal, native_double

CONTRACT = json.loads(Path(__file__).with_name("official_contract.json").read_text())[
    "modules"
]
SIGNALS = {
    "accepted",
    "rejected",
    "clicked",
    "triggered",
    "toggled",
    "activated",
    "valueChanged",
    "currentIndexChanged",
    "currentItemChanged",
    "textChanged",
    "textEdited",
    "editTextChanged",
    "editingFinished",
    "contentsChanged",
    "copyAvailable",
    "timeout",
    "frameChanged",
    "stateChanged",
    "itemChanged",
    "cellChanged",
    "cellActivated",
    "subWindowActivated",
    "aboutToShow",
    "finished",
    "buttonClicked",
    "returnPressed",
    "canceled",
    "currentIdChanged",
}


def official_host(qt):
    classes = {}
    enums = {}
    sender = []

    def enum(name):
        if name not in enums:
            enums[name] = 1 << len(enums)
        return enums[name]

    class Meta(type):
        def __getattr__(cls, key):
            fields = cls._fields
            if key not in fields:
                raise AttributeError(
                    f"{cls._qt_name}.{key} absent from captured native stubs"
                )
            if key in SIGNALS:
                raise AttributeError(key)
            if fields[key] == "value":
                return enum(key) if key[0].isupper() else None

            def static(*args):
                if key == "keys":
                    return ["Fusion", "Windows"]
                if key == "create":
                    return classes["QStyle"]()
                if key in ("currentDate", "currentDateTime"):
                    return classes[cls._qt_name]()
                if key == "fromHsv":
                    return classes["QColor"](*args)
                if key == "currentPath":
                    return "/tmp"
                if key == "tempPath":
                    return "/tmp"
                if key == "toNativeSeparators":
                    return args[0]
                if key == "supportedFormats":
                    return [ByteArray(b"gif"), ByteArray(b"mng")]
                if key == "availableMibs":
                    return [106, 4]
                if key == "codecForMib":
                    return classes["QTextCodec"](
                        "utf-8" if args[0] == 106 else "iso-8859-1"
                    )
                if key == "codecForName":
                    return classes["QTextCodec"](
                        args[0].decode() if isinstance(args[0], bytes) else args[0]
                    )
                if args and isinstance(args[0], Native):
                    return args[0]._invoke(key, *args[1:])
                if key == "escape":
                    return re.escape(args[0])
                if key == "fromLocalFile":
                    return classes["QUrl"](args[0])
                return None

            return static

    class Native(metaclass=Meta):
        _fields: ClassVar[dict] = {}
        _qt_name = "Native"

        def __init__(self, *args, **kwargs):
            if kwargs:
                raise TypeError("called slot does not support kwargs")
            self._data = {
                "windowTitle": "",
                "text": "",
                "title": "",
                "objectName": "Fusion",
                "value": 0,
                "minimum": 0,
                "maximum": 99,
                "currentIndex": 0,
                "currentRow": 0,
                "rowCount": 0,
                "columnCount": 0,
                "visible": False,
                "enabled": True,
                "checked": False,
                "width": 400,
                "height": 300,
                "spacing": 6,
                "margin": 0,
                "modified": False,
                "count": 0,
                "styleSheet": "",
                "currentId": 0,
                "intValue": 0,
                "doubleValue": 0.0,
                "textValue": "",
                "speed": 100,
                "size": None,
                "geometry": None,
            }
            self._args = args
            self._items, self._children, self._signals, self._cells = [], [], {}, {}
            self._parent, self._layout, self._central = None, None, None
            self._extra, self._props = {}, {}
            self.visible, self.deleted = False, False
            self._active = False
            self._match = None
            self._position = [0, 0, 0, 0]
            self._blocked = False
            for arg in args:
                if isinstance(arg, Native):
                    self._parent = arg
                    arg._children.append(self)
            if args and isinstance(args[0], str):
                self._data.update(text=args[0], title=args[0])
                self._extra["path"] = args[0]
            if self._qt_name in ("QSize", "QPoint", "QPointF", "QRect"):
                values = list(args)
                if len(values) == 1 and isinstance(values[0], Native):
                    values = values[0]._position
                if len(values) == 2 and all(isinstance(v, Native) for v in values):
                    values = values[0]._position[:2] + values[1]._position[:2]
                self._position = (values + [0] * 4)[:4]
            if self._qt_name in ("QListWidgetItem", "QTreeWidgetItem") and self._parent:
                self._parent._items.append(self)
            if self._qt_name == "QStringListModel":
                self._items = (
                    list(args[0]) if args and isinstance(args[0], list) else []
                )
            if (
                self._qt_name == "QTableWidget"
                and len(args) >= 2
                and isinstance(args[0], int)
            ):
                self._data.update(rowCount=args[0], columnCount=args[1])
            if self._qt_name.endswith("Layout") and self._parent:
                self._parent._layout = self
            # PythonQt exposes native properties in __dict__, even on subclasses.
            if self._fields.get("geometry") == "value":
                object.__setattr__(self, "geometry", classes["QRect"](0, 0, 400, 300))

        def __getattr__(self, key):
            if key in self._fields:
                if key in SIGNALS:
                    return self._signals.setdefault(key, Signal())
                if self._fields[key] == "value":
                    if key[0].isupper():
                        return enum(key)
                    if key == "document":
                        if "document" not in self._extra:
                            self._extra["document"] = classes["QTextDocument"](self)
                        return self._extra["document"]
                    if key == "currentText":
                        return self._data.get(
                            "editText",
                            str(self._items[self._data["currentIndex"]][0])
                            if self._items
                            else "",
                        )
                    if key == "count":
                        return len(self._items)
                    if key in ("palette", "font", "sizePolicy"):
                        return classes["Q" + key[0].upper() + key[1:]]()
                    if key in (
                        "size",
                        "sizeHint",
                        "minimumSizeHint",
                        "minimumSize",
                        "maximumSize",
                    ):
                        return classes["QSize"](80, 30)
                    if key in ("geometry", "rect"):
                        return classes["QRect"](*self._position)
                    if key == "pos":
                        return classes["QPoint"](*self._position[:2])
                    return self._data.get(key, 0)
                return lambda *args, **kwargs: self._invoke(key, *args, **kwargs)
            raise AttributeError(
                f"{self._qt_name}.{key} absent from captured native stubs"
            )

        def connect(self, signature, callback):
            key = signature.split("(")[0]
            assert key in self._fields, f"{self._qt_name}.{key} signal unavailable"
            self._signals.setdefault(signature, Signal()).connect(callback)

        def disconnect(self, signature, callback):
            self._signals[signature].disconnect(callback)

        def emit(self, key, *args):
            if self._blocked:
                return
            sender.append(self)
            try:
                for name, signal in list(self._signals.items()):
                    if name.split("(")[0] != key:
                        continue
                    count = 0 if name.endswith("()") else len(args)
                    for cb in list(signal.callbacks):
                        parameters = inspect.signature(cb).parameters.values()
                        if any(p.kind == p.VAR_POSITIONAL for p in parameters):
                            cb(*args[:count])
                        else:
                            n = len(
                                [
                                    p
                                    for p in parameters
                                    if p.kind
                                    in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                                ]
                            )
                            cb(*args[: min(count, n)])
            finally:
                sender.pop()

        def _invoke(self, key, *a, **kw):
            if key == "sender":
                return sender[-1] if sender else None
            if key == "blockSignals":
                old = self._blocked
                self._blocked = a[0]
                return old
            if key in (
                "__init__",
                "paintEvent",
                "focusInEvent",
                "keyPressEvent",
                "event",
                "eventFilter",
                "setAttribute",
            ):
                return None
            if key == "inherits":
                return a[0] == self._qt_name or a[0] in ("QObject", "QWidget")
            if key == "children":
                return self._children
            if key == "setParent":
                self._parent = a[0]
                return None
            if key == "setLayout":
                self._layout = a[0]
                return None
            if key == "layout":
                return self._layout
            if key == "setCentralWidget":
                self._central = a[0]
                return None
            if key == "centralWidget":
                return self._central
            if key in (
                "menuBar",
                "statusBar",
                "horizontalHeader",
                "verticalHeader",
                "header",
                "document",
                "verticalScrollBar",
                "style",
                "textCursor",
                "cursorRect",
                "lineEdit",
            ):
                typ = {
                    "menuBar": "QMenuBar",
                    "statusBar": "QStatusBar",
                    "horizontalHeader": "QHeaderView",
                    "verticalHeader": "QHeaderView",
                    "header": "QHeaderView",
                    "document": "QTextDocument",
                    "verticalScrollBar": "QScrollBar",
                    "style": "QStyle",
                    "textCursor": "QTextCursor",
                    "cursorRect": "QRect",
                    "lineEdit": "QLineEdit",
                }[key]
                if key not in self._extra:
                    self._extra[key] = classes[typ](self)
                return self._extra[key]
            if key in ("setText", "setPlainText"):
                self._data["text"] = a[-1]
                if len(a) == 2:
                    self._cells[a[0]] = a[1]
                self.emit("textChanged")
                return None
            if key == "text":
                return self._cells.get(a[0], "") if a else self._data["text"]
            if key == "toPlainText":
                return self._data["text"]
            if key == "setVisible":
                self.visible = bool(a[0])
                return None
            if key == "setCurrentRow":
                self._data["currentRow"] = a[0]
                self.emit("currentItemChanged", self._items[a[0]], None)
                return None
            if key == "setCurrentIndex":
                self._data["currentIndex"] = a[0]
                self.emit("currentIndexChanged", a[0])
                return None
            if key == "setEditText":
                self._data["editText"] = a[0]
                self.emit("editTextChanged", a[0])
                return None
            if key == "setChecked":
                old = self._data["checked"]
                self._data["checked"] = a[0]
                if old != a[0]:
                    self.emit("toggled", a[0])
                return None
            if key == "setValue":
                self._data["value"] = a[0]
                self.emit("valueChanged", a[0])
                return None
            if key == "setRange":
                self._data.update(minimum=a[0], maximum=a[1])
                return None
            if key == "setData":
                self._props[tuple(a[:-1])] = a[-1]
                return None
            if key == "data":
                return self._props.get(tuple(a))
            if key in ("setModel", "setWidget"):
                self._extra[key[3:].lower()] = a[0]
                return None
            if key in ("model", "widget"):
                return self._extra.get(key)
            if key == "setGeometry":
                self._position = a[0]._position[:] if len(a) == 1 else list(a)
                return None
            if key == "resize":
                w, h = a[0]._position[:2] if len(a) == 1 else a
                self._data.update(width=w, height=h)
                return None
            if key == "move":
                self._position[:2] = a[0]._position[:2] if len(a) == 1 else a
                return None
            if key == "setProperty":
                self._props[a[0]] = a[1]
                return None
            if key.startswith("set"):
                prop = key[3:4].lower() + key[4:]
                self._data[prop] = a[0] if len(a) == 1 else a
                return None
            if key in ("show", "open") and self._qt_name != "QFile":
                self.visible = True
                return None
            if key in ("hide", "close"):
                self.visible = False
                return None
            if key == "isVisible":
                return self.visible
            if key == "isChecked":
                return self._data["checked"]
            if key == "isModified":
                return self._data["modified"]
            if key == "isWindowModified":
                return self._data.get("windowModified", False)
            if key == "accept":
                self.emit("accepted")
                self.visible = False
                return None
            if key == "reject":
                self.emit("rejected")
                self.visible = False
                return None
            if key == "click":
                if self._data.get("checkable", False) or self._qt_name in (
                    "QRadioButton",
                    "QCheckBox",
                ):
                    self._invoke("setChecked", not self._data["checked"])
                self.emit("clicked", self._data["checked"])
                return None
            if key == "trigger":
                self.emit("triggered", self._data["checked"])
                return None
            if key in (
                "addWidget",
                "addItem",
                "addTab",
                "addPage",
                "addAction",
                "addMenu",
                "addToolBar",
                "addButton",
            ):
                obj = a[0]
                if key == "addWidget" and self._qt_name == "QLayout":
                    item = classes["QWidgetItem"](obj)
                    item._extra["widget"] = obj
                    self.addItem(item)
                    return None
                if key == "addItem" and self._qt_name in ("QComboBox", "QListWidget"):
                    obj = (a[0], a[1] if len(a) > 1 else None)
                elif isinstance(obj, str) and key in (
                    "addAction",
                    "addMenu",
                    "addToolBar",
                    "addButton",
                ):
                    typ = {
                        "addAction": "QAction",
                        "addMenu": "QMenu",
                        "addToolBar": "QWidget",
                        "addButton": "QPushButton",
                    }[key]
                    obj = classes[typ](obj, self)
                self._items.append(obj)
                return len(self._items) - 1 if key in ("addPage", "addTab") else obj
            if key in ("addItems", "insertItems"):
                self._items.extend((s, None) for s in a[-1])
                return None
            if key == "setItem":
                self._cells[a[:2]] = a[2]
                return None
            if key == "item":
                return self._cells.get(a) if len(a) == 2 else self._items[a[0]]
            if key == "insertRow":
                self._data["rowCount"] += 1
                return None
            if key == "row":
                return self._items.index(a[0])
            if key == "count":
                return len(self._items)
            if key == "itemAt":
                return self._items[a[0]]
            if key == "pageIds":
                return list(range(len(self._items)))
            if key == "page":
                return self._items[a[0]]
            if key == "registerField":
                self._props[a[0].rstrip("*")] = a[1]
                return None
            if key == "field":
                for item in self._items:
                    if a[0] in item._props:
                        obj = item._props[a[0]]
                        return (
                            obj._data["checked"]
                            if obj._qt_name in ("QCheckBox", "QRadioButton")
                            else obj._data["text"]
                        )
                return ""
            if key == "wizard":
                return self._parent
            if key == "next":
                self._data["currentId"] += 1
                return None
            if key == "back":
                self._data["currentId"] -= 1
                return None
            if key == "buttonText":
                return "&Finish"
            if key == "findText":
                return next((i for i, x in enumerate(self._items) if x[0] == a[0]), -1)
            if key == "itemData":
                return self._items[a[0]][1]
            if key == "itemText":
                return self._items[a[0]][0]
            if key == "actions":
                return self._items
            if key == "removeAction":
                self._items.remove(a[0])
                return None
            if key == "clear":
                self._items.clear()
                self._data["text"] = ""
                return None
            if key == "start":
                self._active = True
                return None
            if key == "stop":
                self._active = False
                return None
            if key == "isActive":
                return self._active
            if key == "stringList":
                return self._items
            if key == "isNull":
                return False
            if key == "isEmpty":
                return not self._data["text"]
            if key == "destroyEditor":
                editor = a[0]
                assert all(not signal.callbacks for signal in editor._signals.values())
                editor.deleted = True
                return None
            if key == "deleteLater":
                self.deleted = True
                return None
            if key in ("x", "y", "width", "height", "left", "top", "right", "bottom"):
                idx = {
                    "x": 0,
                    "y": 1,
                    "left": 0,
                    "top": 1,
                    "width": 0 if self._qt_name == "QSize" else 2,
                    "height": 1 if self._qt_name == "QSize" else 3,
                    "right": 2,
                    "bottom": 3,
                }[key]
                return self._position[idx]
            if key in ("sizeHint", "minimumSize", "minimumSizeHint"):
                return classes["QSize"](80, 30)
            if key in ("geometry", "rect"):
                return classes["QRect"](*self._position)
            if key == "expandedTo":
                return classes["QSize"](
                    max(self._position[0], a[0]._position[0]),
                    max(self._position[1], a[0]._position[1]),
                )
            if key == "contentsMargins":
                return SimpleNamespace(
                    left=lambda: 0, right=lambda: 0, top=lambda: 0, bottom=lambda: 0
                )
            if key == "layoutSpacing":
                return 6
            if key == "pixelMetric":
                return 24
            if key in ("standardPixmap", "pixmap"):
                return classes["QPixmap"]()
            if key == "standardIcon":
                return classes["QIcon"]()
            if key == "currentFrameNumber":
                return -1
            if key == "frameCount":
                return 0
            if key == "state":
                return enum("NotRunning")
            if key == "isValid":
                return True
            if key in ("brush", "dark"):
                return classes["QBrush"]()
            if key in ("color", "selectedColor"):
                return classes["QColor"]()
            if key == "selectedFont":
                return classes["QFont"]()
            if key == "name":
                return (
                    ByteArray(self._args[0].encode())
                    if self._qt_name == "QTextCodec"
                    else "#123456"
                )
            if key == "toUnicode":
                return a[0].data().decode(self._args[0], errors="replace")
            if key == "fromUnicode":
                return ByteArray(a[0].encode(self._args[0]))
            if key == "mibEnum":
                return 106 if self._args[0] == "utf-8" else 4
            if key == "canEncode":
                try:
                    a[0].encode(self._args[0])
                    return True
                except UnicodeEncodeError:
                    return False
            if key in ("intValue", "doubleValue", "textValue"):
                return self._data[key]
            if key == "pattern":
                return self._data.get("pattern", self._args[0] if self._args else "")
            if key == "open" and self._qt_name == "QFile":
                return Path(self._args[0]).exists()
            if key == "load":
                return Path(a[0]).is_file()
            if key == "translate" and self._qt_name == "QTranslator":
                return a[1]
            if key == "currentPosition":
                return classes["QPointF"](0, 0)
            if key == "controlPointRect":
                return classes["QRect"](0, 0, 100, 100)
            if key == "toString":
                return "sample"
            if key == "key":
                return "sample-font"
            if key == "rowCount":
                return self._data["rowCount"]
            if key == "columnCount":
                return self._data["columnCount"]
            if key == "fileName":
                return Path(self._extra.get("path", "")).name
            if key in ("absoluteFilePath", "canonicalFilePath"):
                return str(Path(self._extra.get("path", "")).absolute())
            if key == "path":
                return str(Path(self._extra.get("path", "")).parent)
            if key == "absolutePath":
                return str(Path(self._extra.get("path", "")).absolute().parent)
            if key == "suffix":
                return Path(self._extra.get("path", "")).suffix.lstrip(".")
            if key in ("lastRead", "lastModified"):
                return classes["QDateTime"]()
            if key == "size":
                return 20
            if key in ("isReadable", "isWritable"):
                return True
            if key == "isExecutable":
                return False
            if key in ("owner", "group"):
                return "fixture"
            if key == "flags":
                return enum("ItemIsEditable") | enum("ItemIsEnabled")
            if key == "exactMatch":
                pattern = self._data.get("pattern", self._args[0] if self._args else "")
                self._match = re.fullmatch(pattern, a[0])
                return bool(self._match)
            if key == "indexIn":
                pattern = self._data.get("pattern", self._args[0] if self._args else "")
                try:
                    self._match = re.search(pattern, a[0])
                except re.error:
                    self._match = None
                return self._match.start() if self._match else -1
            if key == "cap":
                return (
                    self._match.group(a[0])
                    if self._match and a[0] <= len(self._match.groups())
                    else ""
                )
            if key == "matchedLength":
                return len(self._match.group()) if self._match else -1
            if key == "captureCount":
                return len(self._match.groups()) if self._match else 0
            if key == "errorString":
                return ""
            if key == "parent":
                return self._parent
            if key == "subWindowList":
                return self._items
            if key in ("activeSubWindow", "currentSubWindow"):
                return self._items[-1] if self._items else None
            if key == "addSubWindow":
                sub = classes["QMdiSubWindow"]()
                sub._extra["widget"] = a[0]
                self._items.append(sub)
                return sub
            if key == "selectedFiles":
                return self._extra.get("selectedFiles", [])
            if key == "standardButton":
                return a[0]
            if key == "value":
                return self._props.get(a[0], a[1] if len(a) > 1 else None)
            if key in ("childKeys", "childGroups", "allKeys"):
                return []
            if key == "findChild":
                return next(
                    (x for x in self._children if x._data.get("objectName") == a[-1]),
                    None,
                )
            if key == "findChildren":
                return self._children
            return None

        def unsafe_arithmetic(self, *args):
            raise TypeError("unsafe arithmetic on PythonQt wrapper")

        __neg__ = __pos__ = __add__ = __sub__ = unsafe_arithmetic
        __mul__ = __truediv__ = __floordiv__ = unsafe_arithmetic
        __radd__ = __rsub__ = __rmul__ = __rtruediv__ = unsafe_arithmetic

    def protect_native_members(assign):
        def checked(self, name, value):
            if self._fields.get(name) == "method":
                raise AttributeError(
                    f"Slot {name!r} can not be overwritten on {type(self).__name__} object"
                )
            if value is None and self._fields.get(name) == "value":
                raise TypeError(f"Property {name!r} does not accept NoneType")
            assign(self, name, value)

        return checked

    for module, types in CONTRACT.items():
        namespace = SimpleNamespace()
        setattr(qt, module, namespace)
        for name, fields in types.items():
            cls = Meta(name, (Native,), {"_fields": fields, "_qt_name": name})
            # Sealed native instances; Python subclasses retain their own fields.
            cls.__init__ = Native.__init__
            cls = native_double(cls)
            cls.__setattr__ = protect_native_members(cls.__setattr__)
            classes[name] = cls
            setattr(namespace, name, cls)

    class ByteArray:
        def __init__(self, value=b""):
            self._value = value

        def data(self):
            return self._value

        def __bytes__(self):
            raise TypeError("cannot convert 'QByteArray' object to bytes")

        __neg__ = __pos__ = Native.unsafe_arithmetic

    qt.QtCore.QByteArray = ByteArray
    qt.QtCore.Qt = SimpleNamespace(
        **{k: enum(k) for k in CONTRACT["QtCore"].get("Qt", {})}
    )

    class Loader:
        def load(self, source, parent=None):
            doc = ET.parse(source._args[0])
            root = doc.find("widget")
            widget = classes[root.get("class")]()
            title = root.find("property[@name='windowTitle']/string")
            if title is not None:
                widget._data["windowTitle"] = title.text
            for node in list(root.iter("widget"))[1:] + list(root.iter("action")):
                item = classes[node.get("class", "QAction")](widget)
                item._data["objectName"] = node.get("name")
                if item._qt_name == "QComboBox":
                    for value in node.findall("item/property/string"):
                        item._items.append((value.text, None))
            return widget

        def deleteLater(self):
            pass

    qt.QtUiTools = SimpleNamespace(QUiLoader=Loader)
    qt._classes = classes
    return qt
