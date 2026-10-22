# this_file: tests/test_issue122_E1.py
"""Exact Models behaviours, real metadata history, and owned PythonQt lifetimes.

Preserved sources are read only as data. Native acceptance belongs to integration.
"""

import ast
import importlib
import json
import os
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from historical_sources import recorded_sha256

ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = ROOT.parent / "fontlab-fontlabapp" / "src"
TITLES = (
    "Glyph Encoding Chart",
    "Glyph Mark Colours",
    "Glyph Review Form",
    "Glyph Coverage Grid",
    "Glyph Inventory XML",
    "Glyph Proof Worksheet",
    "Glyph Review Priorities",
)
READONLY = (TITLES[0], TITLES[3], TITLES[4])
WRITERS = TITLES[1:3]
ROWS = (
    ("A", "U+0041 U+FF21", "2026-01-02 03:04:05"),
    ("A.alt", "", ""),
    ("B", "U+0042", ""),
)
DISPOSITIONS = {
    "chart": ("ported", "Scripts/Models/Glyph Encoding Chart.py"),
    "coloreditorfactory": ("ported", "Scripts/Models/Glyph Mark Colours.py"),
    "simplewidgetmapper": ("ported", "Scripts/Models/Glyph Review Form.py"),
    "combowidgetmapper": ("duplicate-of", "Scripts/Models/Glyph Review Form.py"),
    "dirview": ("duplicate-of", "Scripts/Tools/Find Font Source Files.py"),
    "fetchmore": ("duplicate-of", "Scripts/Models/Glyph Sorting and Filtering.py"),
    "frozencolumn": ("duplicate-of", "Scripts/Models/Glyph Sorting and Filtering.py"),
    "interview": ("duplicate-of", "Scripts/Models/Glyph Sorting and Filtering.py"),
    "pixelator": ("ported", "Scripts/Models/Glyph Coverage Grid.py"),
    "puzzle": ("duplicate-of", "Scripts/Drag And Drop/Glyph Pair Board.py"),
    "simpledommodel": ("ported", "Scripts/Models/Glyph Inventory XML.py"),
    "spreadsheet": ("ported", "Scripts/Models/Glyph Proof Worksheet.py"),
    "stardelegate": ("ported", "Scripts/Models/Glyph Review Priorities.py"),
    "storageview": ("retired", "no FontLab action; OS disk utilities cover it"),
}


def load(title: str) -> dict[str, Any]:
    """Execute only the new menu, without its main entrypoint."""
    return runpy.run_path(str(ROOT / "Scripts" / "Models" / f"{title}.py"))


@pytest.fixture
def app(monkeypatch: Any) -> Any:
    """Use real public App modules; aliases contain the real imported objects."""
    monkeypatch.syspath_prepend(str(APP_SOURCE))
    modules = {}
    for name in (
        "glyph_catalog",
        "qt_properties",
        "draft_signals",
        "table_filter",
        "history",
        "names_edit",
        "edit_guards",
    ):
        modules[name] = importlib.import_module("fontlabapp." + name)
        assert (
            Path(modules[name].__file__).resolve().is_relative_to(APP_SOURCE.resolve())
        )
    return SimpleNamespace(**modules)


def test_real_app_dependencies_exist(app: Any) -> None:
    assert callable(app.glyph_catalog.capture)
    assert callable(app.qt_properties.value)
    assert callable(app.draft_signals.Scope)
    assert app.table_filter.Table(("Name", "Unicode", "Modified"), ROWS).rows == ROWS
    for name in ("commit", "AutoFacts", "PartialWriteError"):
        assert callable(getattr(app.history, name))
    for name in ("scan", "fresh_facts"):
        assert callable(getattr(app.names_edit, name))


@pytest.mark.parametrize(
    "title,field,old,new",
    [
        ("Glyph Mark Colours", "mark", 0, 121),
        ("Glyph Review Form", "note", "Original", "Review: spacing"),
    ],
)
@pytest.mark.parametrize("auto", [False, True])
def test_metadata_write_one_undo_changed_rows_only_and_auto_refusal(
    title: str,
    field: str,
    old: Any,
    new: Any,
    auto: bool,
    app: Any,
    host: Any,
    monkeypatch: Any,
) -> None:
    events = []
    glyph = SimpleNamespace(
        name="A",
        layers=[],
        lastModified=None,
        checkInitHistoryState=lambda mode: events.append(("init", mode)),
    )
    setattr(glyph, field, old)
    layer = SimpleNamespace(
        name="Regular",
        autoLayer=auto,
        checkInitHistoryState=lambda mode: events.append(("layer", mode)),
    )
    glyph.layers = [layer]
    other = SimpleNamespace(name="B", mark=31, note="Untouched")
    facts = app.names_edit.Facts(
        None,
        17,
        {
            "A": app.names_edit.Entry("A", SimpleNamespace(id=1), glyph),
            "B": app.names_edit.Entry("B", SimpleNamespace(id=2), other),
        },
        app.history.AutoFacts(frozenset({"A"} if auto else ()), {}),
    )
    monkeypatch.setattr(app.names_edit, "fresh_facts", lambda package_id: facts)
    native = SimpleNamespace(
        flGlyph=SimpleNamespace(updatedFgGlyphs=lambda: ()),
        flItems=lambda: SimpleNamespace(
            notifyChangesApplied=lambda label, items: events.append(("notify", items))
        ),
    )
    monkeypatch.setattr(
        app.history,
        "_native",
        lambda name: (
            native
            if name == "fontlab"
            else SimpleNamespace(
                QtCore=SimpleNamespace(
                    QDateTime=SimpleNamespace(currentDateTimeUtc=lambda: 123)
                )
            )
        ),
    )
    for name in ("history", "names_edit", "edit_guards"):
        monkeypatch.setitem(sys.modules, "fly.ap." + name, getattr(app, name))
        setattr(sys.modules["fly.ap"], name, getattr(app, name))
    apply = load(title)["apply_changes"]
    baseline = {"A": (1, old)}
    if auto:
        with pytest.raises(ValueError, match="auto layer"):
            apply(17, baseline, {"A": new})
        assert events == [] and getattr(glyph, field) == old
    else:
        assert apply(17, baseline, {"A": new}) == ("A",)
        assert getattr(glyph, field) == new
        assert [event for event in events if event[0] == "notify"] == [
            ("notify", [layer, glyph])
        ]
        assert other.mark == 31 and other.note == "Untouched"
        before = list(events)
        assert apply(17, {"A": (1, new)}, {"A": new}) == ()
        assert events == before


class Signal:
    """Exact callbacks with explicit failed-disconnect controls."""

    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.fail = False

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        if self.fail:
            raise RuntimeError("disconnect refused")
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in self.slots[:]:
            slot(*args)


class Widget:
    """Known widget APIs only; reject native member shadowing on subclasses."""

    forbidden = frozenset(
        {
            "layout",
            "data",
            "model",
            "size",
            "children",
            "windowTitle",
            "selectionModel",
            "parent",
            "statusTip",
            "geometry",
            "close",
            "actions",
            "render",
            "update",
            "font",
            "move",
            "statusBar",
        }
    )

    def __init__(self, *args: Any) -> None:
        object.__setattr__(self, "_ready", False)
        self.nodes: list[Any] = []
        for arg in args:
            if isinstance(arg, Widget):
                arg.nodes.append(self)
        self.text_value = args[0] if args and isinstance(args[0], str) else ""
        self.number = 1
        self.clicked = Signal()
        self.valueChanged = Signal()
        self.destroyed = Signal()
        self.currentIndexChanged = Signal()
        self.textChanged = Signal()
        self.entries = []
        self.combo_index = -1
        self.visible = self.deleted = False
        self.table_model = None
        self.bar = SimpleNamespace(valueChanged=Signal(), setValue=lambda value: None)
        self.selection = SimpleNamespace(deleteLater=lambda: None)
        object.__setattr__(self, "_ready", True)

    def __setattr__(self, name: str, value: Any) -> None:
        if getattr(self, "_ready", False) and name in self.forbidden:
            raise AttributeError(f"Native member {name}")
        object.__setattr__(self, name, value)

    def setWindowTitle(self, text: str) -> None:
        self.title = text

    def setAttribute(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def setSpacing(self, *args: Any) -> None:
        pass

    def addWidget(self, *args: Any) -> None:
        pass

    def addLayout(self, *args: Any) -> None:
        pass

    def setText(self, text: str) -> None:
        self.text_value = text
        self.textChanged.emit(text)

    def text(self) -> str:
        return self.text_value

    def setPlainText(self, text: str) -> None:
        self.text_value = text
        self.textChanged.emit()

    def toPlainText(self) -> str:
        return self.text_value

    def setReadOnly(self, value: bool) -> None:
        self.read_only = value

    def setEnabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def setTextFormat(self, value: int) -> None:
        pass

    def setWordWrap(self, value: bool) -> None:
        pass

    def setPlaceholderText(self, text: str) -> None:
        pass

    def setRange(self, low: int, high: int) -> None:
        self.limits = (low, high)
        self.number = min(max(self.number, low), high)

    def setValue(self, number: int) -> None:
        self.number = number
        self.valueChanged.emit(number)

    def value(self) -> int:
        return self.number

    def setModel(self, model: Any) -> None:
        self.table_model = model

    def model(self) -> Any:
        return self.table_model

    def setSelectionModel(self, selection: Any) -> None:
        self.selection = selection

    def selectionModel(self) -> Any:
        return self.selection

    def setColumnHidden(self, *args: Any) -> None:
        pass

    def setFixedWidth(self, width: int) -> None:
        pass

    def verticalScrollBar(self) -> Any:
        return self.bar

    def show(self) -> None:
        self.visible = True

    def deleteLater(self) -> None:
        self.deleted = True

    def close(self) -> None:
        self.closeEvent(SimpleNamespace(accept=lambda: None, ignore=lambda: None))


class Combo(Widget):
    def addItem(self, label: str, data: Any = None) -> None:
        self.entries.append((label, data))
        if self.combo_index == -1:
            self.setCurrentIndex(0)

    def addItems(self, labels: list[str]) -> None:
        for label in labels:
            self.addItem(label)

    def findData(self, data: Any) -> int:
        return next(
            (i for i, (_label, value) in enumerate(self.entries) if value == data), -1
        )

    def setCurrentIndex(self, index: int) -> None:
        if index != self.combo_index:
            self.combo_index = index
            self.currentIndexChanged.emit(index)

    def currentIndex(self) -> int:
        return self.combo_index

    def currentText(self) -> str:
        return self.entries[self.combo_index][0] if self.combo_index >= 0 else ""

    def setCurrentText(self, text: str) -> None:
        self.setCurrentIndex(
            next(i for i, (label, _data) in enumerate(self.entries) if label == text)
        )

    def itemData(self, index: int) -> Any:
        return self.entries[index][1]


class Model(Widget):
    made = 0

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        Model.made += 1
        self.rows = []

    def setHorizontalHeaderLabels(self, headers: list[str]) -> None:
        self.headers = tuple(headers)

    def appendRow(self, items: list[Any]) -> None:
        self.rows.append(items)

    def item(self, row: int, column: int) -> Any:
        return self.rows[row][column]


class Item:
    def __init__(self, text: str) -> None:
        self.text = text
        self.editable = True
        self.updates = 0

    def setEditable(self, editable: bool) -> None:
        self.editable = editable

    def setText(self, text: str) -> None:
        self.text = text
        self.updates += 1


class View(Widget):
    def setItemDelegateForColumn(self, column: int, delegate: Any) -> None:
        self.cell_delegate = delegate
        self.delegate_column = column

    def setItemDelegate(self, delegate: Any) -> None:
        self.cell_delegate = delegate

    def setEditTriggers(self, trigger: Any) -> None:
        self.edit_triggers = trigger


class Delegate(Widget):
    def destroyEditor(self, editor: Any, index: Any) -> None:
        editor.deleteLater()


class Mapper(Widget):
    ManualSubmit = 1

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.mappings = []
        self.mapper_row = 0

    def setSubmitPolicy(self, policy: int) -> None:
        assert policy == self.ManualSubmit

    def addMapping(self, widget: Any, column: int, prop: bytes = b"text") -> None:
        self.mappings.append((widget, column, prop))

    def setCurrentIndex(self, index: int) -> None:
        self.mapper_row = index
        if index >= 0 and self.table_model and self.table_model.rows:
            for widget, column, prop in self.mappings:
                text = self.table_model.item(index, column).text
                if prop == b"currentText":
                    widget.setCurrentText(text)
                elif prop == b"plainText":
                    widget.setPlainText(text)
                else:
                    widget.setText(text)

    def toFirst(self) -> None:
        self.setCurrentIndex(0)

    def revert(self) -> None:
        self.setCurrentIndex(self.mapper_row)

    def submit(self) -> bool:
        for widget, column, prop in self.mappings:
            text = (
                widget.currentText()
                if prop == b"currentText"
                else widget.toPlainText()
                if prop == b"plainText"
                else widget.text()
            )
            self.table_model.item(self.mapper_row, column).setText(text)
        return True


@pytest.fixture
def host(app: Any, monkeypatch: Any) -> Any:
    for name in ("fly", "fly.ap"):
        module = ModuleType(name)
        module.__path__ = []
        monkeypatch.setitem(sys.modules, name, module)
    sys.modules["fly"].ap = sys.modules["fly.ap"]
    for name in (
        "draft_signals",
        "qt_properties",
        "glyph_catalog",
        "history",
        "names_edit",
        "edit_guards",
    ):
        module = getattr(app, name)
        monkeypatch.setitem(sys.modules, "fly.ap." + name, module)
        setattr(sys.modules["fly.ap"], name, module)
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QVBoxLayout",
                "QHBoxLayout",
                "QLabel",
                "QPushButton",
                "QLineEdit",
                "QPlainTextEdit",
                "QSpinBox",
            )
        }
    )
    gui.QTableView = View
    gui.QStandardItemModel, gui.QStandardItem = Model, Item
    gui.QComboBox, gui.QDataWidgetMapper, gui.QStyledItemDelegate = (
        Combo,
        Mapper,
        Delegate,
    )
    gui.QAbstractItemView = SimpleNamespace(NoEditTriggers=0)
    clipboard = SimpleNamespace(text="")
    clipboard.setText = lambda text: setattr(clipboard, "text", text)
    gui.QApplication = SimpleNamespace(clipboard=lambda: clipboard)
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(
            QByteArray=bytes,
            Qt=SimpleNamespace(Tool=1, WindowFlags=int, WA_QuitOnClose=2, PlainText=0),
        ),
    )
    return SimpleNamespace(
        qt=qt,
        clipboard=clipboard,
        capture=lambda: app.table_filter.Table(
            ("Glyph name", "Unicode", "Modified"), ROWS
        ),
    )


def open_panel(title: str, host: Any) -> tuple[dict[str, Any], Any]:
    module = load(title)
    capture = host.capture
    if title in WRITERS:
        value = 0 if title == TITLES[1] else "Existing\nmultiline note"
        def capture():
            return (
                17,
                {row[0]: (index + 1, value) for index, row in enumerate(ROWS)},
            )
    return module, module["show"](host.qt, None, capture)


def close_panel(panel: Any) -> None:
    if hasattr(panel, "discard_changes"):
        panel.discard_changes()
    panel.dirty = False
    panel.close()


def click(panel: Any, title: str) -> None:
    next(node for node in panel.nodes if node.text_value == title).clicked.emit(False)


def test_all_28_source_identities_and_rulings() -> None:
    rows = [
        row
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
        if "itemviews/" in row["target"]
        and Path(row["target"]).name.split("-")[0] in DISPOSITIONS
    ]
    assert len(rows) == 28
    for row in rows:
        family = Path(row["target"]).name.split("-")[0]
        disposition, destination = DISPOSITIONS[family]
        assert (
            recorded_sha256(row['target'])
            == row["target_sha256"]
        )
        if disposition != "retired":
            assert (ROOT / destination).is_file()
        if disposition == "ported" or family == "combowidgetmapper":
            text = (ROOT / destination).read_text()
            assert row["target"] in text and row["target_sha256"] in text
    for name in (
        "Glyph Colour Draft",
        "Font Export Storage",
        "Paged Glyph Catalogue",
        "Pinned Glyph Catalogue",
        "Linked Glyph Views",
    ):
        assert not (ROOT / "Scripts/Models" / f"{name}.py").exists()


def test_readonly_exact_results_and_no_draft_data() -> None:
    chart = load(TITLES[0])
    assert chart["build_rows"](ROWS) == (
        ("Encoded", "2", "66.67%", "█████████████", ""),
        ("Unencoded", "1", "33.33%", "███████", ""),
        ("Unencoded glyph", "", "", "", "A.alt"),
    )
    assert chart["build_rows"](())[0][1:3] == ("0", "0.00%")
    for title in READONLY:
        module = load(title)
        assert "drafts" not in module["report"](ROWS)
    grid = load(TITLES[3])["build_rows"](ROWS + (("A.dup", "U+0041 U+1F600", ""),))
    assert grid[0][2] == "A / A.dup" and grid[-1][1] == "A.dup"
    from xml.etree import ElementTree

    root = ElementTree.fromstring(
        load(TITLES[4])["report"]((("A&B<", "U+0041 U+FF21", ""),))
    )
    assert root[0].attrib["name"] == "A&B<"
    assert [x.text for x in root[0]] == ["U+0041", "U+FF21"]


@pytest.mark.parametrize("title", TITLES)
def test_lifetime_disconnect_retry_and_setup_cleanup(title: str, host: Any) -> None:
    module, panel = open_panel(title, host)
    assert panel.visible and panel.owned_model
    record = panel.scope.records[-1]
    record[0].fail = True
    panel.close()
    assert not panel.deleted
    record[0].fail = False
    panel.close()
    assert panel.deleted and not panel.scope.records and not module["_PANELS"]

    class FailedView(View):
        def __init__(self, *args: Any) -> None:
            raise RuntimeError("view setup failed")

    host.qt.QtGui.QTableView = FailedView
    with pytest.raises(RuntimeError, match="view setup failed"):
        module["show"](host.qt, None, host.capture)
    assert not module["_PANELS"]


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "error",
    [ValueError("Open a font"), RuntimeError("font changed"), TimeoutError("deadline")],
)
def test_capture_error_preserves_previous_model(
    title: str, error: Exception, host: Any
) -> None:
    _module, panel = open_panel(title, host)
    previous, rows = panel.owned_model, panel.snapshot

    def fail() -> Any:
        raise error

    panel.capture_font = fail
    click(panel, "Refresh")
    assert panel.owned_model is previous and panel.snapshot == rows
    assert str(error) in panel.status_line.text()
    close_panel(panel)


@pytest.mark.parametrize("title", READONLY + (TITLES[5], TITLES[6]))
def test_reports_export_exclusively(title: str, host: Any, tmp_path: Path) -> None:
    _module, panel = open_panel(title, host)
    click(panel, "Copy Report")
    panel.export_field.setText(str(tmp_path / "report"))
    click(panel, "Export New")
    assert (tmp_path / "report").read_text() == host.clipboard.text
    click(panel, "Export New")
    assert "exists" in panel.status_line.text()
    close_panel(panel)


@pytest.mark.parametrize("title", TITLES)
def test_parent_destruction_fences_callbacks(title: str, host: Any) -> None:
    module, panel = open_panel(title, host)
    callbacks = [slot for _signal, slot, _retry in panel.scope.records]
    panel.destroyed.emit(panel)
    for callback in callbacks:
        callback(False)
    assert panel.scope.dead and not module["_PANELS"]


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize("text", ["a\0b", "a\rb", "a\u00a0b", "a\u2028b", "a\u2029b"])
def test_unsafe_text_refused(title: str, text: str) -> None:
    with pytest.raises(ValueError):
        load(title)["checked"](text)


@pytest.mark.parametrize("title", TITLES)
def test_real_no_font_refusal_in_main(
    title: str, host: Any, app: Any, monkeypatch: Any
) -> None:
    native = SimpleNamespace(
        flWorkspace=SimpleNamespace(
            instance=lambda: SimpleNamespace(currentPackage=None)
        ),
        CurrentFont=lambda: None,
    )
    monkeypatch.setattr(app.names_edit, "_native", lambda name: native)
    module_native = importlib.import_module("fontlabapp._glyph_catalog_native")
    monkeypatch.setattr(module_native, "_native", lambda name: native)
    sys.modules["fly"].fl = SimpleNamespace(MainWindow=lambda: None)
    sys.modules["fly"].qt = host.qt
    module = load(title)
    module["main"]()
    panel = module["_PANELS"][-1]
    assert panel.visible and "Open a font" in panel.status_line.text()
    close_panel(panel)


@pytest.mark.parametrize("title", TITLES)
def test_public_source_contract(title: str) -> None:
    text = (ROOT / "Scripts/Models" / f"{title}.py").read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    doc = ast.get_docstring(tree)
    assert all(
        part + ":" in doc
        for part in ("What", "How", "Why", "Usage", "Benefit", "Requires")
    )
    assert not any(
        word in doc
        for word in (
            "unverified",
            "acceptance pending",
            "issue 122",
            "unresolved",
            "preserved archive",
            "Archived first-party",
        )
    )
    assert "Independent rewrite of the Qt " in doc
    assert "Based on the author's own FontLab sample, Apache-2.0." in " ".join(
        doc.split()
    )
    assert f"this_file: Scripts/Models/{title}.py" in text
    assert not any(
        word in text
        for word in (
            "QtWidgets",
            "QApplication(",
            "fly.ap._",
            "VIEW =",
            "STORAGE =",
            "EDITABLE =",
            "count: int",
        )
    )
    if title in READONLY:
        assert not any(
            word in text
            for word in (
                "Discard",
                "Reload Snapshot",
                "Reset Draft",
                "self.drafts",
                '"drafts"',
            )
        )
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, node.name
            assert all(
                arg.arg == "self" or arg.annotation is not None
                for arg in node.args.args
            ), node.name


@pytest.mark.parametrize("title", WRITERS)
def test_delegates_mapper_and_incremental_edits(
    title: str, host: Any, monkeypatch: Any
) -> None:
    module, panel = open_panel(title, host)
    model = panel.owned_model
    made = Model.made
    if title == TITLES[2]:
        assert len(panel.mapper.mappings) == 2
        assert panel.note_field.toPlainText() == "Existing\nmultiline note"
        panel.state_choice.setCurrentText("Review")
        panel.note_field.setPlainText("Check\nspacing")
        applied = []
        monkeypatch.setitem(
            module["show"].__globals__,
            "apply_changes",
            lambda pid, baseline, desired, **kwargs: (
                applied.append((pid, dict(desired))) or tuple(desired)
            ),
        )
        click(panel, "Apply")
        assert applied == [(17, {"A": "Review: Check\nspacing"})]
        assert (
            model.item(0, 1).text == "Review"
            and model.item(0, 2).text == "Check\nspacing"
        )
        assert not panel.dirty
    else:
        delegate = panel.editor_delegate
        index = SimpleNamespace(row=lambda: 0)
        editor = delegate.createEditor(panel, None, index)
        delegate.setEditorData(editor, index)
        desired = 121 if title == TITLES[1] else 5
        editor.setCurrentIndex(editor.findData(desired))
        delegate.setModelData(editor, model, index)
        assert panel.dirty and panel.cell_value(0) == desired
        if title == TITLES[1]:
            assert model.item(0, 1).text == "Green"
            applied = []
            monkeypatch.setitem(
                module["show"].__globals__,
                "apply_changes",
                lambda pid, baseline, changed, **kwargs: (
                    applied.append(dict(changed)) or tuple(changed)
                ),
            )
            click(panel, "Apply")
            assert applied == [{"A": 121}] and not panel.dirty
        else:
            assert model.item(0, 1).text == "★★★★★"
        delegate.destroyEditor(editor, index)
        assert editor.deleted
    assert panel.owned_model is model and Model.made == made
    assert all(item.updates == 0 for item in model.rows[1])
    close_panel(panel)


def test_worksheet_updates_only_edited_row(host: Any) -> None:
    module, panel = open_panel(TITLES[5], host)
    model = panel.owned_model
    made = Model.made
    panel.draft_field.setText("3")
    click(panel, "Apply Draft")
    assert panel.owned_model is model and Model.made == made
    assert model.item(0, 2).text == "/A/A/A"
    assert all(item.updates == 0 for item in model.rows[1])
    assert module["report"](ROWS[:1], {"A": "2"}) == "/A/A"
    click(panel, "Discard and Close")


def test_priority_export_import_round_trip_normalizes_bom_and_crlf(
    host: Any, tmp_path: Path
) -> None:
    _module, panel = open_panel(TITLES[6], host)
    panel.change_cell(0, 5)
    path = tmp_path / "queue.json"
    panel.export_field.setText(str(path))
    click(panel, "Export New")
    content = path.read_text()
    panel.discard_changes()
    path.write_bytes(b"\xef\xbb\xbf" + content.replace("\n", "\r\n").encode())
    model = panel.owned_model
    panel.source_field.setText(str(path))
    click(panel, "Import")
    assert panel.drafts == {"A": "5"} and panel.owned_model is model
    assert model.item(0, 1).text == "★★★★★"
    assert (
        "BOM removed" in panel.status_line.text()
        and "Line endings converted" in panel.status_line.text()
    )
    close_panel(panel)


@pytest.mark.parametrize(
    "bad", ["unknown", "stars", "nul", "nbsp", "ls", "ps", "duplicate", "mismatch"]
)
def test_priority_import_refuses_bad_queue_without_state_change(
    bad: str, host: Any, tmp_path: Path
) -> None:
    module, panel = open_panel(TITLES[6], host)
    payload = json.loads(module["report"](ROWS, {}))
    if bad == "unknown":
        payload["rows"][0][0] = "Missing"
    elif bad == "stars":
        payload["rows"][0][2] = "6"
    elif bad == "duplicate":
        payload["rows"].append(payload["rows"][0])
    elif bad == "mismatch":
        payload["drafts"] = {"A": "5"}
    else:
        payload["rows"][0][0] += {
            "nul": "\0",
            "nbsp": "\u00a0",
            "ls": "\u2028",
            "ps": "\u2029",
        }[bad]
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(payload))
    panel.source_field.setText(str(path))
    previous = panel.owned_model
    click(panel, "Import")
    assert panel.drafts == {} and panel.owned_model is previous and not panel.dirty
    assert "Queue imported" not in panel.status_line.text()
    close_panel(panel)


@pytest.mark.parametrize("title", WRITERS)
def test_metadata_stale_or_changed_font_refuses_before_history(
    title: str, app: Any, host: Any, monkeypatch: Any
) -> None:
    module = load(title)

    def switched(package_id: int) -> Any:
        raise ValueError("font switched")

    monkeypatch.setattr(app.names_edit, "fresh_facts", switched)
    with pytest.raises(ValueError, match="font switched"):
        module["apply_changes"](17, {}, {})


def test_native_capture_preserves_multiline_notes_and_actual_marks(
    app: Any, host: Any, monkeypatch: Any
) -> None:
    facts = SimpleNamespace(
        package_id=17,
        entries={
            "A": SimpleNamespace(
                record=SimpleNamespace(id=12),
                glyph=SimpleNamespace(mark=121, note="Original\nnote"),
            )
        },
    )
    monkeypatch.setattr(app.names_edit, "scan", lambda: facts)
    assert load(TITLES[1])["capture_metadata"]() == (17, {"A": (12, 121)})
    assert load(TITLES[2])["capture_metadata"]() == (17, {"A": (12, "Original\nnote")})


@pytest.fixture
def native_font(app: Any, host: Any, monkeypatch: Any) -> Any:
    """Run the actual shared history with fake native objects and notifications."""
    events = []

    class Glyph:
        def __init__(self, name: str, identity: int) -> None:
            self.name, self.identity = name, identity
            self.mark, self.note = 0, "Original"
            self.lastModified = None
            self.layers = [
                SimpleNamespace(
                    name="Regular",
                    autoLayer=False,
                    checkInitHistoryState=lambda mode: events.append(("layer", name)),
                )
            ]
            self.fail_mode = ""

        def checkInitHistoryState(self, mode: int) -> None:
            events.append(("glyph", self.name))

        def __setattr__(self, name: str, value: Any) -> None:
            if name in ("mark", "note") and getattr(self, "fail_mode", "") == "write":
                raise RuntimeError("setter failed")
            if (
                name in ("mark", "note")
                and getattr(self, "fail_mode", "") == "readback"
            ):
                return
            object.__setattr__(self, name, value)

    glyphs = [Glyph("A", 1), Glyph("B", 2)]
    facts = app.names_edit.Facts(
        None,
        17,
        {
            glyph.name: app.names_edit.Entry(
                glyph.name, SimpleNamespace(id=glyph.identity), glyph
            )
            for glyph in glyphs
        },
        app.history.AutoFacts(frozenset(), {}),
    )
    native = SimpleNamespace(
        flGlyph=SimpleNamespace(updatedFgGlyphs=lambda: ()),
        flItems=lambda: SimpleNamespace(
            notifyChangesApplied=lambda label, items: events.append(
                ("notify", list(items))
            )
        ),
    )
    monkeypatch.setattr(
        app.history,
        "_native",
        lambda name: (
            native
            if name == "fontlab"
            else SimpleNamespace(
                QtCore=SimpleNamespace(
                    QDateTime=SimpleNamespace(currentDateTimeUtc=lambda: 123)
                )
            )
        ),
    )
    monkeypatch.setattr(app.names_edit, "fresh_facts", lambda package_id: facts)
    return SimpleNamespace(glyphs=glyphs, facts=facts, native=native, events=events)


@pytest.mark.parametrize(
    "title,field,old,new",
    [(TITLES[1], "mark", 0, 121), (TITLES[2], "note", "Original", "Review: checked")],
)
def test_multiple_metadata_rows_share_one_notification(
    title: str, field: str, old: Any, new: Any, native_font: Any
) -> None:
    font = native_font
    baseline = {glyph.name: (glyph.identity, old) for glyph in font.glyphs}
    assert load(title)["apply_changes"](
        17, baseline, {glyph.name: new for glyph in font.glyphs}
    ) == ("A", "B")
    assert [event for event in font.events if event[0] == "notify"] == [
        ("notify", [glyph.layers[0] for glyph in font.glyphs] + font.glyphs)
    ]
    assert all(
        getattr(glyph, field) == new and glyph.lastModified == 123
        for glyph in font.glyphs
    )


@pytest.mark.parametrize(
    "title,old,new", [(TITLES[1], 0, 121), (TITLES[2], "Original", "Done: checked")]
)
@pytest.mark.parametrize("mode", ["write", "readback"])
def test_metadata_failure_keeps_one_undo_and_recovery_hint(
    title: str, old: Any, new: Any, mode: str, native_font: Any, app: Any
) -> None:
    native_font.glyphs[0].fail_mode = mode
    with pytest.raises(
        app.history.PartialWriteError,
        match="Native changes may remain; use Edit > Undo",
    ):
        load(title)["apply_changes"](17, {"A": (1, old)}, {"A": new})
    assert len([event for event in native_font.events if event[0] == "notify"]) == 1


@pytest.mark.parametrize(
    "title,field,old,new",
    [(TITLES[1], "mark", 0, 121), (TITLES[2], "note", "Original", "Review: checked")],
)
@pytest.mark.parametrize("cause", ["identity", "external", "missing", "queued"])
def test_metadata_stale_inputs_do_not_start_history(
    title: str, field: str, old: Any, new: Any, cause: str, native_font: Any
, capsys) -> None:
    font = native_font
    baseline = {"A": (1, old)}
    if cause == "identity":
        font.facts.entries["A"].record.id = 99
    elif cause == "external":
        setattr(font.glyphs[0], field, new)
    elif cause == "missing":
        font.facts.entries.pop("A")
    else:
        font.native.flGlyph.updatedFgGlyphs = lambda: (1,)
    if cause == "queued":
        assert load(title)["apply_changes"](17, baseline, {"A": new}) == ("A",)
        assert font.native.flGlyph.updatedFgGlyphs() == (1,) and font.events
        output = capsys.readouterr().out
        assert "(1,)" in output and "Queued glyph ids:" in output and "8537" in output and "modification dates" in output
        return
    with pytest.raises(ValueError):
        load(title)["apply_changes"](17, baseline, {"A": new})
    assert font.events == []


@pytest.mark.parametrize("title", WRITERS)
def test_native_apply_refusal_survives_in_panel_with_input(
    title: str, host: Any, monkeypatch: Any
) -> None:
    module, panel = open_panel(title, host)

    def refuse(package_id: int, baseline: dict, desired: dict, **kwargs: Any) -> Any:
        raise ValueError("Refused. A has auto layers.")

    monkeypatch.setitem(module["show"].__globals__, "apply_changes", refuse)
    if title == TITLES[1]:
        panel.change_cell(0, 121)
    else:
        panel.note_field.setPlainText("Keep this note")
    model = panel.owned_model
    click(panel, "Apply")
    assert panel.dirty and panel.owned_model is model
    assert "auto layers" in panel.status_line.text()
    panel.close()
    assert not panel.deleted
    close_panel(panel)


@pytest.mark.parametrize("title", (TITLES[1],))
def test_open_delegate_discard_cannot_restore_discarded_value(
    title: str, host: Any
) -> None:
    _module, panel = open_panel(title, host)
    delegate = panel.editor_delegate
    index = SimpleNamespace(row=lambda: 0)
    editor = delegate.createEditor(panel, None, index)
    delegate.setEditorData(editor, index)
    editor.setCurrentIndex(editor.findData(121 if title == TITLES[1] else 5))
    delegate.flush()
    assert panel.dirty
    panel.discard_changes()
    delegate.destroyEditor(editor, index)
    assert not panel.dirty and panel.cell_value(0) == 0
    panel.close()
    assert panel.deleted


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("bom", [False, True])
def test_priority_import_line_endings_and_bom(
    ending: str, bom: bool, tmp_path: Path
) -> None:
    module = load(TITLES[6])
    content = module["report"](ROWS, {"A": "5"})
    path = tmp_path / "queue.json"
    path.write_bytes(
        (b"\xef\xbb\xbf" if bom else b"") + content.replace("\n", ending).encode()
    )
    scores, notes = module["import_queue"](path, {"A", "A.alt", "B"})
    assert scores == {"A": "5"}
    assert ("BOM removed" in notes) == bom
    assert ("Line endings converted" in notes) == ("\r" in ending)


@pytest.mark.parametrize(
    "content",
    ["[]", "{}", "null", '{"columns":[],"columns":[]}', '{"columns": [true]}'],
)
def test_malformed_priority_json_is_refused(content: str, tmp_path: Path) -> None:
    path = tmp_path / "queue.json"
    path.write_text(content)
    with pytest.raises(ValueError):
        load(TITLES[6])["import_queue"](path, {"A"})


def test_mark_capture_keeps_unknown_values_and_grey_zero(
    app: Any, host: Any, monkeypatch: Any
) -> None:
    module = load(TITLES[1])
    facts = SimpleNamespace(
        package_id=17,
        entries={
            name: SimpleNamespace(
                record=SimpleNamespace(id=index), glyph=SimpleNamespace(mark=value)
            )
            for index, (name, value) in enumerate(
                (("Unknown", 999), ("Grey", 1000), ("Empty", None)), 1
            )
        },
    )
    monkeypatch.setattr(app.names_edit, "scan", lambda: facts)
    assert module["capture_metadata"]() == (
        17,
        {"Unknown": (1, 999), "Grey": (2, 1000), "Empty": (3, 0)},
    )
    assert module["valid_mark"](1000) == 1000


@pytest.mark.parametrize(
    "bad",
    [
        "bad\r\nnote",
        "bad\u00a0note",
        "bad\u2028note",
        "bad\u2029note",
        "bad\0note",
        "bad\ud800note",
    ],
)
def test_unsupported_note_is_readonly_beside_editable_note(
    bad: str, app: Any, host: Any, monkeypatch: Any
) -> None:
    module = load(TITLES[2])
    facts = SimpleNamespace(
        package_id=17,
        entries={
            "Bad": SimpleNamespace(
                record=SimpleNamespace(id=1), glyph=SimpleNamespace(note=bad)
            ),
            "Good": SimpleNamespace(
                record=SimpleNamespace(id=2), glyph=SimpleNamespace(note=None)
            ),
        },
    )
    monkeypatch.setattr(app.names_edit, "scan", lambda: facts)
    captured = module["capture_metadata"]()
    assert set(captured[1]) == {"Bad", "Good"}
    panel = module["show"](host.qt, None, lambda: captured)
    assert panel.snapshot[0][1] == "Read-only"
    assert "Bad" in panel.snapshot[0][2] and "unsupported" in panel.snapshot[0][2]
    assert panel.mapper.mapper_row == 1
    panel.row_number.setValue(1)
    click(panel, "Apply")
    assert (
        "Bad" in panel.status_line.text()
        and "read-only" in panel.status_line.text().lower()
    )
    assert panel.mapper.mapper_row != 0
    panel.row_number.setValue(2)
    assert panel.state_choice.currentText() == "Unset"
    close_panel(panel)


def test_unset_and_empty_review_notes_round_trip() -> None:
    module = load(TITLES[2])
    for state in ("Todo", "Review", "Done"):
        assert module["compose_note"](state, "") == state
        assert module["split_note"](state) == (state, "")
        assert module["split_note"](state + ":") == (state, "")
    assert module["split_note"]("free note") == ("Unset", "free note")
    assert module["compose_note"]("Unset", "") == ""
    assert module["compose_note"]("Unset", "free note") == "free note"


@pytest.mark.parametrize(
    "title,field,new", [(TITLES[1], "mark", 1000), (TITLES[2], "note", "Review")]
)
def test_none_native_fields_capture_and_apply_as_empty(
    title: str, field: str, new: Any, native_font: Any, app: Any, monkeypatch: Any
) -> None:
    font = native_font
    setattr(font.glyphs[0], field, None)
    monkeypatch.setattr(app.names_edit, "scan", lambda: font.facts)
    module = load(title)
    package_id, baseline = module["capture_metadata"]()
    assert baseline["A"][1] == (0 if field == "mark" else "")
    assert module["apply_changes"](package_id, baseline, {"A": new}) == ("A",)
    assert getattr(font.glyphs[0], field) == new
    assert [event[0] for event in font.events].count("notify") == 1


def test_apply_skips_unsafe_note_and_writes_good_neighbor(native_font: Any) -> None:
    font = native_font
    font.glyphs[0].note = "Keep\u00a0this"
    font.glyphs[1].note = None
    assert load(TITLES[2])["apply_changes"](
        17,
        {"A": (1, font.glyphs[0].note), "B": (2, "")},
        {"A": "Sanitized", "B": "Done"},
    ) == ("B",)
    assert font.glyphs[0].note == "Keep\u00a0this" and font.glyphs[1].note == "Done"
    assert [event for event in font.events if event[0] == "notify"] == [
        ("notify", [font.glyphs[1].layers[0], font.glyphs[1]])
    ]


def test_out_of_domain_mark_remains_visible_and_valid_neighbor_can_change(
    host: Any, native_font: Any
) -> None:
    module = load(TITLES[1])
    native_font.glyphs[0].mark = 999
    baseline = {"A": (1, 999), "B": (2, 0)}
    panel = module["show"](host.qt, None, lambda: (17, baseline))
    assert panel.owned_model.item(0, 1).text == "Mark 999"
    delegate = panel.editor_delegate
    index = SimpleNamespace(row=lambda: 0)
    editor = delegate.createEditor(panel, None, index)
    delegate.setEditorData(editor, index)
    delegate.flush()
    assert not panel.dirty, (
        "Reading an unchanged unusual mark must not count as a write"
    )
    panel.change_cell(1, 121)
    click(panel, "Apply")
    assert native_font.glyphs[0].mark == 999 and native_font.glyphs[1].mark == 121
    with pytest.raises(ValueError, match="A:"):
        module["apply_changes"](17, baseline, {"A": 999})
    close_panel(panel)


def test_mark_auto_layer_failure_reports_whole_apply_refusal(
    host: Any, native_font: Any, app: Any, monkeypatch: Any
) -> None:
    font = native_font
    facts = app.names_edit.Facts(
        None, 17, font.facts.entries, app.history.AutoFacts(frozenset({"B"}), {})
    )
    monkeypatch.setattr(app.names_edit, "fresh_facts", lambda package_id: facts)
    module = load(TITLES[1])
    panel = module["show"](host.qt, None, lambda: (17, {"A": (1, 0), "B": (2, 0)}))
    panel.change_cell(0, 121)
    panel.change_cell(1, 211)
    click(panel, "Apply")
    assert (
        "Whole Apply refused" in panel.status_line.text()
        and "B" in panel.status_line.text()
    )
    assert font.events == [] and panel.dirty
    close_panel(panel)


def assert_native_namespace_safe(cls: type) -> None:
    """Inspect declarations, including methods that an instance setter cannot catch."""
    assert not (set(vars(cls)) & Widget.forbidden), (
        f"Native member collision in {cls.__name__}"
    )


@pytest.mark.parametrize("title", TITLES)
def test_panel_and_delegate_class_names_do_not_shadow_native_members(
    title: str, host: Any
) -> None:
    module, panel = open_panel(title, host)
    assert_native_namespace_safe(type(panel))
    if "delegate_type" in module:
        assert_native_namespace_safe(module["delegate_type"](host.qt))
    for name in Widget.forbidden:
        with pytest.raises(AttributeError):
            setattr(panel, name, object())
    close_panel(panel)


def test_class_guard_detects_method_collisions() -> None:
    class Collision(Widget):
        def update(self) -> None:
            pass

    with pytest.raises(AssertionError, match="Native member collision"):
        assert_native_namespace_safe(Collision)


@pytest.mark.parametrize("kind", ["directory", "fifo", "oversize"])
def test_priority_import_refuses_nonregular_or_oversize_file(
    kind: str, tmp_path: Path, host: Any
) -> None:
    module, panel = open_panel(TITLES[6], host)
    path = tmp_path / "source"
    if kind == "directory":
        path.mkdir()
    elif kind == "fifo":
        os.mkfifo(path)
    else:
        with path.open("wb") as stream:
            stream.seek(module["MAX_QUEUE_BYTES"])
            stream.write(b" ")
    panel.source_field.setText(str(path))
    previous = panel.owned_model
    click(panel, "Import")
    assert panel.owned_model is previous and panel.drafts == {}
    assert (
        "regular file" if kind != "oversize" else "4 MiB"
    ) in panel.status_line.text()
    close_panel(panel)


def star_surface(host: Any) -> Any:
    """Model the documented Qt painter, option and mouse-event value objects."""
    gui, core = host.qt.QtGui, host.qt.QtCore
    gui.QStyle = SimpleNamespace(State_Selected=1)
    gui.QPalette = SimpleNamespace(Highlight=1, Base=2, HighlightedText=3, Text=4)
    core.Qt.AlignCenter, core.Qt.LeftButton = 4, 1
    core.Qt.Key_Delete, core.Qt.Key_Backspace = 127, 8
    core.QEvent = SimpleNamespace(MouseButtonRelease=1, KeyPress=2)
    core.QSize = lambda width, height: (width, height)
    option = SimpleNamespace(
        rect=SimpleNamespace(left=lambda: 10, width=lambda: 130),
        state=0,
        palette=SimpleNamespace(color=lambda role: role),
    )
    return option


def test_star_delegate_paints_sizes_clicks_and_clears_without_rebuilding(
    host: Any,
) -> None:
    option = star_surface(host)
    _module, panel = open_panel(TITLES[6], host)
    delegate = panel.editor_delegate
    index = SimpleNamespace(row=lambda: 0)
    assert delegate.sizeHint(option, index) == (130, 28)
    assert delegate.createEditor(panel, option, index) is None
    model, made = panel.owned_model, Model.made
    event = SimpleNamespace(
        type=lambda: 1, button=lambda: 1, pos=lambda: SimpleNamespace(x=lambda: 139)
    )
    assert delegate.editorEvent(event, model, option, index)
    assert panel.cell_value(0) == 5 and model.item(0, 2).text == "5"
    calls = []
    painter = SimpleNamespace(
        save=lambda: calls.append("save"),
        restore=lambda: calls.append("restore"),
        fillRect=lambda *args: None,
        setPen=lambda *args: None,
        drawText=lambda rect, align, text: calls.append(text),
    )
    delegate.paint(painter, option, index)
    assert calls == ["save", "★★★★★", "restore"]
    event = SimpleNamespace(type=lambda: 2, key=lambda: 127)
    assert delegate.editorEvent(event, model, option, index)
    delegate.paint(painter, option, index)
    assert calls[-3:] == ["save", "☆☆☆☆☆", "restore"]
    assert panel.owned_model is model and Model.made == made
    assert all(item.updates == 0 for item in model.rows[1])
    close_panel(panel)


def test_star_paint_failure_restores_borrowed_painter(host: Any) -> None:
    option = star_surface(host)
    _module, panel = open_panel(TITLES[6], host)
    calls = []

    def failed_draw(*args: Any) -> None:
        raise RuntimeError("paint failed")

    painter = SimpleNamespace(
        save=lambda: calls.append("save"),
        restore=lambda: calls.append("restore"),
        fillRect=lambda *args: None,
        setPen=lambda *args: None,
        drawText=failed_draw,
    )
    panel.editor_delegate.paint(painter, option, SimpleNamespace(row=lambda: 0))
    assert calls == ["save", "restore"] and "paint failed" in panel.status_line.text()
    close_panel(panel)
