# this_file: tests/test_issue122_E3.py
"""Exercise all E3 algorithms and execute modeless panels with host-shaped fakes."""

import ast
import importlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
TITLES = (
    "FontLab Script Scaffold Wizard",
    "Glyph Batch Recipe Settings",
    "Expandable Glyph Search",
    "Proof Text Coverage Dialog",
    "Font Glyph Inventory Tabs",
    "Glyph Proof Batch Wizard",
)


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts" / "Dialogs" / f"{title}.py"))


def test_scaffold_is_valid_python_and_refuses_invalid_names() -> None:
    render = load(TITLES[0])["scaffold"]
    code = render("AuditWidths", "Inspect widths")
    ast.parse(code)
    assert "class AuditWidths:" in code
    assert "from fly import fl" in code
    for name in ("", "class", "a-b", "x\ny", "1abc", "fl", "TITLE", "main", "tuple"):
        with pytest.raises(ValueError):
            render(name, "Inspect")
    # Titles are data, including embedded quotes and newlines.
    ast.parse(render("Audit", 'A "title"\nnext'))


def test_recipe_has_exact_scope_and_batch_count() -> None:
    render = load(TITLES[1])["recipe"]
    assert json.loads(render(("A", "A.alt", "B"), "A", 1)) == {
        "prefix": "A",
        "batch_size": 1,
        "glyphs": ["A", "A.alt"],
        "batches": 2,
    }
    with pytest.raises(ValueError):
        render(("A",), "Z", 10)
    for size in (0, -1, 1001, True):
        with pytest.raises(ValueError):
            render(("A",), "", size)


def test_search_handles_exact_case_and_reverse() -> None:
    search = load(TITLES[2])["search"]
    names = ("A", "A.alt", "a", "B")
    assert search(names, "a", False, False, False) == ("A", "A.alt", "a")
    assert search(names, "A", True, True, True) == ("A",)
    assert search(names, "a", False, True, True) == ("a", "A")
    assert search(names, "Z", True, False, False) == ()
    with pytest.raises(ValueError):
        search(names, "", False, False, False)


def test_coverage_reports_missing_duplicates_and_supplementary_codes() -> None:
    coverage = load(TITLES[3])["coverage"]
    rows = (("A", (65,)), ("A.alt", (65,)), ("smile", (0x1F600,)))
    assert coverage(rows, "A😀A!") == (
        "U+0041  A, A.alt\nU+1F600  smile\nU+0021  MISSING"
    )
    assert coverage(rows, "\ud83d\ude00") == "U+1F600  smile"
    assert coverage(rows, "\ud800") == "U+FFFD  MISSING"
    with pytest.raises(ValueError):
        coverage(rows, "")


def test_inventory_exact_numbers_and_proof_chunks() -> None:
    inventory = load(TITLES[4])["inventory"]
    assert inventory((("A", (65,)), ("A.alt", (65,)), ("blank", ()))) == (
        "Glyphs: 3\nEncoded glyphs: 2\nDistinct codepoints: 1",
        "A\nA.alt\nblank",
        "U+0041  A, A.alt",
    )
    chunks = load(TITLES[5])["proof_batches"]
    assert chunks(("A", "A.alt", "B"), "", 2) == "/A/A.alt\n/B"
    assert chunks(("A", "A.alt", "B"), "A", 5) == "/A/A.alt"
    with pytest.raises(ValueError):
        chunks(("A",), "Z", 5)
    with pytest.raises(ValueError):
        chunks(("bad/name",), "", 5)


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, callback: Any) -> None:
        self.slots.append(callback)

    def disconnect(self, callback: Any) -> None:
        self.slots.remove(callback)

    def emit(self, *args: Any) -> None:
        for slot in self.slots[:]:
            slot(*args)


class Widget:
    """Small Qt property-shaped double; no font-writing API exists."""

    def __init__(self, *args: Any) -> None:
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.value = 10
        self.checked = False
        self.currentIndex = 0
        self.clicked, self.toggled, self.currentRowChanged = (
            Signal(),
            Signal(),
            Signal(),
        )
        self.textValueSelected = Signal()
        self.items: list[Any] = []
        self.visible = False

    def setText(self, text: str) -> None:
        self.text = text

    def setPlainText(self, text: str) -> None:
        self.text = text

    def toPlainText(self) -> str:
        return self.text

    def setValue(self, value: int) -> None:
        self.value = value

    def setChecked(self, value: bool) -> None:
        self.checked = value

    def addWidget(self, widget: Any) -> None:
        self.items.append(widget)

    def addTab(self, widget: Any, label: str) -> None:
        self.items.append((widget, label))

    def addItems(self, items: Any) -> None:
        self.items.extend(items)

    def setCurrentIndex(self, index: int) -> None:
        self.currentIndex = index

    def setVisible(self, value: bool) -> None:
        self.visible = value

    def show(self) -> None:
        object.__setattr__(self, "visible", True)

    def close(self) -> bool:
        object.__setattr__(self, "visible", False)
        for signal, slot in self._connections[:]:
            signal.disconnect(slot)
        self._connections.clear()
        return True

    def __getattr__(self, name: str) -> Any:
        if name.startswith("set") or name in ("resize", "hide", "adjustSize"):
            return lambda *args: None
        raise AttributeError(name)


RESERVED = frozenset(
    [
        "size",
        "name",
        "text",
        "width",
        "height",
        "font",
        "palette",
        "layout",
        "title",
        "windowTitle",
        "result",
        "value",
        "acceptDrops",
        "accessibleDescription",
        "accessibleName",
        "autoFillBackground",
        "baseSize",
        "childrenRect",
        "childrenRegion",
        "contextMenuPolicy",
        "cursor",
        "enabled",
        "focus",
        "focusPolicy",
        "frameGeometry",
        "frameSize",
        "fullScreen",
        "geometry",
        "inputMethodHints",
        "isActiveWindow",
        "layoutDirection",
        "locale",
        "maximized",
        "maximumHeight",
        "maximumSize",
        "maximumWidth",
        "minimized",
        "minimumHeight",
        "minimumSize",
        "minimumSizeHint",
        "minimumWidth",
        "modal",
        "mouseTracking",
        "normalGeometry",
        "objectName",
        "opacity",
        "parent",
        "pos",
        "rect",
        "sizeGripEnabled",
        "sizeHint",
        "sizePolicy",
        "statusTip",
        "styleSheet",
        "toolTip",
        "toolTipDuration",
        "updatesEnabled",
        "visible",
        "whatsThis",
        "windowFilePath",
        "windowFlags",
        "windowIcon",
        "windowIconText",
        "windowModality",
        "windowModified",
        "windowOpacity",
        "windowRole",
        "windowState",
        "windowType",
        "x",
        "y",
        "z",
        "accept",
        "reject",
        "accepted",
        "rejected",
        "finished",
        "done",
        "exec",
        "open",
        "close",
        "show",
        "hide",
        "resize",
        "move",
        "raise_",
        "lower",
        "activateWindow",
        "adjustSize",
        "event",
        "eventFilter",
        "findChild",
        "findChildren",
        "children",
        "parentWidget",
        "setLayout",
        "setFont",
        "setPalette",
        "setVisible",
        "setWindowTitle",
        "deleteLater",
        "destroyed",
        "connect",
        "disconnect",
        "inherits",
        "property",
        "setProperty",
        "metaObject",
        "winId",
        "effectiveWinId",
        "nativeParentWidget",
        "window",
        "windowHandle",
        "style",
        "actions",
        "addAction",
        "removeAction",
        "render",
        "repaint",
        "update",
        "updateGeometry",
        "setGeometry",
        "setFixedSize",
        "grab",
        "releaseMouse",
        "releaseKeyboard",
        "grabMouse",
        "grabKeyboard",
        "focusWidget",
        "nextInFocusChain",
        "previousInFocusChain",
        "hasFocus",
        "hasMouseTracking",
        "hasTabletTracking",
        "isEnabled",
        "isVisible",
        "isWindow",
        "isHidden",
    ]
)


class Panel(Widget):
    """Reject native-member shadowing on the dialog itself, like PythonQt."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in RESERVED:
            raise AttributeError(f"Native dialog member cannot be shadowed: {name}")
        object.__setattr__(self, name, value)

    def __init__(self, parent: Any, title: str, key: str) -> None:
        self.items: list[Any] = []
        self.visible_state = False
        self._connections: list[Any] = []
        self.root, self.subtitle = Widget(), Widget()

    def _connect(self, signal: Signal, callback: Any) -> None:
        def guarded(*args: Any) -> None:
            try:
                callback(*args)
            except Exception as error:  # noqa: BLE001 - mirror the App callback boundary
                self.status.setText(str(error))

        signal.connect(guarded)
        self._connections.append((signal, guarded))


class NativeRecord:
    """Read-only host object. Record and refuse all exposed native mutations."""

    def __init__(self, writes: list[Any], **values: Any) -> None:
        object.__setattr__(self, "_writes", writes)
        object.__setattr__(self, "_values", values)

    def __setattr__(self, name: str, value: Any) -> None:
        self._writes.append(("set", name, value))
        raise AssertionError(f"Unexpected native write: {name}")

    def __getattr__(self, name: str) -> Any:
        if name in {
            "notifyChangesApplied",
            "UpdateAll",
            "Select",
            "Unselect",
            "setMaster",
            "setProperty",
            "changed",
            "update",
            "setText",
            "setValue",
        }:

            def record(*args: Any, **kwargs: Any) -> None:
                self._writes.append((name, args, kwargs))
                raise AssertionError(f"Unexpected native writer: {name}")

            return record
        if name == "glyphs":
            return self._values["read_glyphs"]()
        if name == "currentPackage":
            return self._values["read_package"]()
        return self._values[name] if name in self._values else self._missing(name)

    def _missing(self, name: str) -> Any:
        raise AttributeError(name)


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    # Exercise the real App capture, not an imitation of its fences or scans.
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp" / "src"))
    native_capture = importlib.import_module("fontlabapp._glyph_catalog_native")
    state = SimpleNamespace(
        font=True,
        panels=[],
        writes=[],
        reads=0,
        rows=(("A", (65,)), ("A.alt", (65,)), ("B", (66,))),
        context_calls=0,
        context_hook=None,
        read_hook=None,
    )
    mapped: dict[int, Any] = {}
    state.package = NativeRecord(
        state.writes,
        id=9,
        fgId=99,
        master="Regular",
        isNull=False,
        findFgId=lambda identity: mapped.get(identity),
    )

    def read_glyphs() -> tuple[Any, ...]:
        state.reads += 1
        if state.read_hook is not None:
            state.read_hook()
        result = []
        for identity, (name, codes) in enumerate(state.rows, 1):
            result.append(
                NativeRecord(state.writes, id=identity, name=name, unicodes=codes)
            )
            mapped[identity] = NativeRecord(
                state.writes,
                id=identity + 100,
                name=name,
                fgGlyphId=identity,
                package=state.package,
                isNull=False,
                isValid=True,
                lastModified=NativeRecord(state.writes, isValid=False),
            )
        return tuple(result)

    state.native_font = NativeRecord(state.writes, id=99, read_glyphs=read_glyphs)
    workspace = NativeRecord(
        state.writes, read_package=lambda: state.package if state.font else None
    )

    def current_font() -> Any:
        state.context_calls += 1
        if state.context_hook is not None:
            state.context_hook()
        return state.native_font if state.font else None

    state.native = NativeRecord(
        state.writes,
        CurrentFont=current_font,
        flWorkspace=SimpleNamespace(instance=lambda: workspace),
        flItems=NativeRecord(state.writes),
        fl=NativeRecord(state.writes),
    )
    monkeypatch.setattr(native_capture, "_native", lambda name: state.native)
    state.capture_module = native_capture
    scripting = ModuleType("fly.ap.scripting")
    scripting.names_dialog_type = lambda: Panel

    def show(factory: Any, key: str) -> Any:
        panel = factory(None)
        state.panels.append(panel)
        panel.show()
        return panel

    scripting.show_script_dialog = show
    fly = ModuleType("fly")
    fly.fl = state.native
    fly.qt = SimpleNamespace(
        QtGui=SimpleNamespace(
            **{
                name: Widget
                for name in (
                    "QWidget",
                    "QVBoxLayout",
                    "QHBoxLayout",
                    "QLabel",
                    "QLineEdit",
                    "QPlainTextEdit",
                    "QPushButton",
                    "QCheckBox",
                    "QSpinBox",
                    "QStackedWidget",
                    "QListWidget",
                    "QTabWidget",
                    "QInputDialog",
                )
            }
        )
    )
    for name, module in (
        ("fly", fly),
        ("fly.ap", ModuleType("fly.ap")),
        ("fly.ap.scripting", scripting),
        ("fly.ap._glyph_catalog_native", native_capture),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    return state


@pytest.mark.parametrize("title", TITLES)
def test_each_panel_runs_refresh_refuses_and_disconnects(title: str, host: Any) -> None:
    module = load(title)
    assert not host.panels, "Import must not open a panel."
    panel = module["main"]()
    assert panel.visible
    panel.preview()
    assert panel.output.text, "Each panel must produce useful text."
    host.font = False
    panel.preview()
    # Scaffold supports scripting without a font. Other tools must clear stale output.
    if title != TITLES[0]:
        assert panel.output.text == ""
        assert "Open a font" in panel.status.text
    assert not host.writes
    signals = [signal for signal, _ in panel._connections]
    panel.close()
    assert all(not signal.slots for signal in signals)


@pytest.mark.parametrize("field,value", (("id", 10), ("fgId", 100), ("master", "Bold")))
def test_shared_capture_refuses_changed_context(
    field: str, value: Any, host: Any
) -> None:
    read = load(TITLES[2])["glyph_rows"]
    assert read() == (("A", (65,)), ("A.alt", (65,)), ("B", (66,)))
    host.context_calls = 0

    def change() -> None:
        if host.context_calls == 2:
            host.package._values[field] = value

    host.context_hook = change
    with pytest.raises(ValueError, match="changed|unreadable"):
        read()


@pytest.mark.parametrize("code", (0xD800, 0x110000, -1, True))
def test_shared_capture_or_adapter_refuses_invalid_codes(code: int, host: Any) -> None:
    host.rows = (("bad", (code,)),)
    with pytest.raises(ValueError):
        load(TITLES[2])["glyph_rows"]()


@pytest.mark.parametrize("title", (TITLES[0], TITLES[5]))
def test_wizard_advances_only_with_valid_input(title: str, host: Any) -> None:
    panel = load(title)["main"]()
    if title == TITLES[0]:
        panel.class_name.text = "class"
    else:
        panel.prefix.text = "Missing"
    panel.advance()
    assert panel.pages.currentIndex == 0
    assert panel.output.text == ""
    if title == TITLES[0]:
        panel.class_name.text = "MyTool"
    else:
        panel.prefix.text = "A"
    panel.advance()
    assert panel.pages.currentIndex == 1
    assert panel.output.text
    back = next(w for w in panel.root.items if w.text == "Back")
    back.clicked.emit(False)
    assert panel.pages.currentIndex == 0


def test_settings_and_more_controls_execute_their_callbacks(host: Any) -> None:
    settings = load(TITLES[1])["main"]()
    settings.navigation.currentRowChanged.emit(2)
    assert settings.pages.currentIndex == 2
    search = load(TITLES[2])["main"]()
    more = next(w for w in search.root.items if w.text == "More Options")
    more.toggled.emit(True)
    assert search.options.visible
    search.exact.checked = True
    search.case.checked = True
    search.query.text = "A"
    button = next(w for w in search.root.items if w.text == "Preview / Refresh")
    button.clicked.emit(False)
    assert search.output.text == "A"


def test_standard_input_accepts_text_and_cancel_keeps_draft(host: Any) -> None:
    panel = load(TITLES[3])["main"]()
    enter = next(w for w in panel.root.items if w.text == "Enter Proof Text")
    enter.clicked.emit(False)
    assert panel.input_dialog.visible
    panel.input_dialog.textValueSelected.emit("AB!")
    assert panel.draft == "AB!"
    assert panel.output.text == "U+0041  A, A.alt\nU+0042  B\nU+0021  MISSING"
    # Cancel hides the standard dialog; no accepted-text signal fires.
    panel.input_dialog.hide()
    assert panel.draft == "AB!"


def test_inventory_clears_all_tabs_after_failed_refresh(host: Any) -> None:
    panel = load(TITLES[4])["main"]()
    panel.preview()
    assert all(editor.text for editor in panel.extra_outputs)
    host.font = False
    panel.preview()
    assert all(editor.text == "" for editor in panel.extra_outputs)


@pytest.mark.parametrize("title", TITLES[1:])
def test_empty_font_is_handled_without_writes(title: str, host: Any) -> None:
    host.rows = ()
    panel = load(title)["main"]()
    panel.preview()
    assert panel.status.text
    if title == TITLES[4]:
        assert (
            panel.output.text == "Glyphs: 0\nEncoded glyphs: 0\nDistinct codepoints: 0"
        )


def test_shared_capture_rejects_duplicate_names(host: Any) -> None:
    host.rows = (("A", ()), ("A", ()))
    with pytest.raises(ValueError, match="Duplicate"):
        load(TITLES[2])["glyph_rows"]()


def test_shared_capture_checks_budget_before_second_scan(
    host: Any, monkeypatch: Any
) -> None:
    clock = SimpleNamespace(now=0.0)
    monkeypatch.setattr(host.capture_module, "monotonic", lambda: clock.now)
    reader = load(TITLES[2])["glyph_rows"]
    reader.__globals__["monotonic"] = lambda: clock.now
    host.read_hook = lambda: setattr(clock, "now", 3.0)
    with pytest.raises(TimeoutError):
        reader()
    assert host.reads == 1, "An expired first scan must not start a second scan."


def test_shared_capture_refuses_metadata_changed_between_scans(host: Any) -> None:
    def change() -> None:
        if host.reads == 2:
            host.rows = (("changed", (66,)),)

    host.read_hook = change
    with pytest.raises(ValueError, match="changed"):
        load(TITLES[2])["glyph_rows"]()


@pytest.mark.parametrize("name", sorted(RESERVED))
def test_panel_fake_rejects_reserved_native_members(name: str) -> None:
    panel = Panel(None, "Test", "test")
    with pytest.raises(AttributeError, match="cannot be shadowed"):
        setattr(panel, name, Widget())


def test_settings_recipe_is_consumed_by_proof_wizard(host: Any) -> None:
    settings = load(TITLES[1])["main"]()
    settings.prefix.text = "A"
    settings.batch_size.setValue(1)
    assert settings.preview()
    assert settings.pages.currentIndex == 2, "Preview must reveal the recipe."
    wizard = load(TITLES[5])["main"]()
    wizard.recipe_input.setPlainText(settings.output.text)
    assert wizard.preview()
    assert wizard.pages.currentIndex == 1, "Preview must reveal proof lines."
    assert wizard.output.text == "/A\n/A.alt"
    assert wizard.batch_size.value == 1
    assert wizard.prefix.text == "A"


@pytest.mark.parametrize("mutation", ("invalid", "size", "missing", "stale", "count"))
def test_recipe_consumer_refuses_invalid_or_stale_recipe(mutation: str) -> None:
    payload = load(TITLES[1])["recipe"](("A", "B"), "", 2)
    consume = load(TITLES[5])["proof_from_recipe"]
    data = json.loads(payload)
    if mutation == "invalid":
        payload = "not JSON"
    elif mutation == "size":
        data["batch_size"] = True
    elif mutation == "missing":
        del data["glyphs"]
    elif mutation == "stale":
        data["glyphs"] = ["A", "C"]
    else:
        data["batches"] = 9
    if mutation != "invalid":
        payload = json.dumps(data)
    with pytest.raises(ValueError):
        consume(payload, ("A", "B"))


def test_scaffold_can_run_with_title_constant_and_main(host: Any) -> None:
    code = load(TITLES[0])["scaffold"]("AuditWidths", 'Inspect "widths"')
    tree = ast.parse(code)
    assert any(isinstance(n, ast.FunctionDef) and n.name == "main" for n in tree.body)
    namespace: dict[str, Any] = {}
    exec(compile(code, "scaffold", "exec"), namespace)  # noqa: S102 - test our generated code, never preserved sources
    assert namespace["TITLE"] == 'Inspect "widths"'
    assert namespace["main"]() == ("A", "A.alt", "B")


def test_native_write_spies_record_mutations(host: Any) -> None:
    with pytest.raises(AssertionError):
        host.native.flItems.notifyChangesApplied("Unexpected", [])
    with pytest.raises(AssertionError):
        host.native.UpdateAll()
    with pytest.raises(AssertionError):
        host.native.fl.Select(0)
    with pytest.raises(AssertionError):
        host.package.master = "Bold"
    assert [call[0] for call in host.writes] == [
        "notifyChangesApplied",
        "UpdateAll",
        "Select",
        "set",
    ]


def test_scripts_explain_why_and_benefit_and_avoid_shadowing() -> None:
    for title in TITLES:
        path = ROOT / "Scripts" / "Dialogs" / f"{title}.py"
        tree = ast.parse(path.read_text(), feature_version=(3, 11))
        doc = ast.get_docstring(tree)
        assert "Why:" in doc and "Benefit:" in doc
        assert "Fly and fontlabapp" in doc
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                for target in targets:
                    if (
                        isinstance(target, ast.Attribute)
                        and isinstance(target.value, ast.Name)
                        and target.value.id == "self"
                    ):
                        assert target.attr not in RESERVED, (
                            f"{title}: shadows {target.attr}"
                        )
