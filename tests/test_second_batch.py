# this_file: tests/test_second_batch.py
"""Second-batch import, model, interaction and worker boundary checks."""

import hashlib
import json
import threading
from importlib import util
from pathlib import Path
from types import SimpleNamespace

import pytest
from qt_doubles import Signal, native_double

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "catalog/ports.json").read_text(encoding="utf-8"))
NEW = [
    r
    for r in MANIFEST["ports"]
    if r["implementation"] == "implemented"
    and "/pyqt-examples/" in r["target_path"]
    and r["source_id"]
    not in {
        "ce3e17a7a2a03a02",
        "f5ddfd0eaacbf845",
        "79cc15680bc2cebb",
        "402068f40005cd66",
    }
    # Batch 9 chat ports use the strict official doubles and owned localhost peers.
    and not r["source"]["path"].startswith("src/11 PyQt Thread example/")
]
CONNECTED_PORTS = NEW + [
    r for r in MANIFEST["ports"] if r["name"] == "Signals and Slots"
]


def load(record):
    spec = util.spec_from_file_location(
        "port_" + record["source_id"], ROOT / record["target_path"]
    )
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def batch_qt(native_boundary, monkeypatch):
    qt = native_boundary[0]
    base = qt.QtGui.QWidget
    gui_thread = threading.get_ident()

    @native_double
    class Palette:
        def __init__(self):
            self.colors = {}

        def setColor(self, role, color):
            self.colors[role] = color

        def color(self, role):
            return self.colors[role]

    @native_double
    class Widget(base):
        Preferred = Ignored = Password = Save = Ok = 1
        Discard, Cancel = 2, 4

        def __init__(self, *args):
            super().__init__(args[0] if args and isinstance(args[0], str) else "")
            self.value, self.maximum, self.count = 0, 99, 0
            self.title, self.windowTitle = self.text, ""
            self.palette = Palette()
            self.toggled = Signal()
            self.activated = Signal()
            self.returnPressed = Signal()
            self.destroyed = Signal()
            self.triggered = Signal()
            self.buttonClicked = Signal()
            self.items, self.menus, self.actions = [], [], []
            self.rowCount, self.columnCount = 10, 10
            self.modified = False
            self.checked = False

        def __getattr__(self, name):
            if name.startswith("set") or name in {
                "addStretch",
                "update",
                "mousePressEvent",
                "paintEvent",
            }:

                def setter(*args):
                    if len(args) == 1:
                        attr = name[3:4].lower() + name[4:]
                        object.__setattr__(self, attr, args[0])

                return setter
            raise AttributeError(name)

        def close(self):
            event = SimpleNamespace(accept=lambda: None, ignore=lambda: None)
            if hasattr(type(self), "closeEvent"):
                self.closeEvent(event)
            self.visible = False

        def children(self):
            return []

        def inherits(self, name):
            return True

        def connect(self, signature, callback):
            assert signature == "activated(QString)"
            self.activated.connect(callback)

        def disconnect(self, signature, callback):
            assert signature == "activated(QString)"
            self.activated.disconnect(callback)

        def checkState(self):
            return self.check_state

        def setCheckState(self, state):
            object.__setattr__(self, "check_state", state)

        def setRange(self, minimum, maximum):
            object.__setattr__(self, "minimum", minimum)
            self.maximum = maximum

        def isChecked(self):
            return self.checked

        def style(self):
            return Style()

        def findChildren(self, cls):
            return []

        def addItems(self, items):
            self.items.extend(items)

        def addTab(self, widget, label):
            self.items.append((widget, label))
            self.count += 1

        def menuBar(self):
            return self

        def addMenu(self, label):
            menu = Widget(label)
            self.menus.append(menu)
            return menu

        def addAction(self, action):
            self.actions.append(action)

        def document(self):
            return self

        def isModified(self):
            return self.modified

        def setPlainText(self, text):
            self.text = text
            self.modified = False

        def toPlainText(self):
            return self.text

        def appendPlainText(self, text):
            assert threading.get_ident() == gui_thread, (
                "Qt must only be touched on the GUI thread"
            )
            self.text += text + "\n"

        def clear(self):
            self.text = ""

        def viewport(self):
            return self

        def mousePressEvent(self, event):
            pass

        def paintEvent(self, event):
            pass

        def standardButton(self, button):
            return button

    @native_double
    class Style(Widget):
        def standardPalette(self):
            return Palette()

    @native_double
    class Timer(Widget):
        def __init__(self, parent):
            super().__init__(parent)
            self.timeout = Signal()
            self.active = False
            self.interval = 0

        def start(self, interval):
            self.active, self.interval = True, interval

        def stop(self):
            self.active = False

    @native_double
    class Index:
        def __init__(self, row=-1, column=-1, path=""):
            self.r, self.c, self.path = row, column, path

        def isValid(self):
            return self.r >= 0 and self.c >= 0

        def row(self):
            return self.r

        def column(self):
            return self.c

    @native_double
    class Model(Widget):
        def __init__(self, *args):
            super().__init__(*args)
            del self.rowCount
            del self.columnCount

        def index(self, row, column=0):
            return Index(row, column) if isinstance(row, int) else Index(0, 0, row)

        def filePath(self, index):
            return index.path

        def rowCount(self, parent=None):
            return 3

        def columnCount(self, parent=None):
            return 4

    @native_double
    class ListModel(Model):
        def __init__(self, strings, parent):
            super().__init__(parent)
            self.strings = strings

        def stringList(self):
            return self.strings

    Widget.rootIndex = lambda self: self.rootIndex_value
    Widget.setRootIndex = lambda self, index: object.__setattr__(
        self, "rootIndex_value", index
    )
    for name in (
        "QWidget",
        "QDialog",
        "QMainWindow",
        "QPlainTextEdit",
        "QLineEdit",
        "QAction",
        "QTreeView",
        "QListView",
        "QTableView",
        "QComboBox",
        "QLabel",
        "QCheckBox",
        "QGroupBox",
        "QRadioButton",
        "QPushButton",
        "QTabWidget",
        "QTableWidget",
        "QTextEdit",
        "QSpinBox",
        "QDateTimeEdit",
        "QSlider",
        "QScrollBar",
        "QDial",
        "QProgressBar",
        "QMessageBox",
        "QSizePolicy",
    ):
        setattr(qt.QtGui, name, Widget)

    @native_double
    class Layout:
        def __init__(self, *args):
            self.widgets = []

        def addWidget(self, widget, *args):
            self.widgets.append(widget)

        def __getattr__(self, name):
            return lambda *args: None

    for name in ("QVBoxLayout", "QHBoxLayout", "QGridLayout"):
        setattr(qt.QtGui, name, Layout)
    qt.QtGui.QStyleFactory = SimpleNamespace(
        keys=lambda: ["Windows", "Fusion"], create=lambda name: Style()
    )
    qt.QtGui.QDirModel = Model
    qt.QtGui.QKeySequence = type(
        "Key", (), {"Open": 1, "Save": 2, "__init__": lambda self, key: None}
    )
    qt.QtGui.QFileDialog = SimpleNamespace(
        getOpenFileName=lambda *args: "", getSaveFileName=lambda *args: ""
    )
    roles = (
        "Window",
        "WindowText",
        "Base",
        "AlternateBase",
        "ToolTipBase",
        "ToolTipText",
        "Text",
        "Button",
        "ButtonText",
        "BrightText",
        "Link",
        "Highlight",
        "HighlightedText",
    )
    for i, role in enumerate(roles):
        setattr(Palette, role, i)
    qt.QtGui.QPalette = Palette
    qt.QtGui.QColor = lambda *rgb: SimpleNamespace(name=lambda: "#353535")
    qt.QtGui.QPixmap = lambda path: SimpleNamespace(
        size=lambda: SimpleNamespace(width=lambda: 20, height=lambda: 20),
        isNull=lambda: False,
    )
    qt.QtGui.QPainter = lambda view: SimpleNamespace(
        drawPixmap=lambda *args: None, end=lambda: None
    )
    qt.QtCore.QPoint = lambda x, y: SimpleNamespace(x=lambda: x, y=lambda: y)
    qt.QtCore.QDateTime = SimpleNamespace(currentDateTime=lambda: "now")
    qt.QtCore.QTimer = Timer
    qt.QtGui.QAbstractTableModel = Model  # PythonQt placement
    qt.QtGui.QStringListModel = ListModel  # PythonQt placement
    qt.QtCore.QModelIndex = Index
    qt.QtCore.Qt = SimpleNamespace(
        WA_QuitOnClose=2,
        WA_DeleteOnClose=3,
        NonModal=0,
        WindowModal=1,
        NoFocus=0,
        Horizontal=1,
        DisplayRole=0,
        PartiallyChecked=1,
        white=1,
        red=2,
        black=3,
    )
    return qt


@pytest.mark.parametrize("record", NEW, ids=lambda r: r["name"])
def test_new_port_when_built_then_json_inspection_and_cleanup(record, batch_qt):
    handle = load(record).build(batch_qt)
    state = handle.snapshot()
    assert state["closed"] is False, record["name"]
    json.dumps(state)
    handle.close()
    assert handle.snapshot()["closed"] is True, record["name"]
    handle.close()


def test_batch_when_catalogued_then_all_entrypoints_and_resources_match():
    catalog = json.loads((ROOT / "catalog/sources.json").read_text())
    assert (
        MANIFEST["source_catalog_sha256"]
        == hashlib.sha256((ROOT / "catalog/sources.json").read_bytes()).hexdigest()
    ), "The port manifest must cite the current reviewed source catalog hash"
    by_id = {e["id"]: e for e in catalog["files"]}
    # Example 11 is covered by batch 9 with owned localhost peers under D4.
    numbers = {"02", "06", "07", "08", "09", "10", "12", "13", "14", "15"}
    expected = {
        e["id"]
        for e in by_id.values()
        if e["repository"] == "pyqt/examples"
        and e["path"].startswith("src/")
        and e["path"].split("/")[1][:2] in numbers
        and e.get("python", {}).get("role") == "entrypoint"
    }
    actual = {r["source_id"] for r in MANIFEST["ports"]}
    assert len(actual) == len(MANIFEST["ports"]), "Source IDs must be unique"
    assert expected <= actual, "Every requested upstream entrypoint must have a record"
    assert len(NEW) == 7, "02, 07, 09, 10, 12, 13 and 14 are implemented"
    for record in MANIFEST["ports"]:
        if record.get("clean_room_receipt"):
            assert record["license"]["selected"] == "Apache-2.0"
            assert (ROOT / record["clean_room_receipt"]).is_file()
            continue
        for resource in record["resources"]:
            original = by_id[resource["source_id"]]
            assert resource["source"]["sha256"] == original["sha256"]
            if record["implementation"] == "clean_room_pending":
                assert resource["archive"] and "license" not in resource
                continue
            data = (ROOT / resource["target_path"]).read_bytes()
            assert hashlib.sha256(data).hexdigest() == original["sha256"], resource[
                "target_path"
            ]


def record(name):
    return next(r for r in NEW if r["name"] == name)


def test_table_when_native_callback_contract_then_original_values_and_invalid_roles(
    batch_qt,
):
    handle = load(record("QAbstractTableModel")).build(batch_qt)
    model = handle.model
    assert handle.snapshot()["rows"][1] == ["Einstein", "1879-03-14", "Relativity"]
    assert model.data(batch_qt.QtCore.QModelIndex()) is None
    assert model.data(model.index(99, 0)) is None
    assert model.data(model.index(0, 0), 42) is None
    assert model.rowCount(model.index(0, 0)) == 0
    assert model.headerData(-1, 1) is None
    assert model.headerData(0, 2) is None
    handle.close()


def test_editor_when_actions_triggered_then_utf8_roundtrip_and_cancel(
    batch_qt, tmp_path
):
    handle = load(record("Qt Text Editor")).build(batch_qt)
    window = handle.widget
    text = window.centralWidget
    from tests.test_official_batch import owned_directory

    source = owned_directory(handle) / "source.txt"
    source.write_text("Ą–字体", encoding="utf-8")
    batch_qt.QtGui.QFileDialog.getOpenFileName = lambda *args: str(source)
    actions = window.menus[0].actions
    actions[0].triggered.emit()
    assert handle.snapshot()["text"] == "Ą–字体"
    text.text, text.modified = "Changed Ą", True
    actions[1].triggered.emit()
    assert source.read_text(encoding="utf-8") == "Changed Ą"
    assert not text.modified
    text.modified = True
    event = SimpleNamespace(accept=lambda: None, ignore=lambda: None)
    window.closeEvent(event)
    box = handle.alerts[-1].widget
    box.buttonClicked.emit(batch_qt.QtGui.QMessageBox.Cancel)
    assert text.modified, "Cancel must preserve unsaved edits"
    box.buttonClicked.emit(batch_qt.QtGui.QMessageBox.Save)
    assert not text.modified
    handle.close()


def test_numbered_editor_reads_user_file_but_refuses_overwriting_it(batch_qt, tmp_path):
    handle = load(record("Qt Text Editor")).build(batch_qt)
    source = tmp_path / "user.txt"
    source.write_text("Read Ą–字体", encoding="utf-8")
    try:
        batch_qt.QtGui.QFileDialog.getOpenFileName = lambda *args: str(source)
        actions = handle.widget.menus[0].actions
        actions[0].triggered.emit()
        assert handle.snapshot()["text"] == "Read Ą–字体"
        text = handle.widget.centralWidget
        text.text, text.modified = "Changed", True
        actions[1].triggered.emit()
        assert source.read_text(encoding="utf-8") == "Read Ą–字体"
        assert text.modified and "temporary directory" in handle.snapshot()["error"]
    finally:
        handle.close()


def test_gallery_when_timer_advances_then_original_values_and_progress(batch_qt):
    handle = load(record("PyQt Widgets")).build(batch_qt)
    state = handle.snapshot()
    assert state["values"] == {"spin": 50, "slider": 40, "scroll": 60, "dial": 30}
    assert state["table_rows"] == state["table_columns"] == 10
    assert state["password"] == "s3cRe7"
    assert state["tab_count"] == 2 and state["radio_checked"]
    assert state["tri_state"] == batch_qt.QtCore.Qt.PartiallyChecked
    handle.widget.timer.timeout.emit()
    assert handle.snapshot()["progress"] == 100, "Original one-percent remainder step"
    timer = handle.widget.timer
    handle.close()
    assert not timer.active


def test_painter_when_clicked_then_holes_are_inspectable_and_painter_ends(batch_qt):
    drawn, ended = [], []
    batch_qt.QtGui.QPainter = lambda view: SimpleNamespace(
        drawPixmap=lambda point, image: drawn.append(point),
        end=lambda: ended.append(True),
    )
    handle = load(record("QPainter")).build(batch_qt)
    text = handle.widget.centralWidget

    class Point:
        def x(self):
            return 30

        def y(self):
            return 40

        def __sub__(self, other):
            return (self.x() - other.x(), self.y() - other.y())

    text.mousePressEvent(SimpleNamespace(pos=Point))
    text.paintEvent(SimpleNamespace())
    assert handle.snapshot()["holes"] == [[30, 40]]
    assert drawn == [(20, 30)] and ended == [True]
    assert handle.snapshot()["sound_supported"] is False
    handle.close()


def test_editor_when_open_or_save_fails_then_unsaved_text_is_preserved(
    batch_qt, tmp_path
):
    handle = load(record("Qt Text Editor")).build(batch_qt)
    text = handle.widget.centralWidget
    text.text, text.modified = "Unsaved", True
    actions = handle.widget.menus[0].actions
    batch_qt.QtGui.QFileDialog.getOpenFileName = lambda *args: str(tmp_path / "missing")
    actions[0].triggered.emit()
    assert handle.snapshot()["text"] == "Unsaved"
    assert handle.snapshot()["modified"] and handle.snapshot()["error"]
    batch_qt.QtGui.QFileDialog.getSaveFileName = lambda *args: str(tmp_path)
    actions[2].triggered.emit()
    assert handle.snapshot()["modified"] and handle.snapshot()["error"]
    handle.close()


def test_blocked_when_launched_then_reason_before_host_import():
    from fontlab_python_examples import launch

    for r in MANIFEST["ports"]:
        if r["implementation"] == "blocked":
            with pytest.raises(NotImplementedError, match="not ported"):
                launch(r["source_id"])


@pytest.mark.parametrize("port", CONNECTED_PORTS, ids=lambda r: r["name"])
def test_port_when_closed_then_disconnects_before_releasing_and_deleting(
    port, batch_qt
):
    expected = {
        "PyQt Widgets": 7,
        "Qt Text Editor": 5,
        "Qt dark theme": 5,
        "QPainter": 5,
        "QTreeView": 0,
        "QListView": 0,
        "QAbstractTableModel": 0,
        "Signals and Slots": 1,
    }
    handle = load(port).build(batch_qt)
    assert len(handle.connections) == expected[port["name"]], (
        "Record every port connection"
    )
    signals = []
    for obj, signature, slot in handle.connections:
        signal = obj.activated if signature else obj
        assert slot in signal.callbacks, "Retain the exact connected slot"
        if signal not in signals:
            signals.append(signal)
    events = []
    timer = handle.widget.timer if port["name"] == "PyQt Widgets" else None
    if timer is not None:
        stop_timer = timer.stop

        def stop():
            events.append("timer_stopped")
            stop_timer()

        timer.stop = stop

    def stopped():
        assert not handle.snapshot().get("thread_alive", False), (
            "Join worker before disconnect"
        )
        events.append("stopped")

    handle.cleanup.append(stopped)
    for signal in signals:
        disconnect = signal.disconnect

        def disconnect_slot(slot, disconnect=disconnect):
            assert "stopped" in events, "Stop cleanup must precede disconnection"
            events.append("disconnect")
            disconnect(slot)

        signal.disconnect = disconnect_slot

    def released():
        assert not handle.connections and not handle.callbacks
        assert handle.inspect_ui is dict and handle.model is None
        assert all(not signal.callbacks for signal in signals)
        events.append("released")

    handle.release.append(released)
    owner_close = handle.owner.close

    def close_owner():
        assert events[-1] == "released", (
            "Release all references before native owner close"
        )
        assert not handle.cleanup and not handle.release
        if timer is not None:
            assert events[0] == "timer_stopped" and not timer.active
            assert not handle.widget.controls
            assert "timer" not in handle.widget.__dict__
        events.append("owner_closed")
        owner_close()

    handle.owner.close = close_owner
    handle.close()
    assert events.count("disconnect") == expected[port["name"]]
    assert events[-1] == "owner_closed"


def test_editor_prompt_when_closed_then_disconnects_before_alert_and_owner(batch_qt):
    handle = load(record("Qt Text Editor")).build(batch_qt)
    window = handle.widget
    window.centralWidget.modified = True
    window.closeEvent(SimpleNamespace(accept=lambda: None, ignore=lambda: None))
    assert len(handle.connections) == 6, (
        "Dynamic prompt connection must also be recorded"
    )
    alert = handle.alerts[-1]
    signal = alert.widget.buttonClicked
    events = []
    alert_close, owner_close = alert.close, handle.owner.close

    def close_alert():
        assert not signal.callbacks and not handle.connections
        assert not handle.callbacks and handle.inspect_ui is dict
        events.append("alert")
        alert_close()

    def close_owner():
        assert events == ["alert"]
        events.append("owner")
        owner_close()

    alert.close = close_alert
    handle.owner.close = close_owner
    handle.close()
    assert events == ["alert", "owner"]


@pytest.mark.parametrize(
    "name, native_cell",
    [("Qt Text Editor", "text")],
)
def test_subclass_when_closed_then_native_references_in_class_closures_are_cleared(
    name, native_cell, batch_qt
):
    handle = load(record(name)).build(batch_qt)
    method = type(handle.widget).closeEvent
    cells = dict(zip(method.__code__.co_freevars, method.__closure__))
    assert cells[native_cell].cell_contents is not None
    handle.close()
    assert cells[native_cell].cell_contents is None, (
        "Subclass methods must not retain deleted child wrappers"
    )
