# this_file: tests/test_issue122_E6.py
"""Test the real dock composition, safe selection boundary and baseline diffs.

Preserved sources are hashed, never imported. Widget doubles reject a fixed
native member list at class creation and attribute assignment.
"""

import ast
import importlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from historical_sources import recorded_sha256

ROOT = Path(__file__).resolve().parents[1]
APP_SOURCE = ROOT.parent / "fontlab-fontlabapp" / "src"
TITLES = ("Unicode Issues Dock", "Glyph Snapshot Diff")
NATIVE_NAMES = frozenset(
    [
        "render",
        "layout",
        "size",
        "update",
        "font",
        "move",
        "scroll",
        "menuBar",
        "centralWidget",
        "statusBar",
        "geometry",
        "minimumSize",
        "maximumSize",
        "windowTitle",
        "objectName",
        "style",
        "actions",
        "children",
        "parent",
        "window",
        "resize",
        "show",
        "hide",
        "close",
        "deleteLater",
        "setLayout",
        "contentsMargins",
        "sizeHint",
    ]
)
ROWS = (
    ("A", "U+0041 U+0391", "2026-01-01"),
    ("A.alt", "U+0041", ""),
    ("unencoded", "", ""),
    ("B", "U+0042", ""),
)


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts" / "Windows" / f"{title}.py"))


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.fail = False

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        if self.fail:
            raise RuntimeError("disconnect failure")
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


class Event:
    def __init__(self) -> None:
        self.accepted = False

    def type(self) -> int:
        return 19

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.accepted = False


class Widget:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        collisions = NATIVE_NAMES.intersection(cls.__dict__)
        if collisions:
            raise TypeError(f"native class members: {collisions}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in NATIVE_NAMES:
            raise TypeError(f"native instance member: {name}")
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self.owned_children: list[Any] = []
        for arg in args:
            if isinstance(arg, Widget):
                arg.owned_children.append(self)
        self.clicked, self.destroyed, self.doubleClicked, self.textChanged = (
            Signal(),
            Signal(),
            Signal(),
            Signal(),
        )
        self.local_text = args[0] if args and isinstance(args[0], str) else ""
        self.local_items: list[Any] = []
        self.local_filters: list[Any] = []
        self.deleted = False
        self.local_visible = True
        self.local_floating = False

    def setWindowTitle(self, text: str) -> None:
        self.local_title = text

    def setObjectName(self, text: str) -> None:
        self.local_object_name = text

    def setAttribute(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def setText(self, text: str) -> None:
        self.local_text = text
        self.textChanged.emit(text)

    def text(self) -> str:
        return self.local_text

    def setTextFormat(self, *args: Any) -> None:
        pass

    def setWordWrap(self, *args: Any) -> None:
        pass

    def setPlaceholderText(self, *args: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def setSpacing(self, *args: Any) -> None:
        pass

    def addWidget(self, widget: Any, *args: Any) -> None:
        self.local_items.append(widget)

    def addLayout(self, widget: Any, *args: Any) -> None:
        self.local_items.append(widget)

    def setWidget(self, widget: Any) -> None:
        self.local_widget = widget

    def addDockWidget(self, area: Any, dock: Any) -> None:
        self.local_dock, self.local_area = dock, area

    def removeDockWidget(self, dock: Any) -> None:
        assert dock is self.local_dock
        self.local_removed = dock

    def setFloating(self, state: bool) -> None:
        self.local_floating = state

    def isVisible(self) -> bool:
        return self.local_visible

    def setModel(self, model: Any) -> None:
        self.local_model = model

    def setSelectionBehavior(self, *args: Any) -> None:
        pass

    def setSelectionMode(self, *args: Any) -> None:
        pass

    def installEventFilter(self, filter_owner: Any) -> None:
        self.local_filters.append(filter_owner)

    def show(self) -> None:
        self.local_visible = True

    def hide(self) -> None:
        self.local_visible = False

    def deleteLater(self) -> None:
        self.deleted = True

    def close(self) -> None:
        event = Event()
        if any(owner.eventFilter(self, event) for owner in self.local_filters):
            return
        if hasattr(self, "closeEvent"):
            self.closeEvent(event)
        else:
            self.hide()


class Model(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.cells: dict[tuple[int, int], Any] = {}
        self.writes = 0
        self.local_row_count = 0

    def setHorizontalHeaderLabels(self, headers: list[str]) -> None:
        self.local_headers = headers

    def setRowCount(self, count: int) -> None:
        self.local_row_count = count
        self.cells = {key: item for key, item in self.cells.items() if key[0] < count}

    def setItem(self, row: int, column: int, item: Any) -> None:
        self.cells[row, column] = item
        self.writes += 1


class Item:
    def __init__(self, text: str) -> None:
        self.local_text = text

    def setEditable(self, state: bool) -> None:
        assert state is False


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    monkeypatch.syspath_prepend(str(APP_SOURCE))
    fly = ModuleType("fly")
    fly.__path__ = []
    ap = ModuleType("fly.ap")
    ap.__path__ = []
    fly.ap = ap
    monkeypatch.setitem(sys.modules, "fly", fly)
    monkeypatch.setitem(sys.modules, "fly.ap", ap)
    for name in (
        "widgets",
        "draft_signals",
        "qt_properties",
        "glyph_catalog",
        "scripting",
    ):
        module = importlib.import_module("fontlabapp." + name)
        monkeypatch.setitem(sys.modules, "fly.ap." + name, module)
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QLineEdit",
                "QPushButton",
                "QVBoxLayout",
                "QHBoxLayout",
                "QTableView",
                "QDockWidget",
            )
        }
    )
    gui.QStandardItemModel, gui.QStandardItem = Model, Item
    gui.QAbstractItemView = SimpleNamespace(SelectRows=1, SingleSelection=1)
    clipboard = Widget()
    gui.QApplication = SimpleNamespace(clipboard=lambda: clipboard)
    warnings: list[Any] = []
    gui.QMessageBox = SimpleNamespace(warning=lambda *args: warnings.append(args))
    enums = SimpleNamespace(
        Tool=1,
        WA_QuitOnClose=2,
        PlainText=3,
        LeftDockWidgetArea=4,
        RightDockWidgetArea=5,
        TopDockWidgetArea=6,
        BottomDockWidgetArea=7,
        WindowFlags=lambda x: x,
    )
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(Qt=enums, QEvent=SimpleNamespace(Close=19)),
    )
    widgets = sys.modules["fly.ap.widgets"]
    monkeypatch.setattr(widgets, "_native", lambda name: qt)
    package = SimpleNamespace(id=17)
    state = SimpleNamespace(
        rows=ROWS, epochs=None, package=package, failure=None, selections=[]
    )

    def capture() -> Any:
        if state.failure:
            raise state.failure
        return SimpleNamespace(rows=state.rows, epochs=state.epochs)

    def current_package(expected_id: int | None = None) -> Any:
        return (
            state.package
            if state.package is not None
            and (expected_id is None or state.package.id == expected_id)
            else None
        )

    def select_glyphs(names: list[str], *, package_id: int) -> list[str]:
        assert package_id == 17
        state.selections.append((names, package_id))
        return names

    scripting = sys.modules["fly.ap.scripting"]
    real_select = scripting.select_glyphs
    monkeypatch.setattr(scripting, "current_package", current_package)
    monkeypatch.setattr(scripting, "select_glyphs", select_glyphs)
    monkeypatch.setattr(sys.modules["fly.ap.glyph_catalog"], "capture", capture)
    parent = Widget()
    fly.qt, fly.fl = qt, SimpleNamespace(MainWindow=lambda: parent)
    return SimpleNamespace(
        qt=qt,
        parent=parent,
        clipboard=clipboard,
        capture=capture,
        state=state,
        warnings=warnings,
        real_select=real_select,
    )


def test_real_app_names_and_selection_guard_contract(host: Any) -> None:
    from fontlabapp import draft_signals, glyph_catalog, scripting, widgets

    assert callable(widgets.create_panel) and callable(widgets.OwnedWidget.close)
    assert callable(draft_signals.Scope) and callable(glyph_catalog.capture)
    assert callable(scripting.select_glyphs) and callable(scripting.current_package)
    source = (APP_SOURCE / "fontlabapp" / "scripting.py").read_text()
    selection = source[
        source.index("def select_glyphs(") : source.index(
            "def _require_selection_window("
        )
    ]
    assert (
        selection.index("_require_selection_window(package_id)")
        < selection.index("fl.Unselect()")
        < selection.index("fl.Select(index)")
    )


def test_issue_rows_exact_unicode_membership_and_invalid_values() -> None:
    module = load(TITLES[0])
    assert module["issue_rows"](ROWS) == (
        ("A", "Shared Unicode", "U+0041"),
        ("A.alt", "Shared Unicode", "U+0041"),
        ("unencoded", "Unencoded", ""),
    )
    assert module["issue_rows"](()) == ()
    assert module["issue_rows"]((("A", "U+0041 U+0041", ""),)) == ()
    for field in ("U+ZZZZ", "U+D800", "U+110000", "U++041"):
        with pytest.raises(ValueError):
            module["issue_rows"]((("A", field, ""),))
    for name in ("bad\u00a0name", "bad\u2028name", "bad\0name", "bad\ud800name"):
        with pytest.raises((ValueError, UnicodeError)):
            module["issue_rows"](((name, "", ""),))


@pytest.mark.parametrize("visible,area", [(True, "right"), (False, "left")])
def test_real_fontlab_dock_parent_area_and_mac_profile(
    host: Any, visible: bool, area: str
) -> None:
    module = load(TITLES[0])
    host.parent.local_visible = visible
    panel = module["show"](host.qt, host.parent, area=area)
    assert isinstance(panel.owned, sys.modules["fly.ap.widgets"].OwnedWidget)
    assert host.parent.local_dock is panel.owned.widget
    assert panel.owned.widget.local_floating is (not visible)
    assert host.parent.local_area == (5 if area == "right" else 4)
    assert panel.issue_snapshot == module["issue_rows"](ROWS)
    assert (
        "1 unencoded" in panel.count_line.text()
        and "2 shared" in panel.count_line.text()
    )
    assert panel.close_owned()
    assert host.parent.local_removed.deleted
    assert panel.owned.closed and panel not in module["_PANELS"]


def test_dock_filter_double_click_selection_and_stale_font_refusal(host: Any) -> None:
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)
    data_model = panel.data_model
    writes = data_model.writes
    panel.refresh_issues()
    assert panel.data_model is data_model and data_model.writes == writes
    panel.filter_field.setText("A.alt")
    assert panel.page_rows == (("A.alt", "Shared Unicode", "U+0041"),)
    panel.issue_view.doubleClicked.emit(
        SimpleNamespace(row=lambda: 0, isValid=lambda: True)
    )
    assert host.state.selections == [(["A.alt"], 17)]
    host.state.package = SimpleNamespace(id=18)
    panel.issue_view.doubleClicked.emit(
        SimpleNamespace(row=lambda: 0, isValid=lambda: True)
    )
    assert len(host.state.selections) == 1
    assert "font" in panel.status_line.text().lower()
    panel.close_owned()


def test_dock_safe_selection_refusal_and_queued_close_retry(
    host: Any, monkeypatch: Any
) -> None:
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)

    def refusal(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("Activate the Font window before selecting glyphs.")

    monkeypatch.setattr(sys.modules["fly.ap.scripting"], "select_glyphs", refusal)
    panel.issue_view.doubleClicked.emit(
        SimpleNamespace(row=lambda: 0, isValid=lambda: True)
    )
    assert "Activate the Font window" in panel.status_line.text()
    signal, queued, _ = panel.scope.records[1]
    signal.fail = True
    assert not panel.close_owned()
    assert panel in module["_PANELS"] and not panel.owned.closed
    signal.fail = False
    dock = panel.owned.widget
    dock.close()  # native dock X is routed through OwnedWidget.close
    assert dock.deleted and panel.owned.closed
    queued()


def test_dock_paging_keeps_all_issues_and_model(host: Any) -> None:
    host.state.rows = tuple((f"g{i}", "", "") for i in range(250))
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)
    assert len(panel.issue_snapshot) == 250 and len(panel.page_rows) == 100
    model = panel.data_model
    panel.change_page(2)
    assert len(panel.page_rows) == 50 and panel.page_rows[-1][0] == "g249"
    assert panel.data_model is model
    panel.filter_field.setText("g249")
    assert panel.page_number == 0 and len(panel.page_rows) == 1
    panel.close_owned()


def test_diff_exact_added_removed_reencoded_and_modified_including_epoch() -> None:
    module = load(TITLES[1])
    old = module["snapshot"](
        SimpleNamespace(
            rows=(
                ("gone", "", "old"),
                ("A", "U+0041 U+0391", "date"),
                ("B", "U+0042", "same"),
                ("C", "", "old"),
            ),
            epochs=(1, 2, 3, 4),
        )
    )
    new = module["snapshot"](
        SimpleNamespace(
            rows=(
                ("new", "U+004E", "new"),
                ("A", "U+0042", "date"),
                ("B", "U+0042", "same"),
                ("C", "", "new"),
            ),
            epochs=(5, 2, 30, 6),
        )
    )
    assert module["diff_rows"](old, new) == (
        ("Added", "new", "", "U+004E"),
        ("Removed", "gone", "(unencoded)", ""),
        ("Re-encoded", "A", "U+0041 U+0391", "U+0042"),
        ("Modified", "B", "same [3 ms]", "same [30 ms]"),
        ("Modified", "C", "old [4 ms]", "new [6 ms]"),
    )
    assert module["diff_rows"](old, old) == ()
    assert module["diff_rows"]({}, {}) == ()
    reordered = module["snapshot"](
        SimpleNamespace(rows=(("A", "U+0391 U+0041", "date"),), epochs=(2,))
    )
    assert module["diff_rows"]({"A": old["A"]}, reordered) == ()
    with pytest.raises(ValueError):
        module["snapshot"](
            SimpleNamespace(rows=(("A", "", ""), ("A", "", "")), epochs=None)
        )


def test_diff_baseline_is_first_capture_and_latest_replaces_previous(host: Any) -> None:
    module = load(TITLES[1])
    panel = module["show"](host.qt, host.parent)
    baseline = panel.baseline
    model = panel.data_model
    host.state.rows = (("new", "U+004E", ""),)
    panel.capture_latest()
    assert panel.baseline is baseline
    assert panel.change_rows[0] == ("Added", "new", "", "U+004E")
    assert len([row for row in panel.change_rows if row[0] == "Removed"]) == 4
    host.state.rows = ROWS
    panel.capture_latest()
    assert panel.change_rows == () and panel.data_model is model
    host.state.rows = (("new", "U+004E", ""),)
    panel.reset_baseline()
    assert panel.change_rows == () and set(panel.baseline) == {"new"}
    panel.close()


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "error",
    [
        ValueError("No font"),
        RuntimeError("wrong thread"),
        TimeoutError("capture deadline"),
    ],
)
def test_failed_capture_preserves_previous_and_missing_font_is_visible(
    title: str, error: Exception, host: Any
) -> None:
    module = load(title)
    panel = module["show"](host.qt, host.parent)
    previous = tuple(panel.page_rows)
    host.state.failure = error
    action = panel.refresh_issues if title == TITLES[0] else panel.capture_latest
    panel.perform(action)
    assert panel.page_rows == previous and str(error) in panel.status_line.text()
    panel.close_owned() if title == TITLES[0] else panel.close()
    missing = module["show"](host.qt, host.parent)
    assert str(error) in missing.status_line.text()
    missing.close_owned() if title == TITLES[0] else missing.close()


def test_diff_font_identity_refusal_and_explicit_reset(host: Any) -> None:
    module = load(TITLES[1])
    panel = module["show"](host.qt, host.parent)
    host.state.package = SimpleNamespace(id=18)
    with pytest.raises(ValueError, match="font"):
        panel.capture_latest()
    panel.reset_baseline()
    assert panel.package_id == 18
    panel.close()


@pytest.mark.parametrize("title", TITLES)
def test_parent_destroy_and_real_main_entrypoint(title: str, host: Any) -> None:
    namespace = runpy.run_path(
        str(ROOT / "Scripts" / "Windows" / f"{title}.py"), run_name="__main__"
    )
    panel = namespace["_PANELS"][0]
    emitter = panel.owned.content if title == TITLES[0] else panel
    slots = [slot for _, slot, _ in panel.scope.records]
    emitter.destroyed.emit()
    assert panel.scope.dead and panel not in namespace["_PANELS"]
    for slot in slots:
        slot()


@pytest.mark.parametrize("title", TITLES)
def test_native_name_guards_source_typing_and_provenance(title: str) -> None:
    path = ROOT / "Scripts" / "Windows" / f"{title}.py"
    text = path.read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    doc = ast.get_docstring(tree)
    assert f"this_file: Scripts/Windows/{title}.py" in text
    assert all(
        label in doc
        for label in (
            "What:",
            "How:",
            "Why:",
            "Usage:",
            "Benefit:",
            "Historical source:",
            "SHA256:",
        )
    )
    assert not any(
        term in doc
        for term in ("unverified", "unresolved", "GPL", "issue 122", "batch E6")
    )
    assert "the author's own FontLab sample, Apache-2.0" in doc
    assert not any(
        term in text
        for term in (
            "QApplication(",
            "notifyChangesApplied",
            "FL.fl.Select",
            "QSettings(",
            "menuBar(",
        )
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    assert child.name not in NATIVE_NAMES, child.name
        if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
            assert node.attr not in NATIVE_NAMES, node.attr
        if isinstance(node, ast.FunctionDef):
            assert node.returns is not None, node.name
            for arg in (*node.args.args, *node.args.kwonlyargs):
                assert arg.arg == "self" or arg.annotation is not None, node.name
    index = {
        row["target"]: row
        for row in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    lines = doc.splitlines()
    sources = []
    for offset, line in enumerate(lines):
        if line.startswith("Historical source: "):
            source = line.removeprefix("Historical source: ")
            digest = lines[offset + 1].removeprefix("SHA256: ")
            assert digest == index[source]["target_sha256"]
            assert recorded_sha256(source) == digest
            sources.append(source)
    assert len(sources) == (10 if title == TITLES[0] else 2)


def test_fake_guard_rejects_class_and_instance_native_members() -> None:
    with pytest.raises(TypeError):
        type("BadPanel", (Widget,), {"render": lambda self: None})
    with pytest.raises(TypeError):
        Widget().layout = "bad"


def test_real_selection_helper_rejects_glyph_window_before_legacy_writes(
    host: Any, monkeypatch: Any
) -> None:
    scripting = sys.modules["fly.ap.scripting"]
    writes: list[Any] = []

    class Legacy:
        font = (SimpleNamespace(name="A"),)

        def Unselect(self) -> None:
            writes.append("unselect")

        def Select(self, index: int) -> None:
            writes.append(index)

        def Selected(self, index: int) -> bool:
            return index in writes

    wrong_panel = SimpleNamespace(inherits=lambda name: name == "GlyphWindow")
    workspace = SimpleNamespace(activeFontPanel=wrong_panel)
    native = SimpleNamespace(
        flWorkspace=SimpleNamespace(instance=lambda: workspace),
        UpdateAll=lambda: writes.append("update"),
    )
    monkeypatch.setattr(
        scripting,
        "_native",
        lambda name: native if name == "fontlab" else SimpleNamespace(fl=Legacy()),
    )
    with pytest.raises(ValueError, match="Activate the Font window"):
        host.real_select(["A"], package_id=17)
    assert writes == []
    frame = SimpleNamespace(inherits=lambda name: name == "YFrameWindow")
    workspace.activeFontPanel = SimpleNamespace(
        inherits=lambda name: name == "FontWindow", parentWidget=lambda: frame
    )
    assert host.real_select(["A"], package_id=17) == ["A"]
    assert writes == ["unselect", 0, "update"]


@pytest.mark.parametrize("title", TITLES)
def test_no_package_is_a_readable_refusal(title: str, host: Any) -> None:
    host.state.package = None
    module = load(title)
    panel = module["show"](host.qt, host.parent)
    assert "font" in panel.status_line.text().lower()
    assert panel.page_rows == ()
    if title == TITLES[0]:
        panel.close_owned()
    else:
        with pytest.raises(ValueError):
            panel.copy_diff()
        panel.close()


def test_diff_full_copy_beyond_page_and_both_changes_for_one_glyph(host: Any) -> None:
    module = load(TITLES[1])
    panel = module["show"](host.qt, host.parent)
    host.state.rows = tuple((f"new{i}", "", "") for i in range(250))
    panel.capture_latest()
    assert len(panel.change_rows) == 254 and len(panel.page_rows) == 100
    panel.change_page(2)
    assert len(panel.page_rows) == 54
    panel.copy_diff()
    assert len(host.clipboard.text().splitlines()) == 255
    panel.close()
    old = {"A": ((65,), "old", 1)}
    new = {"A": ((66,), "new", 2)}
    assert [row[0] for row in module["diff_rows"](old, new)] == [
        "Re-encoded",
        "Modified",
    ]


def test_diff_disconnect_failure_keeps_close_retry_and_fences_queued_work(
    host: Any,
) -> None:
    module = load(TITLES[1])
    panel = module["show"](host.qt, host.parent)
    signal, queued, _ = panel.scope.records[1]
    signal.fail = True
    event = Event()
    panel.closeEvent(event)
    assert not event.accepted and not panel.deleted
    queued()
    signal.fail = False
    panel.closeEvent(event)
    assert event.accepted and panel.deleted and panel.scope.dead


@pytest.mark.parametrize("title", TITLES)
def test_capture_font_switch_during_read_is_rejected(title: str, host: Any) -> None:
    module = load(title)

    def moving_capture() -> Any:
        host.state.package = SimpleNamespace(id=18)
        return SimpleNamespace(rows=ROWS, epochs=None)

    panel = module["show"](host.qt, host.parent, capture=moving_capture)
    assert "changed during capture" in panel.status_line.text()
    assert panel.page_rows == ()
    panel.close_owned() if title == TITLES[0] else panel.close()


def test_windows_directory_has_exactly_two_tools() -> None:
    assert {path.stem for path in (ROOT / "Scripts" / "Windows").glob("*.py")} == set(
        TITLES
    )


@pytest.mark.parametrize("title", TITLES)
def test_setup_failure_releases_owned_widget_and_connections(
    title: str, host: Any
) -> None:
    module = load(title)

    class BrokenButton(Widget):
        def __init__(self, *args: Any) -> None:
            raise RuntimeError("button setup failed")

    host.qt.QtGui.QPushButton = BrokenButton
    with pytest.raises(RuntimeError, match="button setup failed"):
        module["show"](host.qt, host.parent)
    assert module["_PANELS"] == []
    if title == TITLES[0]:
        assert host.parent.local_removed.deleted
    else:
        panel = next(
            child for child in host.parent.owned_children if hasattr(child, "scope")
        )
        assert panel.deleted and panel.scope.dead


def test_dock_failed_shared_cleanup_retains_owner_until_parent_destruction(
    host: Any, monkeypatch: Any
) -> None:
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)
    content = panel.owned.content

    def failing_remove(self: Any, dock: Any) -> None:
        raise RuntimeError("native remove refused")

    monkeypatch.setattr(type(host.parent), "removeDockWidget", failing_remove)
    assert not panel.close_owned()
    assert panel in module["_PANELS"] and not panel.owned.widget.deleted
    assert "native remove refused" in panel.status_line.text()
    assert not panel.close_owned()
    assert "incomplete" in panel.status_line.text()
    content.destroyed.emit()
    assert panel not in module["_PANELS"]
    assert panel.close_owned()


def test_dock_invalid_area_is_refused_without_native_widget_creation(host: Any) -> None:
    module = load(TITLES[0])
    with pytest.raises(ValueError, match="Dock area"):
        module["show"](host.qt, host.parent, area="middle")
    assert module["_PANELS"] == []


def test_diff_snapshot_rejects_malformed_codepoints_epochs_and_lossy_text() -> None:
    module = load(TITLES[1])
    cases = (
        SimpleNamespace(rows=(("A", "U+ZZZZ", ""),), epochs=None),
        SimpleNamespace(rows=(("A", "", ""),), epochs=(True,)),
        SimpleNamespace(rows=(("A", "", ""),), epochs=()),
        SimpleNamespace(rows=(("A", "", "bad\u2028date"),), epochs=None),
    )
    for table in cases:
        with pytest.raises(ValueError):
            module["snapshot"](table)


def test_all_twenty_four_source_identities_have_recorded_hashes() -> None:
    families = {
        "application",
        "sdi",
        "dockwidgets",
        "menus",
        "mdi",
        "separations",
        "basiclayouts",
        "borderlayout",
        "recentfiles",
        "flowlayout",
        "screenshot",
        "systray",
    }
    source_rows = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    matched = [
        row
        for row in source_rows
        if Path(row["target"]).stem.rsplit("-", 1)[0] in families
        and any(
            "/" + group + "/" in row["target"]
            for group in ("mainwindows", "layouts", "desktop")
        )
    ]
    assert len(matched) == 24
    for row in matched:
        assert (
            recorded_sha256(row['target'])
            == row["target_sha256"]
        )


@pytest.mark.parametrize("title", TITLES)
def test_script_qt_names_are_in_the_host_shaped_fake(title: str, host: Any) -> None:
    """Audit every direct Qt namespace access, including unexecuted slots."""
    assert set(vars(host.qt.QtCore)) == {"Qt", "QEvent"}
    assert set(vars(host.qt.QtGui)) == {
        "QWidget",
        "QLabel",
        "QLineEdit",
        "QPushButton",
        "QVBoxLayout",
        "QHBoxLayout",
        "QTableView",
        "QDockWidget",
        "QStandardItemModel",
        "QStandardItem",
        "QAbstractItemView",
        "QApplication",
        "QMessageBox",
    }
    for namespace, name in (
        (host.qt.QtCore, "QObject"),
        (host.qt.QtCore, "QWidget"),
        (host.qt.QtGui, "QObject"),
        (host.qt.QtGui, "QMissingWidget"),
    ):
        with pytest.raises(AttributeError):
            getattr(namespace, name)
    tree = ast.parse((ROOT / "Scripts" / "Windows" / f"{title}.py").read_text())
    aliases = {"core": host.qt.QtCore, "gui": host.qt.QtGui}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        namespace = (
            aliases.get(node.value.id) if isinstance(node.value, ast.Name) else None
        )
        if (
            isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name)
            and node.value.value.id == "qt"
        ):
            namespace = {"QtCore": host.qt.QtCore, "QtGui": host.qt.QtGui}.get(
                node.value.attr
            )
        if namespace is not None:
            assert node.attr in vars(namespace), (
                f"Unsupported Qt name: {ast.unparse(node)}"
            )


def test_close_filter_is_a_qtgui_widget_parented_to_the_dock(host: Any) -> None:
    module = load(TITLES[0])
    panel = module["show"](host.qt, host.parent)
    assert isinstance(panel.close_filter, host.qt.QtGui.QWidget)
    assert not panel.close_filter.isVisible()
    assert panel.close_filter in panel.owned.widget.owned_children
    assert panel.close_filter in panel.owned.widget.local_filters
    dock = panel.owned.widget
    dock.close()
    assert dock.deleted and panel.owned.closed and panel not in module["_PANELS"]
