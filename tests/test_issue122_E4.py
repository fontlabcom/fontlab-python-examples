# this_file: tests/test_issue122_E4.py
"""Check the five graphics rewrites without executing preserved source bodies."""

import ast
import hashlib
import importlib
import os
import re
import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
TITLES = (
    "Glyph Proof Layout",
    "Glyph Variant Feature Graph",
    "Glyph Review Cards",
    "Glyph Proof Pad",
)
MARK_TITLE = "Glyph Mark Colour Board"


def load(title: str) -> dict[str, Any]:
    """Import only a new script, with no UI side effect."""
    return runpy.run_path(str(ROOT / "Scripts/Graphics" / f"{title}.py"))


def test_anchor_layout_selects_complete_named_sample() -> None:
    sample = load(TITLES[0])["proof_sample"]
    assert sample(("A", "V", "A.alt", "B"), "A") == ("A", "A.alt")
    assert sample(("A", "V"), "") == ("A", "V")
    with pytest.raises(ValueError, match="No glyph"):
        sample(("A",), "Z")
    with pytest.raises(ValueError, match="12"):
        sample(tuple(f"g{i}" for i in range(13)), "")


def test_feature_graph_keeps_exact_suffix_relations_and_draft() -> None:
    module = load(TITLES[1])
    edges = module["variant_edges"](
        ("A", "A.alt", "A.alt.alt", "B.alt", "B", "orphan.alt"), "alt"
    )
    assert edges == (("A", "A.alt"), ("A.alt", "A.alt.alt"), ("B", "B.alt"))
    assert (
        module["feature_draft"](edges)
        == "# Draft only; choose a feature and compile in FontLab.\nsub \\A by \\A.alt;\nsub \\A.alt by \\A.alt.alt;\nsub \\B by \\B.alt;"
    )
    assert module["variant_edges"](("A", "A.ss01", "A.ss010"), "ss01") == (
        ("A", "A.ss01"),
    )
    with pytest.raises(ValueError, match="No matching"):
        module["variant_edges"](("A", "orphan.alt"), "alt")


@pytest.mark.parametrize("suffix", ("", ".alt", "a b", "a/b", "a;", "a\n", "é"))
def test_feature_graph_refuses_invalid_suffix(suffix: str) -> None:
    with pytest.raises(ValueError):
        load(TITLES[1])["variant_edges"](("A", "A.alt"), suffix)


def test_review_report_preserves_multiline_notes_and_unencoded_names() -> None:
    report = load(TITLES[2])["review_report"]
    assert (
        report((("A.alt", "Check", "Top\nBottom"), ("B", "OK", "")))
        == "A.alt [Check]\nTop\nBottom\n\nB [OK]\n"
    )
    with pytest.raises(ValueError):
        report((("A", "Unknown", ""),))


def test_pad_exact_page_boundaries_and_proof() -> None:
    page = load(TITLES[3])["page_names"]
    names = tuple(f"g{i}" for i in range(19))
    assert page(names, 0) == names[:9]
    assert page(names, 1) == names[9:18]
    assert page(names, 2) == ("g18",)
    for index in (-1, 3, True):
        with pytest.raises(ValueError):
            page(names, index)
    with pytest.raises(ValueError, match="empty"):
        page((), 0)


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "name",
    (
        "bad/name",
        "bad name",
        "bad\x00",
        "bad\u00a0",
        "bad\u2028",
        "bad\u2029",
        "bad\ud800",
    ),
)
def test_capture_refuses_lossy_or_unusable_names(
    title: str, name: str, host: Any
) -> None:
    host.rows = ((name, "", ""),)
    with pytest.raises(ValueError):
        load(title)["capture_names"]()


class Signal:
    """Retain exact callback identities, with disconnect failure injection."""

    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.fail = False

    def connect(self, call: Any) -> None:
        self.slots.append(call)

    def disconnect(self, call: Any) -> None:
        if self.fail:
            raise RuntimeError("disconnect refused")
        self.slots.remove(call)

    def emit(self, *args: Any) -> None:
        for call in tuple(self.slots):
            call(*args)


RESERVED = {
    "render",
    "update",
    "scroll",
    "move",
    "layout",
    "data",
    "parent",
    "children",
    "font",
    "palette",
    "geometry",
    "scene",
    "statusTip",
    "size",
    "windowTitle",
    "close",
    "text",
    "value",
}


class KeySequence:
    def __init__(self, text: str) -> None:
        self.sequence = text


class Colour:
    def __init__(self, value: Any) -> None:
        self.css = value.css if isinstance(value, Colour) else value

    def hslHue(self) -> int:
        return {
            "transparent": -1,
            "#ff0000": 0,
            "#ffff00": 60,
            "#00ff00": 120,
            "#00ffff": 180,
            "#0000ff": 240,
            "#ff00ff": 300,
        }[self.css]

    def hslSaturation(self) -> int:
        return 0 if self.css == "transparent" else 255

    def alpha(self) -> int:
        return 0 if self.css == "transparent" else 255


class Mime:
    def __init__(self) -> None:
        self.colour: Any = None

    def setColorData(self, colour: Any) -> None:
        self.colour = colour

    def hasColor(self) -> bool:
        return self.colour is not None

    def colorData(self) -> Any:
        return self.colour


class Widget:
    """Native-shaped fake: only named public methods, no permissive fallback."""

    def __setattr__(self, name: str, value: Any) -> None:
        if name in RESERVED:
            raise AttributeError(f"native member: {name}")
        object.__setattr__(self, name, value)

    def __init__(self, *args: Any) -> None:
        self._text = args[0] if args and isinstance(args[0], str) else ""
        self._value = 0
        self._index = 0
        self._items: list[Any] = []
        self._deleted = False
        self._visible = False
        self.clicked, self.destroyed = Signal(), Signal()
        self._pos = (0, 0)
        self._base_events: list[str] = []

    def mousePressEvent(self, event: Any) -> None:
        self._base_events.append("mousePressEvent")

    def dragEnterEvent(self, event: Any) -> None:
        self._base_events.append("dragEnterEvent")

    def dragMoveEvent(self, event: Any) -> None:
        self._base_events.append("dragMoveEvent")

    def dragLeaveEvent(self, event: Any) -> None:
        self._base_events.append("dragLeaveEvent")

    def dropEvent(self, event: Any) -> None:
        self._base_events.append("dropEvent")

    def setText(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text

    def setPlainText(self, text: str) -> None:
        self._text = text

    def toPlainText(self) -> str:
        return self._text

    def setPlaceholderText(self, text: str) -> None:
        pass

    def setReadOnly(self, state: bool) -> None:
        pass

    def setWordWrap(self, state: bool) -> None:
        pass

    def setTextFormat(self, fmt: Any) -> None:
        pass

    def setWindowTitle(self, title: str) -> None:
        pass

    def setAttribute(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def addWidget(self, item: Any) -> Any:
        self._items.append(item)
        proxy = Widget()
        proxy._items.append(item)
        return proxy

    def addLayout(self, item: Any) -> None:
        self._items.append(item)

    def addItems(self, items: Any) -> None:
        self._items.extend(items)

    def currentText(self) -> str:
        return self._items[self._index]

    def setRange(self, *args: Any) -> None:
        pass

    def setValue(self, number: int) -> None:
        self._value = number

    def value(self) -> int:
        return self._value

    def clear(self) -> None:
        self._items.clear()
        self._text = ""

    def addSimpleText(self, text: str) -> Any:
        item = Widget(text)
        self._items.append(item)
        return item

    def addLine(self, *args: Any) -> Any:
        item = Widget()
        self._items.append(item)
        return item

    def addItem(self, item: Any) -> None:
        self._items.append(item)

    def setPos(self, x: float, y: float) -> None:
        self._pos = (x, y)

    def setToolTip(self, text: str) -> None:
        pass

    def setMinimumSize(self, *args: Any) -> None:
        self._minimum_size = args

    def setPreferredSize(self, *args: Any) -> None:
        self._preferred_size = args

    def setMaximumSize(self, *args: Any) -> None:
        self._maximum_size = args

    def setStyleSheet(self, css: str) -> None:
        self._style = css

    def setAcceptDrops(self, enabled: bool) -> None:
        self._accept_drops = enabled

    def setLayout(self, item: Any) -> None:
        self._items.append(item)

    def addAnchor(self, *args: Any) -> Any:
        self._items.append(args)
        return Widget()

    def setSpacing(self, *args: Any) -> None:
        pass

    def setGeometry(self, *args: Any) -> None:
        self._geometry_value = args

    def setSceneRect(self, *args: Any) -> None:
        pass

    def itemsBoundingRect(self) -> Any:
        return (0, 0, 100, 100)

    def fitInView(self, *args: Any) -> None:
        pass

    def setShortcut(self, *args: Any) -> None:
        assert len(args) == 1 and isinstance(args[0], KeySequence), (
            "Pass an explicit QKeySequence."
        )

    def show(self) -> None:
        self._visible = True

    def raise_(self) -> None:
        pass

    def deleteLater(self) -> None:
        self._deleted = True

    def close(self) -> bool:
        event = SimpleNamespace(accepted=None)
        event.accept = lambda: setattr(event, "accepted", True)
        event.ignore = lambda: setattr(event, "accepted", False)
        self.closeEvent(event)
        return event.accepted


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    """Use the real App lifecycle scope and fake only Qt and catalogue I/O."""
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp/src"))
    scope = importlib.import_module("fontlabapp.draft_signals")
    props = importlib.import_module("fontlabapp.qt_properties")
    state = SimpleNamespace(
        rows=(("A", "U+0041", ""), ("A.alt", "", ""), ("B", "U+0042", "")),
        error=None,
        panels=[],
        copied="",
        writes=[],
    )

    def capture(**kwargs: Any) -> Any:
        if state.error:
            raise state.error
        return SimpleNamespace(rows=state.rows)

    catalog = ModuleType("fly.ap.glyph_catalog")
    catalog.capture = capture
    scripting = ModuleType("fly.ap.scripting")

    def show(factory: Any, key: str) -> Any:
        panel = factory(None)
        state.panels.append(panel)
        panel.show()
        return panel

    scripting.show_script_dialog = show
    state.layer_reads, state.layer_hook = 0, None
    state.metrics = {"A": (500.0, 40.0, 50.0), "A.alt": (250.0, 10.0, 20.0)}
    state.package = SimpleNamespace(id=12, fgId=13, master="Regular", isNull=False)

    def find_name(name: str) -> Any:
        available = [row[0] for row in state.rows]
        if name not in available:
            return None
        identity = available.index(name) + 20
        glyph = SimpleNamespace(
            id=identity, name=name, isValid=True, isNull=False, package=state.package
        )

        def find_layer(master: str) -> Any:
            state.layer_reads += 1
            if state.layer_hook:
                state.layer_hook()
            advance, left, right = state.metrics.get(name, (600.0, 30.0, 40.0))
            return SimpleNamespace(
                id=identity + 100,
                isNull=False,
                advanceWidth=advance,
                shapesCount=1,
                boundingBox=SimpleNamespace(
                    isNull=False, left=left, right=advance - right
                ),
            )

        glyph.findLayer = find_layer
        return glyph

    state.package.findName = find_name
    scripting.current_package = lambda: state.package
    gui = SimpleNamespace(
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
                "QComboBox",
                "QSpinBox",
                "QGraphicsScene",
                "QGraphicsView",
                "QGraphicsWidget",
                "QGraphicsAnchorLayout",
            )
        }
    )
    gui.QApplication = SimpleNamespace(
        clipboard=lambda: SimpleNamespace(
            setText=lambda text: setattr(state, "copied", text)
        )
    )
    gui.QKeySequence, gui.QColor = KeySequence, Colour
    core = SimpleNamespace(
        Qt=SimpleNamespace(
            Window=1,
            WA_QuitOnClose=2,
            PlainText=3,
            KeepAspectRatio=4,
            AnchorLeft=5,
            AnchorTop=6,
            AnchorRight=7,
            AnchorBottom=8,
            LeftButton=9,
            CopyAction=10,
        ),
        QRectF=lambda *args: args,
        QMimeData=Mime,
    )
    state.gui, state.core = gui, core

    class Drag(Widget):
        def setMimeData(self, mime: Any) -> None:
            self._mime = mime

        def exec(self, action: Any) -> None:
            if getattr(state, "drag_hook", None):
                state.drag_hook(self)

    gui.QDrag = Drag
    fly = ModuleType("fly")
    fly.qt = SimpleNamespace(QtGui=gui, QtCore=core)
    for name, module in (
        ("fly", fly),
        ("fly.ap", ModuleType("fly.ap")),
        ("fly.ap.glyph_catalog", catalog),
        ("fly.ap.scripting", scripting),
        ("fly.ap.draft_signals", scope),
        ("fly.ap.qt_properties", props),
    ):
        monkeypatch.setitem(sys.modules, name, module)
    return state


@pytest.mark.parametrize("title", TITLES)
def test_panel_constructs_refreshes_copies_and_disconnects(
    title: str, host: Any
) -> None:
    module = load(title)
    assert not host.panels
    panel = module["main"]()
    assert panel._visible
    assert panel.refresh()
    assert panel.canvas._items
    panel.copy_result()
    assert host.copied
    records = list(panel.scope.records)
    assert panel.close()
    assert panel._deleted
    assert all(not signal.slots for signal, _, _ in records)
    assert not host.writes


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "error",
    (
        ValueError("Open a font."),
        RuntimeError("Host unavailable."),
        TimeoutError("Scan expired."),
    ),
)
def test_failed_refresh_removes_stale_scene_and_copy_payload(
    title: str, error: Exception, host: Any
) -> None:
    panel = load(title)["main"]()
    assert panel.refresh()
    host.error = error
    assert not panel.refresh()
    assert not panel.canvas._items
    assert panel.result == ""
    assert str(error) in panel.message.text()
    with pytest.raises(ValueError):
        panel.copy_result()


@pytest.mark.parametrize("title", TITLES)
def test_close_is_refused_until_signal_disconnect_succeeds(
    title: str, host: Any
) -> None:
    panel = load(title)["main"]()
    signal = panel.scope.records[0][0]
    signal.fail = True
    assert not panel.close()
    assert not panel._deleted
    signal.fail = False
    assert panel.close()


def test_review_cards_keep_unsaved_notes_on_refresh_and_close(host: Any) -> None:
    panel = load(TITLES[2])["main"]()
    assert panel.refresh()
    panel.cards[0][2].setPlainText("Needs attention")
    assert not panel.refresh()
    assert not panel.close()
    assert panel.cards[0][2].toPlainText() == "Needs attention"
    panel.copy_result()
    assert "Needs attention" in host.copied
    assert panel.close()


def test_pad_navigation_clamps_and_copies_one_named_cell(host: Any) -> None:
    host.rows = tuple((f"g{i}", "", "") for i in range(19))
    panel = load(TITLES[3])["main"]()
    assert panel.refresh()
    panel.navigate(1)
    assert panel.page_index == 1
    panel.choose("g10")
    assert panel.result == "/g10"
    panel.navigate(999)
    assert panel.page_index == 2
    panel.navigate(-999)
    assert panel.page_index == 0


def test_pad_failed_page_release_keeps_page_index_and_disables_copy(host: Any) -> None:
    host.rows = tuple((f"g{i}", "", "") for i in range(19))
    panel = load(TITLES[3])["main"]()
    assert panel.refresh()
    signal = panel.page_scope.records[0][0]
    signal.fail = True
    with pytest.raises(RuntimeError, match="release"):
        panel.navigate(1)
    assert panel.page_index == 0, (
        "A failed page change must retain the visible page index."
    )
    assert panel.result == "", "Failed publication must not leave stale copy text."
    assert not panel.close()
    signal.fail = False
    assert panel.close()


def test_review_copy_updates_visible_report_and_owns_changed_status(host: Any) -> None:
    panel = load(TITLES[2])["main"]()
    assert panel.refresh()
    panel.cards[0][1]._index = 1
    panel.cards[0][2].setPlainText("Inspect mark")
    assert not panel.close()
    panel.copy_result()
    assert panel.output_box.toPlainText() == host.copied
    assert "A [Check]\nInspect mark" in host.copied
    assert panel.close()


def test_anchor_scene_contains_exact_shared_edge_constraints(host: Any) -> None:
    panel = load(TITLES[0])["main"]()
    panel.prefix_entry.setText("A")
    assert panel.refresh()
    container = panel.canvas._items[-1]
    anchors = container._items[0]
    assert len(anchors._items) == 7, (
        "Two tiles need top, bottom, join, and the final right edge."
    )
    assert container._geometry_value == ((0.0, 0.0, 900.0, 120.0),)
    assert panel.result == "/A/A.alt"


def test_feature_scene_has_directed_edge_and_exact_escaped_keywords(host: Any) -> None:
    panel = load(TITLES[1])["main"]()
    assert panel.refresh()
    assert len(panel.canvas._items) == 5, (
        "One pair has two labels and three arrow lines."
    )
    draft = load(TITLES[1])["feature_draft"]((("sub", "sub.alt"),))
    assert draft.endswith(r"sub \sub by \sub.alt;")
    with pytest.raises(ValueError):
        load(TITLES[1])["feature_draft"]((("A;", "A;.alt"),))


@pytest.mark.parametrize(
    "note", ("NUL\x00", "NBSP\u00a0", "line\u2028", "para\u2029", "CR\r", "bad\ud800")
)
def test_review_refuses_lossy_note_transfer_and_keeps_it_open(
    note: str, host: Any
) -> None:
    panel = load(TITLES[2])["main"]()
    assert panel.refresh()
    panel.cards[0][2].setPlainText(note)
    with pytest.raises(ValueError):
        panel.copy_result()
    assert not panel.close()
    assert panel.cards[0][2].toPlainText() == note
    panel.discard()
    assert panel._deleted


def test_pad_displays_literal_ampersand_but_copies_exact_name(host: Any) -> None:
    host.rows = (("A&B", "", ""),)
    panel = load(TITLES[3])["main"]()
    assert panel.refresh()
    tile = panel.canvas._items[0]
    assert tile.text() == "A&&B"
    tile.clicked.emit(False)
    panel.copy_result()
    assert host.copied == "/A&B"


def test_feature_draft_accepts_development_names_and_rejects_injection() -> None:
    draft = load(TITLES[1])["feature_draft"]
    assert draft((("A-B", "A-B.alt"),)).endswith(r"sub \A-B by \A-B.alt;")
    for name in ("A;", "A]", "A#", "A" * 64, "2cents", "Aé"):
        with pytest.raises(ValueError):
            draft(((name, "A.alt"),))


@pytest.mark.parametrize("title", TITLES + (MARK_TITLE,))
def test_source_attribution_hashes_match_preserved_read_only_bytes(title: str) -> None:
    preserved = Path(os.environ["FONTLAB_PRESERVED_ROOT"])
    text = (ROOT / "Scripts/Graphics" / f"{title}.py").read_text()
    sources = re.findall(r"Source: ([^\n]+)\nSHA256: ([0-9a-f]{64})", text)
    assert len(sources) == 2, (
        "Each delivered family must identify both archived variants."
    )
    for path, expected in sources:
        assert hashlib.sha256((preserved / path).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize("title", TITLES)
def test_actions_route_through_owned_signals(title: str, host: Any) -> None:
    panel = load(title)["main"]()
    refresh = next(
        button for button in panel.toolbar._items if button.text() == "Refresh"
    )
    copy = next(
        button for button in panel.toolbar._items if button.text() == "Copy Result"
    )
    refresh.clicked.emit(False)
    assert panel.result
    copy.clicked.emit(False)
    assert host.copied
    host.error = TimeoutError("Capture deadline")
    refresh.clicked.emit(False)
    assert panel.result == ""
    assert "Capture deadline" in panel.message.text()


@pytest.mark.parametrize("title", TITLES)
def test_parent_destruction_releases_owned_callbacks(title: str, host: Any) -> None:
    panel = load(title)["main"]()
    assert panel.refresh()
    panel.destroyed.emit()
    assert panel.scope.dead and panel.terminal.dead
    assert not panel.scope.records
    if title == TITLES[3]:
        assert panel.page_scope.dead


@pytest.mark.parametrize("title", TITLES)
def test_real_catalog_double_read_and_font_master_fences(
    title: str, host: Any, monkeypatch: Any
) -> None:
    native = importlib.import_module("fontlabapp._glyph_catalog_native")
    public = importlib.import_module("fontlabapp.glyph_catalog")
    reads = SimpleNamespace(count=0, drift=False)
    package = SimpleNamespace(id=12, fgId=13, isNull=False, master="Regular")
    mapped = SimpleNamespace(
        id=100,
        fgGlyphId=1,
        name="A",
        package=package,
        isNull=False,
        isValid=True,
        lastModified=SimpleNamespace(isValid=False),
    )
    package.findFgId = lambda identity: mapped
    font = SimpleNamespace(
        id=13, glyphs=(SimpleNamespace(id=1, name="A", unicodes=[65]),)
    )
    workspace = SimpleNamespace(currentPackage=package)

    def current_font() -> Any:
        reads.count += 1
        if reads.drift and reads.count == 2:
            package.master = "Bold"
        return font

    monkeypatch.setattr(
        native,
        "_native",
        lambda name: SimpleNamespace(
            CurrentFont=current_font,
            flWorkspace=SimpleNamespace(instance=lambda: workspace),
        ),
    )
    monkeypatch.setitem(sys.modules, "fly.ap.glyph_catalog", public)
    read = load(title)["capture_names"]
    assert read() == ("A",)
    assert reads.count == 3
    reads.count, reads.drift = 0, True
    with pytest.raises(ValueError, match="changed"):
        read()
    workspace.currentPackage = None
    with pytest.raises(ValueError, match="Open a font"):
        read()


@pytest.mark.parametrize("title", TITLES)
def test_empty_font_refresh_never_publishes_partial_output(
    title: str, host: Any
) -> None:
    host.rows = ()
    panel = load(title)["main"]()
    assert not panel.refresh()
    assert panel.result == "" and not panel.canvas._items


@pytest.mark.parametrize("title", TITLES)
def test_capture_adapter_honours_expired_budget(title: str, host: Any) -> None:
    module = load(title)
    reader = module["capture_names"]
    times = iter((0.0, 3.0))
    reader.__globals__["monotonic"] = lambda: next(times)
    with pytest.raises(TimeoutError):
        reader()


def test_real_app_names_exist_without_native_import(monkeypatch: Any) -> None:
    monkeypatch.syspath_prepend(str(ROOT.parent / "fontlab-fontlabapp/src"))
    assert callable(importlib.import_module("fontlabapp.glyph_catalog").capture)
    assert callable(importlib.import_module("fontlabapp.scripting").show_script_dialog)
    assert callable(importlib.import_module("fontlabapp.draft_signals").Scope)
    assert callable(importlib.import_module("fontlabapp.qt_properties").value)
    assert callable(importlib.import_module("fontlabapp.history").commit)
    assert callable(importlib.import_module("fontlabapp.history").scan_auto_facts)
    assert issubclass(
        importlib.import_module("fontlabapp.history").PartialWriteError, RuntimeError
    )
    assert callable(importlib.import_module("fontlabapp.scripting").current_package)


def test_mark_palette_mapping_and_rejects_unknown_colours() -> None:
    module = load(MARK_TITLE)
    assert [row[1] for row in module["SWATCHES"]] == [0, 1, 61, 121, 181, 241, 301]
    assert module["mark_from_colour"](-1, 0, 0) == 0
    for hue, mark in ((0, 1), (60, 61), (120, 121), (180, 181), (240, 241), (300, 301)):
        assert module["mark_from_colour"](hue, 255, 255) == mark
    for colour in ((12, 255, 255), (0, 10, 255), (0, 255, 128)):
        with pytest.raises(ValueError):
            module["mark_from_colour"](*colour)


@pytest.fixture
def mark_host(host: Any, monkeypatch: Any) -> Any:
    history = importlib.import_module("fontlabapp.history")
    guards = importlib.import_module("fontlabapp.edit_guards")
    state = SimpleNamespace(
        events=[],
        auto=False,
        mode="normal",
        available=True,
        settled=True,
        propagate=True,
    )
    host.rows = (("A", "U+0041", ""),)
    state.host = host
    package = SimpleNamespace(id=12, fgId=13, master="Regular", isNull=False)

    class Layer:
        def __init__(self, identity: int, mark: int) -> None:
            self.id, self.mark = identity, mark
            self.name, self.isNull, self.autoLayer = "Regular", False, False

        def checkInitHistoryState(self, flag: int) -> None:
            state.events.append(("history", self.id, flag))

    layers = [Layer(31, 1), Layer(32, 241)]

    class Glyph:
        id, name, isNull, isValid = 21, "A", False, True

        def __init__(self) -> None:
            self._mark = 1
            self.package, self.layers = package, layers

        @property
        def mark(self) -> int | None:
            if state.mode == "drift":
                self._mark += 1
            return self._mark

        @mark.setter
        def mark(self, mark: int) -> None:
            if state.mode == "ignore":
                return
            before = self._mark
            self._mark = mark
            for layer in self.layers:
                if state.propagate and int(layer.mark or 0) == int(before or 0):
                    layer.mark = mark
            if state.mode == "overwrite_override":
                self.layers[1].mark = mark
            elif state.mode == "corrupt_shared":
                self.layers[0].mark = 61
            state.events.append(("mark", mark))
            if state.mode == "partial":
                raise RuntimeError("Setter failed after changing a mark")

        def checkInitHistoryState(self, flag: int) -> None:
            state.events.append(("history", self.id, flag))

    glyph = Glyph()
    package.findName = lambda name: glyph if name == "A" else None
    state.package, state.glyph, state.layers, state.history = (
        package,
        glyph,
        layers,
        history,
    )
    scripting = sys.modules["fly.ap.scripting"]
    scripting.current_package = lambda: package if state.available else None
    native = SimpleNamespace(
        flItems=lambda: SimpleNamespace(
            notifyChangesApplied=lambda title, objects: state.events.append(
                ("notify", title, objects)
            )
        )
    )
    monkeypatch.setattr(
        history,
        "_native",
        lambda name: (
            native
            if name == "fontlab"
            else SimpleNamespace(
                QtCore=SimpleNamespace(
                    QDateTime=SimpleNamespace(currentDateTimeUtc=lambda: "stamp")
                )
            )
        ),
    )

    def settled(native: Any) -> None:
        if not state.settled:
            raise ValueError("Queued glyph updates; wait before writing")

    monkeypatch.setattr(guards, "require_settled", settled)
    monkeypatch.setattr(
        history,
        "scan_auto_facts",
        lambda package: history.auto_facts((("A", state.auto, ()),)),
    )
    monkeypatch.setitem(sys.modules, "fly.ap.history", history)
    return state


@pytest.mark.parametrize("propagate", (True, False))
def test_mark_drop_uses_real_metadata_commit_and_one_combined_notification(
    mark_host: Any,
    propagate: bool,
) -> None:
    mark_host.propagate = propagate
    apply = load(MARK_TITLE)["apply_mark"]
    assert apply((12, 13, "Regular"), 21, "A", 121)
    events = mark_host.events
    assert events[:3] == [("history", 31, 0), ("history", 32, 0), ("history", 21, 0)]
    notifications = [event for event in events if event[0] == "notify"]
    assert len(notifications) == 1
    assert notifications[0][2] == [*mark_host.layers, mark_host.glyph]
    assert mark_host.glyph.mark == 121
    assert [layer.mark for layer in mark_host.layers] == [
        121 if propagate else 1,
        241,
    ], "Keep individually coloured layer overrides."


@pytest.mark.parametrize(
    "refusal", ("auto", "auto_layer", "font", "master", "glyph", "mark", "queued")
)
def test_mark_refuses_before_history(refusal: str, mark_host: Any) -> None:
    context, identity, mark = (12, 13, "Regular"), 21, 121
    if refusal == "auto":
        mark_host.auto = True
    elif refusal == "auto_layer":
        mark_host.layers[0].autoLayer = True
    elif refusal == "font":
        mark_host.available = False
    elif refusal == "master":
        mark_host.package.master = "Bold"
    elif refusal == "glyph":
        identity = 99
    elif refusal == "mark":
        mark = 2
    else:
        mark_host.settled = False
    with pytest.raises(ValueError):
        load(MARK_TITLE)["apply_mark"](context, identity, "A", mark)
    assert not mark_host.events, "Refusal must precede history and mark mutation."


@pytest.mark.parametrize(
    "mode", ("partial", "ignore", "overwrite_override", "corrupt_shared")
)
def test_mark_partial_write_and_readback_mismatch_show_undo_hint(
    mode: str, mark_host: Any
) -> None:
    mark_host.mode = mode
    with pytest.raises(
        RuntimeError, match="Native changes may remain; use Edit > Undo"
    ):
        load(MARK_TITLE)["apply_mark"]((12, 13, "Regular"), 21, "A", 121)
    assert len([event for event in mark_host.events if event[0] == "notify"]) == 1


def test_mark_same_colour_is_a_noop(mark_host: Any) -> None:
    assert not load(MARK_TITLE)["apply_mark"]((12, 13, "Regular"), 21, "A", 1)
    assert not mark_host.events


def drop_event(css: str | None = "#00ff00") -> Any:
    mime = Mime()
    if css is not None:
        mime.setColorData(Colour(css))
    event = SimpleNamespace(accepted=None, action=None)
    event.mimeData = lambda: mime
    event.accept = lambda: setattr(event, "accepted", True)
    event.ignore = lambda: setattr(event, "accepted", False)
    event.setDropAction = lambda action: setattr(event, "action", action)
    return event


def test_mark_panel_executes_colour_drop_then_safe_close(mark_host: Any) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()
    tile = panel.canvas._items[0]
    event = drop_event()
    tile.dragEnterEvent(event)
    assert event.accepted
    tile.dropEvent(event)
    assert event.accepted and mark_host.glyph.mark == 121
    assert "one Edit > Undo" in panel.message.text()
    records = [*panel.scope.records, *panel.terminal.records]
    assert panel.close()
    assert all(not signal.slots for signal, _, _ in records)


@pytest.mark.parametrize(
    "mode", ("auto", "partial", "ignore", "font", "missing_colour")
)
def test_mark_drop_refusals_and_partial_writes_stay_in_status(
    mode: str, mark_host: Any
) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()
    tile = panel.canvas._items[0]
    if mode == "auto":
        mark_host.auto = True
    elif mode in ("partial", "ignore"):
        mark_host.mode = mode
    elif mode == "font":
        mark_host.available = False
    event = drop_event(None if mode == "missing_colour" else "#00ff00")
    tile.dropEvent(event)
    assert not event.accepted
    assert panel.valid is (mode not in ("partial", "ignore"))
    assert panel.message.text()
    if mode in ("partial", "ignore"):
        assert "Native changes may remain; use Edit > Undo" in panel.message.text()
    elif mode == "auto":
        assert "has auto layers" in panel.message.text()


@pytest.mark.parametrize("propagate", (True, False))
def test_unset_glyph_and_layer_marks_read_as_zero(
    propagate: bool, mark_host: Any
) -> None:
    mark_host.propagate = propagate
    mark_host.glyph._mark = None
    mark_host.layers[0].mark = None
    module = load(MARK_TITLE)
    assert module["board_snapshot"]("")[1] == (("A", 21, 0),)
    panel = module["main"]()
    assert panel.refresh()
    event = drop_event()
    panel.canvas._items[0].dropEvent(event)
    assert event.accepted and panel.valid
    assert mark_host.glyph.mark == 121
    assert mark_host.layers[0].mark == (121 if propagate else None)
    assert mark_host.layers[1].mark == 241


def test_timeout_drop_slot_reports_pre_history_refusal_without_invalidating(
    mark_host: Any,
    monkeypatch: Any,
) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()

    def expired(package: Any) -> Any:
        raise TimeoutError("Mark scan expired")

    monkeypatch.setattr(mark_host.history, "scan_auto_facts", expired)
    event = drop_event()
    panel.canvas._items[0].dropEvent(event)
    assert event.accepted is False and panel.valid
    assert "Mark scan expired" in panel.message.text()
    assert not mark_host.events


def test_auto_refusal_allows_next_drop_without_refresh(mark_host: Any) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()
    tile = panel.canvas._items[0]
    mark_host.auto = True
    tile.dropEvent(drop_event())
    assert panel.valid
    mark_host.auto = False
    event = drop_event()
    tile.dropEvent(event)
    assert event.accepted and mark_host.glyph.mark == 121


def test_native_base_event_paths_and_drag_move_acceptance(mark_host: Any) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()
    swatch = panel.swatches[1]
    swatch.mousePressEvent(SimpleNamespace(button=lambda: -1))
    assert swatch._base_events == ["mousePressEvent"]
    tile = panel.canvas._items[0]
    event = drop_event()
    tile.dragMoveEvent(event)
    assert event.accepted and not tile._base_events
    tile.dragLeaveEvent(event)
    for handler in (tile.dragEnterEvent, tile.dragMoveEvent, tile.dropEvent):
        rejected = drop_event(None)
        handler(rejected)
        assert rejected.accepted is False
    assert tile._base_events == [
        "dragLeaveEvent",
        "dragEnterEvent",
        "dragMoveEvent",
        "dropEvent",
    ]
    assert panel.valid and not mark_host.events


def test_colour_drag_blocks_refresh_and_close_until_native_drag_returns(
    mark_host: Any,
) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()

    def while_dragging(drag: Any) -> None:
        assert panel.busy
        assert not panel.refresh() and not panel.close()
        assert not panel._deleted
        assert drag._mime.hasColor()
        panel.canvas._items[0].dropEvent(drop_event("#ff0000"))

    mark_host.host.drag_hook = while_dragging
    panel.swatches[1].mousePressEvent(
        SimpleNamespace(button=lambda: mark_host.host.core.Qt.LeftButton)
    )
    assert not panel.busy
    assert panel.close()


def test_mark_board_close_disconnect_failure_and_external_destruction(
    mark_host: Any,
) -> None:
    panel = load(MARK_TITLE)["main"]()
    assert panel.refresh()
    signal = panel.scope.records[0][0]
    signal.fail = True
    assert not panel.close() and not panel._deleted
    signal.fail = False
    assert panel.close()
    panel = load(MARK_TITLE)["main"]()
    panel.destroyed.emit()
    assert panel.scope.dead and panel.terminal.dead


def test_mark_board_capture_errors_and_changed_marks_refuse(
    mark_host: Any, monkeypatch: Any
) -> None:
    module = load(MARK_TITLE)
    assert module["board_snapshot"]("") == ((12, 13, "Regular"), (("A", 21, 1),))
    with pytest.raises(ValueError, match="prefix"):
        module["board_snapshot"]("Missing")
    mark_host.mode = "drift"
    with pytest.raises(ValueError, match="changed"):
        module["board_snapshot"]("")
    mark_host.mode = "normal"
    panel = module["main"]()
    mark_host.host.error = TimeoutError("Capture expired")
    assert not panel.refresh()
    assert not panel.valid and not panel.canvas._items
    assert "Capture expired" in panel.message.text()


def test_spacing_capture_returns_current_master_advance_and_geometric_margins(
    host: Any,
) -> None:
    module = load(TITLES[0])
    assert module["capture_spacing"](("A", "A.alt")) == (
        ("A", 500.0, 40.0, 50.0),
        ("A.alt", 250.0, 10.0, 20.0),
    )
    panel = module["main"]()
    panel.prefix_entry.setText("A")
    assert panel.refresh()
    container = panel.canvas._items[-1]
    anchors = container._items[0]
    first_proxy = anchors._items[0][2]
    second_proxy = anchors._items[3][2]
    assert first_proxy._preferred_size == (600.0, 120.0)
    assert second_proxy._preferred_size == (300.0, 120.0)
    assert "Advance 500" in panel.canvas._items[0].text()
    assert "LSB 40  RSB 50" in panel.canvas._items[0].text()


@pytest.mark.parametrize("drift", ("master", "width"))
def test_spacing_capture_refuses_changed_master_or_measurements(
    drift: str, host: Any
) -> None:
    def change() -> None:
        if host.layer_reads == 2:
            if drift == "master":
                host.package.master = "Bold"
            else:
                host.metrics["A"] = (510.0, 40.0, 50.0)

    host.layer_hook = change
    with pytest.raises(ValueError, match="changed"):
        load(TITLES[0])["capture_spacing"](("A",))


@pytest.mark.parametrize("title", TITLES[:2] + TITLES[3:] + (MARK_TITLE,))
def test_readonly_and_mark_tools_have_no_review_lifecycle_messages(title: str) -> None:
    text = (ROOT / "Scripts/Graphics" / f"{title}.py").read_text()
    assert "saved_review" not in text and "has_draft" not in text
    assert "Unsaved review" not in text and "edits stay local" not in text
    assert "feature-parity claim" not in text and "BSD/GPL" not in text


def test_mark_panel_class_attributes_avoid_native_widget_members(
    mark_host: Any,
) -> None:
    cls = load(MARK_TITLE)["panel_type"](sys.modules["fly"].qt)
    assert not {
        "render",
        "update",
        "layout",
        "font",
        "size",
        "close",
        "scroll",
        "move",
    }.intersection(vars(cls))


def test_proportional_spacing_has_exact_ratios_and_zero_width() -> None:
    widths = load(TITLES[0])["strip_widths"]
    assert widths((500.0, 250.0, 0.0), 900.0) == (600.0, 300.0, 0.0)
    for advances in ((0.0,), (-1.0,), (float("nan"),), (float("inf"),)):
        with pytest.raises(ValueError):
            widths(advances, 900.0)


@pytest.mark.parametrize("title", TITLES)
def test_panel_class_attributes_avoid_native_widget_members(
    title: str, host: Any
) -> None:
    panel_class = load(title)["panel_type"](sys.modules["fly"].qt)
    native = {
        "render",
        "update",
        "layout",
        "font",
        "size",
        "close",
        "scroll",
        "move",
        "resize",
        "setParent",
        "geometry",
        "windowTitle",
        "children",
    }
    assert not native.intersection(vars(panel_class)), (
        f"{title} shadows a native QWidget member"
    )
    assert "draw_scene" in vars(panel_class)


def test_graph_keeps_full_draft_but_bounds_scene(host: Any) -> None:
    host.rows = tuple(
        (name, "", "") for i in range(150) for name in (f"g{i}", f"g{i}.alt")
    )
    panel = load(TITLES[1])["main"]()
    assert panel.refresh()
    assert panel.result.count("\nsub ") == 150
    assert len(panel.canvas._items) == 500
    assert "First 100 of 150" in panel.message.text()


def test_pad_filters_before_paging_and_uses_explicit_shortcuts(host: Any) -> None:
    host.rows = tuple((f"g{i}", "", "") for i in range(30))
    panel = load(TITLES[3])["main"]()
    panel.prefix_entry.setText("g2")
    assert panel.refresh()
    assert panel.names == ("g2", *(f"g{i}" for i in range(20, 30)))
    panel.navigate(1)
    assert panel.result == "/g28/g29"
    source = (ROOT / "Scripts/Graphics/Glyph Proof Pad.py").read_text()
    assert 'gui.QKeySequence("Alt+Left")' in source
    assert 'gui.QKeySequence("Alt+Right")' in source


def test_discard_failed_close_retains_review_cards_and_copy(host: Any) -> None:
    panel = load(TITLES[2])["main"]()
    assert panel.refresh()
    panel.cards[0][2].setPlainText("Keep on failed Close")
    signal = panel.scope.records[0][0]
    signal.fail = True
    panel.discard()
    assert not panel._deleted
    assert "Keep on failed Close" in panel.copy_payload()
    panel.copy_result()
    assert "Keep on failed Close" in host.copied
    signal.fail = False
    panel.discard()
    assert panel._deleted


@pytest.mark.parametrize("title", TITLES + (MARK_TITLE,))
def test_public_source_has_python311_contracts_and_no_font_writes(title: str) -> None:
    path = ROOT / "Scripts/Graphics" / f"{title}.py"
    text = path.read_text()
    tree = ast.parse(text, feature_version=(3, 11))
    doc = ast.get_docstring(tree)
    assert all(
        label in doc
        for label in ("What:", "How:", "Why:", "Usage:", "Benefit:", "Apache-2.0")
    )
    assert "# this_file: " + str(path.relative_to(ROOT)) in text
    assert all(
        term not in text
        for term in (
            "notifyChangesApplied",
            "UpdateAll",
            "QApplication(",
            "_component_graph_native",
            "issue 122",
            "E4",
        )
    )
    if title != MARK_TITLE:
        assert "history.commit" not in text
    else:
        assert "import fly.ap.history as history" in text
        assert 'operation="metadata"' in text
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assert node.returns is not None, node.name
            assert all(
                arg.annotation is not None
                for arg in node.args.args
                if arg.arg not in ("self", "cls")
            ), node.name
