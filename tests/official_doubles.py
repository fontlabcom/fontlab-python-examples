# this_file: tests/official_doubles.py
"""Strict stub-member doubles with small, explicit UI/data behavior.

The captured contract lists actual exported host names, not speculative Qt APIs.
Rendering, overload dispatch and native virtual callbacks need FontLab acceptance.
"""

import datetime
import inspect
import json
import re
import threading
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
    "selectionChanged",
    "currentChanged",
    "sectionResized",
    "entered",
    "exited",
    "propertiesAssigned",
    "xChanged",
    "yChanged",
    "messageClicked",
    "currentRowChanged",
    "currentFontChanged",
}


def official_host(qt):
    gui_thread = threading.get_ident()
    classes = {}
    enums = {}
    sender = []
    streams = {}

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
                if key in ("currentDate", "currentDateTime", "currentTime"):
                    return classes[cls._qt_name]()
                if key == "colorNames":
                    return [
                        "black",
                        "blue",
                        "cornsilk",
                        "darkslateblue",
                        "green",
                        "mediumslateblue",
                        "red",
                        "white",
                        "yellow",
                    ]
                if key == "longMonthName":
                    return datetime.date(2026, args[0], 1).strftime("%B")
                if key == "longDayName":
                    return (
                        "Monday",
                        "Tuesday",
                        "Wednesday",
                        "Thursday",
                        "Friday",
                        "Saturday",
                        "Sunday",
                    )[args[0] - 1]
                if key == "clipboard":
                    if "clipboard" not in streams:
                        streams["clipboard"] = classes["QClipboard"]()
                    return streams["clipboard"]
                if key == "supportedImageFormats":
                    return [ByteArray(b"png"), ByteArray(b"jpg")]
                if key == "standardSizes":
                    return [8, 10, 12, 16, 20]
                if key == "matchingLocales":
                    return [classes["QLocale"]()]
                if key == "languageToString":
                    return "English"
                if key == "countryToString":
                    return "United Kingdom"
                if key == "font":
                    return classes["QFont"]()
                if key == "isLeftToRight":
                    return True
                if key == "mightBeRichText":
                    return "<" in args[0]
                if key == "fromHsv":
                    return classes["QColor"](*args)
                if key == "fromImage":
                    return classes["QPixmap"](
                        args[0]._data["width"], args[0]._data["height"]
                    )
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
                if key == "codecForHtml":
                    return classes["QTextCodec"]("utf-8")
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
            assert threading.get_ident() == gui_thread, (
                "Native Qt construction on a Python worker"
            )
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
            if self._qt_name == "QPainter":
                self._active = True
                qt._painters.append(self)
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
            if self._qt_name in (
                "QSize",
                "QSizeF",
                "QPoint",
                "QPointF",
                "QRect",
                "QRectF",
            ):
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
            if self._qt_name == "QColor":
                if len(args) >= 3:
                    self._data.update(red=args[0], green=args[1], blue=args[2])
                else:
                    self._data.update(red=0, green=0, blue=0)
                    if args and isinstance(args[0], Native):
                        self._data.update(
                            {
                                key: args[0]._data[key]
                                for key in ("red", "green", "blue")
                            }
                        )
                    elif args and isinstance(args[0], int):
                        rgb = {
                            enum("cyan"): (0, 255, 255),
                            enum("magenta"): (255, 0, 255),
                            enum("yellow"): (255, 255, 0),
                            enum("white"): (255, 255, 255),
                        }.get(args[0], (0, 0, 0))
                        self._data.update(
                            zip(("red", "green", "blue"), rgb, strict=True)
                        )
            if self._qt_name in ("QDate", "QDateTime", "QTime"):
                self._extra["date"] = (
                    datetime.date(*args[:3])
                    if self._qt_name == "QDate" and len(args) >= 3
                    else datetime.date(2026, 10, 14)
                )
                self._data.update(
                    hour=args[0] if self._qt_name == "QTime" and args else 12,
                    minute=args[1]
                    if self._qt_name == "QTime" and len(args) > 1
                    else 34,
                    second=args[2] if self._qt_name == "QTime" and len(args) > 2 else 0,
                )
            if self._qt_name == "QFont":
                self._data.update(
                    family=args[0] if args and isinstance(args[0], str) else "Sans",
                    pointSize=args[1] if len(args) > 1 else 10,
                )
            if self._qt_name == "QPolygonF" and args and isinstance(args[0], list):
                self._items = list(args[0])
            if self._qt_name in ("QState", "QStateMachine") and self._parent:
                self._parent._extra.setdefault("states", []).append(self)
            if (
                self._qt_name == "QGraphicsView"
                and args
                and getattr(args[0], "_qt_name", None) == "QGraphicsScene"
            ):
                self._extra["scene"] = args[0]
            if self._qt_name.endswith("Layout") and self._parent:
                self._parent._layout = self
            if (self._qt_name == "QStandardItemModel" and len(args) >= 2) and (
                isinstance(args[0], int) and isinstance(args[1], int)
            ):
                self._data.update(rowCount=args[0], columnCount=args[1])
            if (self._qt_name in ("QImage", "QPixmap") and len(args) >= 2) and (
                isinstance(args[0], int) and isinstance(args[1], int)
            ):
                self._data.update(width=args[0], height=args[1])
                self._position[2:] = args[:2]
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
                    if key in ("selection", "selectedIndexes", "offset") or (
                        key == "currentIndex" and self._qt_name == "QItemSelectionModel"
                    ):
                        return self._invoke(key)
                    if key in ("x", "y"):
                        return self._position[0 if key == "x" else 1]
                    if key == "color":
                        return self._data.get(key, classes["QColor"]())
                    if key == "pixmap":
                        return self._data.get(key, classes["QPixmap"]())
                    if key == "document":
                        if "document" not in self._extra:
                            self._extra["document"] = classes["QTextDocument"](self)
                        return self._extra["document"]
                    if key == "currentFont":
                        return self._data.get(key, classes["QFont"]())
                    if key == "locale":
                        return self._data.get(key, classes["QLocale"]())
                    if key in ("date", "selectedDate", "minimumDate", "maximumDate"):
                        return self._data.get(key, classes["QDate"]())
                    if key in ("time", "minimumTime", "maximumTime"):
                        return self._data.get(key, classes["QTime"]())
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
                active_before = {
                    id(t._extra["source"]._invoke("machine")): set(
                        t._extra["source"]
                        ._invoke("machine")
                        ._extra.get("active_states", set())
                    )
                    for t in self._extra.get("transitions", [])
                    if t._extra["source"]._invoke("machine") is not None
                }
                for transition in self._extra.get("transitions", []):
                    if transition._extra["signal"].split("(")[0] != key:
                        continue
                    source = transition._extra["source"]
                    machine = source._invoke("machine")
                    if (
                        machine is None
                        or not machine._active
                        or source not in active_before.get(id(machine), set())
                    ):
                        continue
                    target = transition._extra["target"]
                    # Keep ancestors active for group-level transitions.
                    active = set()
                    parent = target._parent
                    while parent is not None and parent is not machine:
                        active.add(parent)
                        parent = parent._parent
                    machine._extra["active_states"] = active
                    machine._enter_state(target)
            finally:
                sender.pop()

        def _enter_state(self, state):
            self._extra["active_states"].add(state)
            for obj, prop, value in state._extra.get("assignments", []):
                if prop == "geometry":
                    obj._invoke("setGeometry", value)
                elif prop == "pos":
                    obj._invoke("setPos", value)
                else:
                    obj._invoke("set" + prop[0].upper() + prop[1:], value)
            state.emit("entered")
            initial = state._extra.get("initialState")
            if initial is not None:
                self._enter_state(initial)

        def _invoke(self, key, *a, **kw):
            assert threading.get_ident() == gui_thread, (
                "Native Qt access on a Python worker"
            )
            if (
                getattr(qt, "_strict_integer_coordinates", False)
                and self._qt_name == "QPainter"
                and key == "drawText"
                and len(a) >= 3
                and isinstance(a[0], (int, float))
            ):
                assert type(a[0]) is int and type(a[1]) is int, (
                    "drawText(x, y, text) requires integer coordinates"
                )
            if self._qt_name == "QSettings" and key == "setValue":
                self._props[a[0]] = a[1]
                return None
            if self._qt_name == "QClipboard" and key == "setText":
                self._data["text"] = a[0]
                return None
            if self._qt_name == "QTableWidget" and key == "item":
                return self._cells.get(a[:2])
            if self._qt_name == "QTableWidget" and key == "setItem":
                self._cells[a[:2]] = a[2]
                return None
            if self._qt_name == "QTableWidgetItem" and key == "data":
                return self._data["text"]
            if self._qt_name == "QFile" and key == "exists":
                return Path(self._args[0]).is_file()
            if self._qt_name in ("QDate", "QDateTime"):
                date = self._extra["date"]
                if key in ("year", "month", "day", "dayOfWeek", "daysInMonth"):
                    return {
                        "year": date.year,
                        "month": date.month,
                        "day": date.day,
                        "dayOfWeek": date.isoweekday(),
                        "daysInMonth": (
                            datetime.date(
                                date.year + (date.month == 12), date.month % 12 + 1, 1
                            )
                            - datetime.timedelta(days=1)
                        ).day,
                    }[key]
                if key == "addDays":
                    value = date + datetime.timedelta(days=a[0])
                    return classes["QDate"](value.year, value.month, value.day)
                if key == "setDate":
                    try:
                        self._extra["date"] = datetime.date(*a[:3])
                    except ValueError:
                        return False
                    return True
                if key == "toString":
                    return date.isoformat()
            if self._qt_name == "QTime":
                if key in ("hour", "minute", "second"):
                    return self._data[key]
                if key == "toString":
                    return f"{self._data['hour']:02}:{self._data['minute']:02}"
            if self._qt_name == "QFont" and key in (
                "family",
                "pointSize",
                "bold",
                "italic",
                "underline",
                "weight",
            ):
                return self._data.get(
                    key, False if key in ("bold", "italic", "underline") else 50
                )
            if self._qt_name == "QFontDatabase":
                if key in ("styles", "families"):
                    return ["Regular", "Bold"] if key == "styles" else ["Sans", "Serif"]
                if key in ("pointSizes", "smoothSizes", "standardSizes"):
                    return [8, 10, 12, 16]
                if key == "styleString":
                    return "Regular"
                if key == "font":
                    return classes["QFont"](a[0], a[2])
            if self._qt_name == "QFontMetrics":
                if key in ("height", "ascent", "descent", "xHeight"):
                    return {"height": 20, "ascent": 15, "descent": 5, "xHeight": 8}[key]
                if key == "width":
                    return len(a[0]) * 8
            if key == "printer" and self._qt_name in (
                "QPrintDialog",
                "QPrintPreviewDialog",
            ):
                if "printer" not in self._extra:
                    self._extra["printer"] = classes["QPrinter"]()
                return self._extra["printer"]
            if key == "currentWidget" and self._qt_name in (
                "QTabWidget",
                "QStackedWidget",
            ):
                return self._items[self._data["currentIndex"]] if self._items else None
            if key == "window" and self._qt_name == "QPalette":
                return classes["QBrush"]()
            if key == "addResource" and self._qt_name == "QTextDocument":
                self._extra.setdefault("resources", {})[a[1]._args[0]] = a[2]
                return None
            if key in ("setFormat", "mergeCharFormat", "mergeCurrentCharFormat"):
                self._extra.setdefault("formats", []).append(a)
                return None
            if key == "previousBlockState":
                return self._data.get("currentBlockState", -1)
            if key == "write" and self._qt_name == "QTextDocumentWriter":
                Path(self._args[0]).write_text(a[0]._parent._data["text"])
                return True
            if key == "setModified" and self._qt_name == "QTextDocument":
                self._data["modified"] = a[0]
                self.emit("modificationChanged", a[0])
                return None
            if key == "find" and self._qt_name == "QTextDocument":
                result = classes["QTextCursor"]()
                result._extra["editor"] = self._parent
                result._extra["selection_text"] = a[0]
                result._extra["found"] = a[0] in self._parent._data["text"]
                return result
            if self._qt_name == "QLocale":
                if key in ("nativeLanguageName", "nativeCountryName"):
                    return (
                        "English" if key == "nativeLanguageName" else "United Kingdom"
                    )
                if key in ("language", "country"):
                    return enum("English" if key == "language" else "UnitedKingdom")
            if key == "setDateRange":
                self._data.update(minimumDate=a[0], maximumDate=a[1])
                return None
            if key == "setTimeRange":
                self._data.update(minimumTime=a[0], maximumTime=a[1])
                return None
            if key in ("setDate", "setSelectedDate"):
                prop = "date" if key == "setDate" else "selectedDate"
                old = self._data.get(prop)
                self._data[prop] = a[0]
                if old == a[0]:
                    return None
                self.emit("dateChanged", a[0]) if key == "setDate" else self.emit(
                    "selectionChanged"
                )
                return None
            if key in ("yearShown", "monthShown"):
                date = self._data.get("selectedDate", classes["QDate"]())
                return date.year() if key == "yearShown" else date.month()
            if key == "setDateTextFormat":
                self._props[a[0].toString()] = a[1]
                return None
            if key in ("dateTextFormat", "weekdayTextFormat", "headerTextFormat"):
                return classes["QTextCharFormat"]()
            if key == "display":
                self._data["value"] = a[0]
                return None
            if key == "addSeparator":
                action = classes["QAction"](self)
                self._items.append(action)
                return action
            if self._qt_name in ("QRect", "QRectF") and key == "center":
                return classes["QPoint"](
                    self._position[0] + self._position[2] // 2,
                    self._position[1] + self._position[3] // 2,
                )
            if (
                key == "layout"
                and self._qt_name == "QMainWindow"
                and self._layout is None
            ):
                self._layout = classes["QGridLayout"](self)
                return self._layout
            if key in (
                "charFormat",
                "blockFormat",
                "frameFormat",
                "currentFrame",
                "insertFrame",
                "insertTable",
                "cellAt",
                "firstCursorPosition",
            ):
                types = {
                    "charFormat": "QTextCharFormat",
                    "blockFormat": "QTextBlockFormat",
                    "frameFormat": "QTextFrameFormat",
                    "currentFrame": "QTextFrame",
                    "insertFrame": "QTextFrame",
                    "insertTable": "QTextTable",
                    "cellAt": "QTextTableCell",
                    "firstCursorPosition": "QTextCursor",
                }
                result = classes[types[key]]()
                result._extra["editor"] = self._extra.get("editor")
                if key == "insertTable":
                    result._data.update(rowCount=a[0], columnCount=a[1])
                return result
            if self._qt_name == "QTextTable":
                if key in ("rows", "columns"):
                    return self._data["rowCount" if key == "rows" else "columnCount"]
                if key == "insertRows":
                    self._data["rowCount"] += a[1]
                    return None
            if key == "insertText" and self._qt_name == "QTextCursor":
                editor = self._extra.get("editor")
                if editor is not None:
                    selected = self._extra.pop("selection_text", "")
                    editor._data["text"] = (
                        editor._data["text"].replace(selected, a[0], 1)
                        if selected
                        else editor._data["text"] + a[0]
                    )
                return None
            if key == "insertBlock":
                editor = self._extra.get("editor")
                if editor is not None:
                    editor._data["text"] += "\n"
                return None
            if key == "insert" and self._qt_name == "QLineEdit":
                self._data["text"] += a[0]
                self.emit("textChanged", self._data["text"])
                return None
            if key in ("lighter", "darker") and self._qt_name == "QColor":
                return classes["QColor"](self)
            if key == "rgb" and self._qt_name == "QColor":
                return (
                    0xFF000000
                    | self._data["red"] << 16
                    | self._data["green"] << 8
                    | self._data["blue"]
                )
            if key in ("lastPosition", "position"):
                return 0
            if key in ("setHtml",):
                self._data["text"] = a[0]
                return None
            if key == "toHtml":
                return self._data["text"]
            if key in ("textColor", "foreground", "color"):
                return (
                    classes["QBrush"]() if key == "foreground" else classes["QColor"]()
                )
            if key == "alignment":
                return self._data.get("alignment", enum("AlignLeft"))
            if key == "isUndoAvailable" or key == "isRedoAvailable":
                return False
            if key == "font" and self._qt_name == "QFontInfo":
                return self._args[0]
            if key == "family" and self._qt_name == "QFontInfo":
                return self._args[0].family()
            # Value-class setters do not implicitly construct values from enums.
            value_types = {
                "setEasingCurve": "QEasingCurve",
                "setColorAt": "QColor",
                "setDefaultTextColor": "QColor",
                "setTextColor": "QColor",
                "setColor": "QColor",
                "setCursor": "QCursor",
            }
            if key in value_types:
                expected = value_types[key]
                if not a or not isinstance(a[-1], classes[expected]):
                    raise TypeError(
                        f"{key} requires {expected}; bare enum/int rejected"
                    )
            if (
                key == "fill"
                and self._qt_name == "QPixmap"
                and len(a) == 1
                and not isinstance(a[0], classes["QColor"])
            ):
                raise TypeError("fill requires QColor; bare enum/int rejected")
            if key == "setPen" and self._qt_name == "QPainter":
                styles = {
                    enum(name)
                    for name in (
                        "NoPen",
                        "SolidLine",
                        "DashLine",
                        "DotLine",
                        "DashDotLine",
                        "DashDotDotLine",
                        "CustomDashLine",
                    )
                }
                if not a or not (
                    isinstance(a[0], (classes["QPen"], classes["QColor"]))
                    or isinstance(a[0], int)
                    and a[0] in styles
                ):
                    raise TypeError("setPen requires QPen, QColor or Qt.PenStyle")
            if self._qt_name == "QLineF":
                p1 = self._args[0] if self._args else classes["QPointF"]()
                p2 = self._args[1] if len(self._args) > 1 else classes["QPointF"]()
                dx = p2._position[0] - p1._position[0]
                dy = p2._position[1] - p1._position[1]
                if key in ("dx", "dy", "length"):
                    return (
                        dx
                        if key == "dx"
                        else dy
                        if key == "dy"
                        else (dx * dx + dy * dy) ** 0.5
                    )
                if key in ("p1", "p2"):
                    return p1 if key == "p1" else p2
            if self._qt_name == "QTransform" and key in (
                "translate",
                "scale",
                "rotate",
            ):
                return self
            if key == "line":
                return self._data.get("line", classes["QLineF"]())
            if key == "textCursor":
                cursor = classes["QTextCursor"]()
                cursor._extra["editor"] = self
                return cursor
            if key == "buttons":
                return list(self._items)
            if key == "button" and self._qt_name == "QButtonGroup":
                return self._extra["button_ids"][a[0]]
            if key == "checkedId":
                return next(
                    (
                        key
                        for key, button in self._extra.get("button_ids", {}).items()
                        if button.isChecked()
                    ),
                    -1,
                )
            if key == "matrix":
                return classes["QTransform"]()
            if key in ("dx", "dy") and self._qt_name == "QTransform":
                return 0
            if key == "assignProperty":
                self._extra.setdefault("assignments", []).append(a)
                return None
            if key == "addState":
                self._extra.setdefault("states", []).append(a[0])
                a[0]._parent = self
                return None
            if key == "setInitialState":
                self._extra["initialState"] = a[0]
                return None
            if key == "initialState":
                return self._extra.get("initialState")
            if key == "machine":
                item = self
                while item is not None and item._qt_name != "QStateMachine":
                    item = item._parent
                return item
            if key == "addTransition":
                transition = classes["QSignalTransition"](self)
                transition._extra["source"] = self
                if len(a) == 3:
                    transition._extra.update(
                        sender=a[0], signal=a[1].lstrip("2"), target=a[2]
                    )
                    a[0]._extra.setdefault("transitions", []).append(transition)
                elif len(a) == 1:
                    transition = a[0]
                    transition._extra["source"] = self
                return transition
            if key == "addAnimation":
                self._items.append(a[0])
                return None
            if key == "setTargetState":
                self._extra["target"] = a[0]
                return None
            if key == "configuration":
                return list(self._extra.get("active_states", set()))
            if key == "isRunning":
                return self._active
            if key == "start" and self._qt_name == "QStateMachine":
                self._active = True
                self._extra["active_states"] = set()
                self._enter_state(self._extra["initialState"])
                return None
            if key == "stop" and self._qt_name == "QStateMachine":
                self._active = False
                self._extra["active_states"] = set()
                return None
            if key == "setScene":
                self._extra["scene"] = a[0]
                return None
            if key == "scene":
                return self._extra.get("scene")
            if key == "addItem" and self._qt_name == "QGraphicsScene":
                self._items.append(a[0])
                a[0]._extra["scene"] = self
                return None
            if key == "items" and self._qt_name == "QGraphicsScene":
                return self._items[:]
            if key == "removeItem":
                self._items.remove(a[0])
                return None
            if key == "selectedItems":
                return [item for item in self._items if item._data.get("selected")]
            if key == "clearSelection":
                for item in self._items:
                    item._data["selected"] = False
                return None
            if key == "childItems":
                return [
                    child
                    for child in self._children
                    if child._qt_name.startswith("QGraphics")
                ]
            if key in (
                "sceneRect",
                "itemsBoundingRect",
                "childrenBoundingRect",
                "boundingRect",
                "windowFrameRect",
            ):
                return classes["QRectF"](-20, -20, 80, 80)
            if key in ("collidingItems",):
                return []
            if key == "pos":
                return classes["QPointF"](*self._position[:2])
            if key == "geometry":
                return classes["QRectF"](*self._position)
            if key in ("mapToParent", "mapToScene", "mapFromScene", "mapFromItem"):
                if (
                    a
                    and isinstance(a[0], Native)
                    and a[0]._qt_name in ("QPoint", "QPointF")
                ):
                    return classes["QPointF"](*a[0]._position[:2])
                return classes["QPointF"](*a[-2:])
            if key in ("setMenu", "setDefaultAction"):
                self._extra[key[3:4].lower() + key[4:]] = a[0]
                return None
            if key in ("menu", "defaultAction"):
                return self._extra.get(key)
            if key == "setCurrentTime" and self._qt_name == "QPropertyAnimation":
                self._data["currentTime"] = a[0]
                if type(self).__dict__.get("updateCurrentTime"):
                    self.updateCurrentTime(a[0])
                return None
            if key == "pointAtPercent":
                return classes["QPointF"](a[0] * 100, a[0] * 100)
            if key == "valueForProgress":
                return a[0]
            if key == "easingCurve":
                value = self._data.get("easingCurve")
                return (
                    value
                    if isinstance(value, Native)
                    else classes["QEasingCurve"](value)
                )
            if key in ("period", "amplitude", "overshoot"):
                return self._data.get(key, 0.3 if key == "period" else 1.0)
            if key in ("red", "green", "blue"):
                return self._data[key]
            if key == "lighter":
                return self
            if key == "name" and self._qt_name == "QColor":
                return "#{:02x}{:02x}{:02x}".format(
                    *tuple(self._data[n] for n in ("red", "green", "blue"))
                )
            if key in ("rotation", "opacity", "scale", "zValue"):
                return self._data.get(key, 0)
            if key == "first":
                return self._items[0]
            if key == "polygon":
                return self._data.get(key, classes["QPolygonF"]())
            if key == "toFillPolygon":
                return classes["QPolygonF"]([])
            if key == "size" and self._qt_name in ("QRect", "QRectF"):
                return classes["QSizeF"](*self._position[2:])
            if key == "toSize":
                return classes["QSize"](*self._position[:2])
            if key == "toPoint":
                return classes["QPoint"](*self._position[:2])
            if (
                key in ("translate", "rotate", "scale")
                and self._qt_name == "QTransform"
            ):
                return self

            if self._qt_name == "QAbstractListModel" and key == "columnCount":
                return 1
            if self._qt_name == "QBuffer":
                if key == "open":
                    return True
                if key == "setData":
                    self._extra["bytes"] = a[0].data()
                    return None
                if key == "data":
                    return ByteArray(self._extra.get("bytes", b""))
            if self._qt_name == "QDataStream":
                buffer = self._args[0]
                if key == "writeQVariant":
                    values = self._extra.setdefault("values", [])
                    values.append(a[0])
                    token = b"fixture:" + str(id(values)).encode()
                    streams[token] = values[:]
                    buffer._extra["bytes"] = token
                    return None
                if key == "readQVariant":
                    values = streams.get(buffer._extra.get("bytes"))
                    pos = self._extra.get("read_position", 0)
                    self._extra["read_position"] = pos + 1
                    if values is None or pos >= len(values):
                        self._extra["corrupt"] = True
                        return None
                    return values[pos]
                if key == "atEnd":
                    token = buffer._extra.get("bytes", b"")
                    return not token or self._extra.get("read_position", 0) >= len(
                        streams.get(token, [None])
                    )
                if key == "status":
                    return (
                        enum("ReadCorruptData")
                        if self._extra.get("corrupt")
                        else enum("Ok")
                    )
            if self._qt_name == "QMimeData":
                if key == "setData":
                    self._props[a[0]] = (
                        a[1] if isinstance(a[1], ByteArray) else ByteArray(a[1])
                    )
                    return None
                if key == "data":
                    return self._props.get(a[0], ByteArray())
                if key == "hasFormat":
                    return a[0] in self._props
                if key == "hasText":
                    return bool(self._data["text"])
                if key in ("hasColor", "hasImage"):
                    return (
                        "colorData" if key == "hasColor" else "imageData"
                    ) in self._data
                if key in ("colorData", "imageData"):
                    return self._data.get(key)
            if self._qt_name == "QDrag" and key == "exec":
                return getattr(qt, "_drag_result", enum("IgnoreAction"))
            if key == "childAt":
                return next(
                    (
                        child
                        for child in self._children
                        if child.isVisible() and child.inherits("QLabel")
                    ),
                    None,
                )
            if key == "viewOptions":
                return classes["QStyleOptionViewItem"]()
            if key == "itemDelegate":
                return classes["QAbstractItemDelegate"]()
            if key in ("base",) and self._qt_name == "QPalette":
                return classes["QBrush"]()
            if self._qt_name in ("QRect", "QRectF"):
                if key == "isValid":
                    return self._position[2] > 0 and self._position[3] > 0
                if key == "topLeft":
                    return classes["QPoint"](*self._position[:2])
                if key == "adjusted":
                    x, y, w, h = self._position
                    return classes["QRect"](
                        x + a[0], y + a[1], w + a[2] - a[0], h + a[3] - a[1]
                    )
                if key == "normalized":
                    return self
                if key == "united":
                    return a[0]
            if self._qt_name == "QFontMetrics" and key == "size":
                return classes["QSize"](len(a[1]) * 8, 20)
            if self._qt_name in ("QImage", "QPixmap"):
                if key == "pixel":
                    return self._extra.get("pixels", {}).get(a[:2], 0xFFFFFFFF)
                if key == "setPixel":
                    self._extra.setdefault("pixels", {})[a[:2]] = a[2]
                    return None
                if key in ("width", "height"):
                    return self._data[key]
                if key == "size":
                    return classes["QSize"](self._data["width"], self._data["height"])
                if key == "copy":
                    result = classes[self._qt_name](
                        *(
                            a[2:]
                            if len(a) == 4
                            else (self._data["width"], self._data["height"])
                        )
                    )
                    result._extra["pixels"] = dict(self._extra.get("pixels", {}))
                    return result
                if key == "scaled":
                    return classes[self._qt_name](*a[:2])
            if self._qt_name == "QModelIndex":
                if key in ("row", "column", "internalId", "internalPointer"):
                    return self._extra.get(key, 0 if key.startswith("internal") else -1)
                if key == "isValid":
                    return self._extra.get("row", -1) >= 0
                if key == "parent":
                    model = self._extra.get("model")
                    return model.parent(self) if model else classes["QModelIndex"]()
                if key == "data":
                    return self._extra["model"].data(self, *a)
            if key in ("createIndex", "index") and self._qt_name in (
                "QAbstractItemModel",
                "QAbstractListModel",
                "QStandardItemModel",
            ):
                result = classes["QModelIndex"]()
                if key == "createIndex" or (
                    0 <= a[0] < self.rowCount() and 0 <= a[1] < self.columnCount()
                ):
                    result._extra.update(
                        row=a[0],
                        column=a[1],
                        model=self,
                        internalId=a[2] if key == "createIndex" else 0,
                    )
                return result
            if key == "hasIndex":
                return 0 <= a[0] < self.rowCount(a[2]) and 0 <= a[1] < self.columnCount(
                    a[2]
                )
            if (
                key in ("insertRow", "insertColumn", "removeRow", "removeColumn")
                and self._qt_name == "QAbstractItemModel"
            ):
                return getattr(self, key + "s")(
                    a[0], 1, *(a[1:] or (classes["QModelIndex"](),))
                )
            if self._qt_name == "QStandardItemModel":
                if key == "setHorizontalHeaderLabels":
                    self._data["columnCount"] = len(a[0])
                    self._extra["headers"] = list(a[0])
                    return None
                if key == "setItem":
                    self._data["rowCount"] = max(self._data["rowCount"], a[0] + 1)
                    self._data["columnCount"] = max(self._data["columnCount"], a[1] + 1)
                    self._cells[a[:2]] = a[2]
                    return None
                if key == "setData":
                    role = a[2] if len(a) > 2 else enum("DisplayRole")
                    if role == enum("EditRole"):
                        role = enum("DisplayRole")
                    self._props[(a[0].row(), a[0].column(), role)] = a[1]
                    self.emit("dataChanged", a[0], a[0], [])
                    return True
                if key == "data":
                    role = a[1] if len(a) > 1 else enum("DisplayRole")
                    cell = self._cells.get((a[0].row(), a[0].column()))
                    return self._props.get(
                        (a[0].row(), a[0].column(), role),
                        cell._data["text"] if cell else None,
                    )
                if key in ("insertRows", "removeRows"):
                    self._data["rowCount"] += a[1] if key == "insertRows" else -a[1]
                    if key == "removeRows":
                        self._props.clear()
                    return True
                if key == "parent":
                    return classes["QModelIndex"]()
            if key in ("dataChanged", "headerDataChanged"):
                self.emit(key, *a)
                return None
            if key == "selectionModel":
                if "selection" not in self._extra:
                    self._extra["selection"] = classes["QItemSelectionModel"](
                        self._extra.get("model"), self
                    )
                return self._extra["selection"]
            if key == "setSelectionModel":
                self._extra["selection"] = a[0]
                return None
            if key == "currentIndex" and self._qt_name in (
                "QItemSelectionModel",
                "QTreeView",
                "QTableView",
                "QAbstractItemView",
                "QListView",
            ):
                if self._qt_name != "QItemSelectionModel":
                    return self.selectionModel()._invoke("currentIndex")
                return self._extra.get("current", classes["QModelIndex"]())
            if (
                key in ("select", "setCurrentIndex")
                and self._qt_name == "QItemSelectionModel"
            ):
                self._extra["current"] = a[0]
                self._extra["selected"] = [a[0]] if a[0].isValid() else []
                self.emit(
                    "selectionChanged",
                    classes["QItemSelection"](),
                    classes["QItemSelection"](),
                )
                return None
            if key == "selectedIndexes":
                if self._qt_name in ("QListView", "QTableView", "QTreeView"):
                    return self.selectionModel()._invoke("selectedIndexes")
                return self._extra.get("selected", [])
            if key == "selection":
                result = classes["QItemSelection"]()
                result._items = self._extra.get("selected", [])
                return result
            if key == "isEmpty" and self._qt_name == "QItemSelection":
                return not self._items
            if key in ("rootIndex",):
                return classes["QModelIndex"]()
            if key in ("columnWidth", "rowHeight", "frameWidth"):
                return self._props.get(
                    (key, a[0] if a else 0), 100 if key == "columnWidth" else 20
                )
            if key in ("setColumnWidth", "setRowHeight"):
                self._props[
                    ("columnWidth" if key == "setColumnWidth" else "rowHeight", a[0])
                ] = a[1]
                return None
            if key == "setPos":
                self._position[:2] = a[0]._position[:2] if len(a) == 1 else a
                return None
            if key == "addPixmap":
                item = classes["QGraphicsPixmapItem"](a[0])
                self._items.append(item)
                return item
            if key == "graphicsEffect":
                return self._data.get("graphicsEffect")
            if key == "offset":
                return self._data.get("offset", classes["QPointF"](8, 8))
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
                "horizontalScrollBar",
                "viewport",
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
                    "horizontalScrollBar": "QScrollBar",
                    "viewport": "QWidget",
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
                self.emit(
                    "textChanged", a[-1]
                ) if self._qt_name == "QLineEdit" else self.emit("textChanged")
                return None
            if key == "text":
                return self._cells.get(a[0], "") if a else self._data["text"]
            if key == "toPlainText":
                return self._data["text"]
            if key == "setDisabled":
                self._data["enabled"] = not a[0]
                return None
            if key == "setVisible":
                self.visible = bool(a[0])
                return None
            if key == "setCurrentRow":
                self._data["currentRow"] = a[0]
                self.emit("currentItemChanged", self._items[a[0]], None)
                self.emit("currentRowChanged", a[0])
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
                old = self._data["value"]
                self._data["value"] = a[0]
                if old != a[0]:
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
                if key == "setModel" and a[0] is None:
                    selection = self._extra.get("selection")
                    assert selection is None or all(
                        not signal.callbacks for signal in selection._signals.values()
                    ), "Disconnect Python selection slots before detaching the model"
                self._extra[key[3:].lower()] = a[0]
                return None
            if key in ("model", "widget"):
                return self._extra.get(key)
            if key == "setGeometry":
                self._position = a[0]._position[:] if len(a) == 1 else list(a)
                if self._fields.get("geometry") == "value":
                    self.geometry = classes["QRect"](*self._position)
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
            if key == "isEnabled":
                return self._data["enabled"]
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
            if key == "addAction":
                if len(a) == 1 and isinstance(a[0], classes["QAction"]):
                    self._items.append(a[0])
                    return a[0] if self._qt_name == "QActionGroup" else None
                callbacks = [arg for arg in a if callable(arg)]
                receiver_slot = (
                    len(a) >= 3 and isinstance(a[-2], Native) and isinstance(a[-1], str)
                ) or (
                    len(a) >= 4 and isinstance(a[-3], Native) and isinstance(a[-2], str)
                )
                if callbacks or receiver_slot:
                    text = next(arg for arg in a if isinstance(arg, str))
                    action = classes["QAction"](text, self)
                    for callback in callbacks:
                        action.connect("triggered()", callback)
                    self._items.append(action)
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
                        "addToolBar": "QToolBar",
                        "addButton": "QPushButton",
                    }[key]
                    obj = classes[typ](obj, self)
                self._items.append(obj)
                if (
                    key == "addButton"
                    and self._qt_name == "QButtonGroup"
                    and len(a) > 1
                ):
                    self._extra.setdefault("button_ids", {})[a[1]] = a[0]
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
            if key == "end" and self._qt_name == "QPainter":
                assert self._active, "QPainter.end called twice"
                self._active = False
                return True
            if key == "isActive":
                return self._active
            if key == "stringList":
                return self._items
            if key == "isNull":
                if self._qt_name == "QTextCursor":
                    return not self._extra.get("found", True)
                return self._qt_name in ("QPixmap", "QImage") and not self._args
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
                    "width": 0 if self._qt_name in ("QSize", "QSizeF") else 2,
                    "height": 1 if self._qt_name in ("QSize", "QSizeF") else 3,
                    "right": 2,
                    "bottom": 3,
                }[key]
                return self._position[idx]
            if key in ("sizeHint", "minimumSize", "minimumSizeHint"):
                return classes["QSize"](80, 30)
            if key in ("geometry", "rect", "contentsRect"):
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
                return enum("Running") if self._active else enum("NotRunning")
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
                if isinstance(pattern, Native):
                    pattern = pattern._data.get("pattern", pattern._args[0])
                try:
                    self._match = re.compile(pattern).search(
                        a[0], a[1] if len(a) > 1 else 0
                    )
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
            if key in self._data:
                return self._data[key]
            return None

        def __iter__(self):
            return iter(self._items)

        def __eq__(self, other):
            if self._qt_name in ("QDate", "QDateTime", "QTime"):
                return (
                    isinstance(other, Native)
                    and self._extra.get("date") == other._extra.get("date")
                    and self._data.get("hour") == other._data.get("hour")
                )
            return self is other

        __hash__ = object.__hash__

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
    qt.QtCore.Qt.mightBeRichText = lambda text: "<" in text

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
    qt._painters = []
    return qt
