# this_file: tests/test_issue122_E8.py
"""E8 independent drag/drop rewrites. Offline doubles; no native acceptance."""

from __future__ import annotations

import ast
import json
import runpy
from pathlib import Path
from types import SimpleNamespace as NS
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
TITLES = (
    "Deferred Glyph Report Drag",
    "Font File Drop Shelf",
    "Draggable Glyph Names",
    "Font Drop Inspector",
    "Proof Word Magnets",
    "Glyph Pair Board",
)


def load(title: str) -> dict[str, Any]:
    return runpy.run_path(str(ROOT / "Scripts/Drag And Drop" / (title + ".py")))


@pytest.fixture
def facts() -> Any:
    return NS(
        context=(1, 7, "Regular"),
        rows=(
            NS(name="A", unicodes=(65,)),
            NS(name="A.alt", unicodes=(65,)),
            NS(name="V", unicodes=(86,)),
            NS(name="smile", unicodes=(0x1F600,)),
            NS(name="part", unicodes=()),
        ),
    )


@pytest.mark.parametrize("title", TITLES)
def test_new_scripts_import_lazily_and_use_shared_fly(title: str) -> None:
    code = (ROOT / "Scripts/Drag And Drop" / (title + ".py")).read_text()
    tree = ast.parse(code, feature_version=(3, 11))
    assert "this_file: Scripts/Drag And Drop/" + title in code
    assert "behaviour-only" in ast.get_docstring(tree)
    assert callable(load(title)["panel_type"])


def test_deferred_encoder_is_lazy_cached_and_exact(facts: Any) -> None:
    module = load(TITLES[0])
    calls = []
    report = module["LazyReport"](facts, lambda rows: calls.append(rows) or "encoded")
    assert calls == []
    assert report.get() == report.get() == "encoded"
    assert len(calls) == 1
    data = json.loads(module["encode_report"](facts.rows))
    assert data["glyphs"][3] == {"name": "smile", "unicodes": [128512]}
    assert data["glyphs"][4]["unicodes"] == []


def test_shelf_paths_are_local_existing_and_deduplicated(tmp_path: Path) -> None:
    parse = load(TITLES[1])["font_paths"]
    font = tmp_path / "My Font.OTF"
    font.write_bytes(b"font")
    ufo = tmp_path / "Source.ufo"
    ufo.mkdir()
    (ufo / "metainfo.plist").write_text("fixture")
    assert parse([str(font), str(ufo), str(font)]) == (str(font), str(ufo))
    for bad in (
        [],
        [str(tmp_path / "absent.ttf")],
        ["https://host/a.ttf"],
        [str(tmp_path)],
        [str(tmp_path / "bad.ufo")],
    ):
        with pytest.raises(ValueError):
            parse(bad)
    with pytest.raises(ValueError):
        parse([str(font), str(tmp_path / "missing.ttf")])


def test_glyph_tokens_keep_order_suffixes_and_unencoded_names(facts: Any) -> None:
    make = load(TITLES[2])["glyph_tokens"]
    assert make(facts) == ("/A", "/A.alt", "/V", "/smile", "/part")
    with pytest.raises(ValueError, match="Open a font"):
        make(None)
    assert make(NS(rows=())) == ()


def test_inspector_reports_all_coverage_matches_and_occurrences(facts: Any) -> None:
    report = load(TITLES[3])["coverage_report"]
    assert report(facts, "AA😀?") == (
        "1: U+0041 → A, A.alt\n2: U+0041 → A, A.alt\n"
        "3: U+1F600 → smile\n4: U+003F → MISSING"
    )
    assert report(facts, "") == "No text received."
    with pytest.raises(ValueError, match="Open a font"):
        report(None, "A")
    with pytest.raises(ValueError, match="Unicode"):
        report(facts, "\ud800")


def test_magnets_keep_repeated_words_and_report_missing(facts: Any) -> None:
    module = load(TITLES[4])
    assert module["words"]("AV  AV\n😀") == ("AV", "AV", "😀")
    assert module["words"]("") == ()
    assert module["missing_characters"](facts, "AV?😀?") == ("U+003F",)
    with pytest.raises(ValueError, match="Unicode"):
        module["words"]("\udfff")


def test_pair_board_preserves_occurrences_and_names(facts: Any) -> None:
    module = load(TITLES[5])
    assert module["resolve_tokens"](facts, "/A /part /A.alt /A") == (
        "A",
        "part",
        "A.alt",
        "A",
    )
    assert module["pair_lines"](("A", "V", "A")) == "/A/V\n/V/A"
    assert module["pair_lines"](("A",)) == ""
    with pytest.raises(ValueError, match="Unknown glyph"):
        module["resolve_tokens"](facts, "/absent")
    with pytest.raises(ValueError, match="slash"):
        module["resolve_tokens"](facts, "AV")
    with pytest.raises(ValueError, match="Open a font"):
        module["resolve_tokens"](None, "/A")


class Signal:
    def __init__(self) -> None:
        self.slots: list[Any] = []

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


class Widget:
    """Only the Qt methods used by these panels; unknown API access fails."""

    def __setattr__(self, name: str, val: Any) -> None:
        native = {
            "size",
            "text",
            "font",
            "name",
            "width",
            "height",
            "layout",
            "parent",
            "children",
            "plainText",
            "windowTitle",
        }
        if type(self) is not Widget and name in native:
            raise AttributeError(f"Native QWidget member cannot be overwritten: {name}")
        object.__setattr__(self, name, val)

    @property
    def text(self) -> str:
        return self._text

    @property
    def plainText(self) -> str:
        return self._plain_text

    @property
    def children(self) -> list[Any]:
        return self._children

    def __init__(self, *args: Any) -> None:
        self._text = args[0] if args and isinstance(args[0], str) else ""
        self._plain_text = ""
        self.destroyed, self.clicked = Signal(), Signal()
        self.deleted = False
        self._children: list[Any] = []
        for arg in args:
            if isinstance(arg, Widget):
                arg.children.append(self)

    def setWindowTitle(self, text: str) -> None:
        self.title = text

    def setAttribute(self, *args: Any) -> None:
        pass

    def resize(self, *args: Any) -> None:
        pass

    def setTextFormat(self, *args: Any) -> None:
        pass

    def setWordWrap(self, *args: Any) -> None:
        pass

    def setPlaceholderText(self, *args: Any) -> None:
        pass

    def setAcceptDrops(self, *args: Any) -> None:
        pass

    def setDragEnabled(self, *args: Any) -> None:
        pass

    def setSelectionMode(self, *args: Any) -> None:
        pass

    def setDragDropMode(self, *args: Any) -> None:
        pass

    def setReadOnly(self, *args: Any) -> None:
        pass

    def setStyleSheet(self, *args: Any) -> None:
        pass

    def setText(self, text: str) -> None:
        self._text = text

    def setPlainText(self, text: str) -> None:
        self._plain_text = text

    def clear(self) -> None:
        self._text = self._plain_text = ""

    def deleteLater(self) -> None:
        self.deleted = True


class Layout:
    def __init__(self, *args: Any) -> None:
        pass

    def setContentsMargins(self, *args: Any) -> None:
        pass

    def addWidget(self, *args: Any) -> None:
        pass

    def addLayout(self, *args: Any) -> None:
        pass


class ItemList(Widget):
    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.rows: list[Any] = []
        self.selected: list[int] = []

    @property
    def count(self) -> int:
        return len(self.rows)

    def addItem(self, text: str) -> None:
        self.rows.append(NS(text=text))

    def addItems(self, texts: Any) -> None:
        for text in texts:
            self.addItem(text)

    def clear(self) -> None:
        self.rows.clear()
        self.selected.clear()

    def row(self, item: Any) -> int:
        return self.rows.index(item)

    def takeItem(self, index: int) -> Any:
        self.selected = []
        return self.rows.pop(index)

    def item(self, index: int) -> Any:
        return self.rows[index]

    def selectedItems(self) -> list[Any]:
        return [self.rows[i] for i in self.selected]

    def startDrag(self, actions: Any) -> None:
        self.rows.reverse()

    def dropEvent(self, event: Any) -> None:
        event.accept()

    def dragEnterEvent(self, event: Any) -> None:
        event.accept()

    def dragMoveEvent(self, event: Any) -> None:
        event.accept()


class Mime:
    def __init__(self) -> None:
        self.payload, self.links = "", []

    def setText(self, text: str) -> None:
        self.payload = text

    def setUrls(self, urls: list[Any]) -> None:
        self.links = urls

    def text(self) -> str:
        return self.payload

    def hasText(self) -> bool:
        return bool(self.payload)

    def hasUrls(self) -> bool:
        return bool(self.links)

    def urls(self) -> list[Any]:
        return self.links

    def formats(self) -> list[str]:
        return (["text/plain"] if self.payload else []) + (
            ["text/uri-list"] if self.links else []
        )


class Url:
    def __init__(self, path: str, local: bool = True) -> None:
        self.path, self.local = path, local

    def isLocalFile(self) -> bool:
        return self.local

    def toLocalFile(self) -> str:
        return self.path

    def toString(self) -> str:
        return self.path

    @staticmethod
    def fromLocalFile(path: str) -> Any:
        return Url(path)


class Event:
    def __init__(self, mime: Any = None, source: Any = None) -> None:
        self.mime, self.sender = mime, source
        self.accepted = self.ignored = False

    def mimeData(self) -> Any:
        return self.mime

    def source(self) -> Any:
        return self.sender

    def accept(self) -> None:
        self.accepted = True

    def ignore(self) -> None:
        self.ignored = True

    def setDropAction(self, action: Any) -> None:
        self.action = action


@pytest.fixture
def runtime(monkeypatch: Any) -> Any:
    """Inject Fly boundaries; Scope double records exact connected slot pairs."""
    import sys
    from types import ModuleType

    class Scope:
        def __init__(self, failure: Any) -> None:
            self.pairs: list[Any] = []
            self.failure, self.refuse = failure, False

        def connect(self, signal: Any, fn: Any) -> None:
            def guard(*args: Any) -> None:
                try:
                    fn(*args)
                except Exception as error:  # noqa: BLE001 - emulate App callback boundary
                    self.failure(error)

            signal.connect(guard)
            self.pairs.append((signal, guard))

        def finish(self, *, destroyed: bool = False) -> bool:
            if self.refuse:
                return False
            if not destroyed:
                for signal, fn in self.pairs:
                    signal.disconnect(fn)
            self.pairs.clear()
            return True

    for name in ("fly", "fly.ap", "fly.ap.draft_signals", "fly.ap.qt_properties"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    sys.modules["fly.ap.draft_signals"].Scope = Scope
    sys.modules["fly.ap.qt_properties"].value = lambda obj, key: (
        getattr(obj, key)() if callable(getattr(obj, key)) else getattr(obj, key)
    )
    drags: list[Any] = []
    clipboard = Widget()

    class Drag:
        def __init__(self, parent: Any) -> None:
            self.parent, self.deleted = parent, False
            drags.append(self)

        def setMimeData(self, mime: Any) -> None:
            self.mime = mime

        def exec(self, action: Any) -> None:
            event = Event()
            self.parent.closeEvent(event)
            assert event.ignored, "Panel must survive the nested drag event loop"

        def deleteLater(self) -> None:
            self.deleted = True

    qt = NS(
        QtGui=NS(
            QWidget=Widget,
            QLabel=Widget,
            QLineEdit=Widget,
            QPlainTextEdit=Widget,
            QPushButton=Widget,
            QListWidget=ItemList,
            QVBoxLayout=Layout,
            QHBoxLayout=Layout,
            QAbstractItemView=NS(ExtendedSelection=3, InternalMove=4),
            QDrag=Drag,
            QApplication=NS(clipboard=lambda: clipboard, startDragDistance=lambda: 10),
        ),
        QtCore=NS(
            Qt=NS(Window=1, PlainText=2, WA_QuitOnClose=3, CopyAction=4, LeftButton=1),
            QMimeData=Mime,
            QByteArray=bytes,
            QVariant=NS(String=10),
            QUrl=Url,
        ),
    )
    return NS(qt=qt, drags=drags, clipboard=clipboard)


@pytest.mark.parametrize("title", TITLES)
def test_panels_construct_close_disconnect_and_refuse_busy_close(
    title: str,
    facts: Any,
    runtime: Any,
    monkeypatch: Any,
) -> None:
    import sys

    mod = load(title)
    panel = mod["panel_type"](runtime.qt, lambda: facts)()
    registry = {mod["KEY"]: panel}
    monkeypatch.setattr(sys, "_fontlab_samples", registry, raising=False)
    assert panel.title == title and panel.scope.pairs
    panel.busy = True
    busy = Event()
    panel.closeEvent(busy)
    assert busy.ignored and not panel.deleted
    panel.busy = False
    panel.scope.refuse = True
    refused = Event()
    panel.closeEvent(refused)
    assert refused.ignored and not panel.deleted
    panel.scope.refuse = False
    pairs = list(panel.scope.pairs) + list(panel.terminal.pairs)
    closed = Event()
    panel.closeEvent(closed)
    assert closed.accepted and panel.deleted and not registry
    assert all(not signal.slots for signal, _ in pairs), "Disconnect before Qt deletion"


@pytest.mark.parametrize("title", [title for title in TITLES if title != TITLES[1]])
def test_capture_failure_is_visible_and_clears_font_facts(
    title: str, runtime: Any
) -> None:
    def absent() -> None:
        raise ValueError("Open a font first")

    panel = load(title)["panel_type"](runtime.qt, absent)()
    assert panel.facts is None and "Open a font" in panel.status.text
    if title in (TITLES[0], TITLES[2], TITLES[5]):
        assert panel.text_items() == () and panel.output.plainText == ""


def test_deferred_mime_retrieval_is_on_demand(facts: Any, runtime: Any) -> None:
    mod = load(TITLES[0])
    count: list[Any] = []
    report = mod["LazyReport"](facts, lambda rows: count.append(rows) or "{}")
    mime = mod["deferred_mime"](runtime.qt.QtCore, report)
    assert mime.formats() == ["application/json", "text/plain"] and not count
    assert mime.hasFormat("application/json") and not mime.hasFormat("image/png")
    assert mime.retrieveData("application/json", 12) == b"{}"
    assert mime.retrieveData("text/plain", 10) == "A\nA.alt\nV\nsmile\npart"
    assert mime.retrieveData("unknown", 12) == b"" and len(count) == 1


def test_names_drag_contains_only_selected_tokens(facts: Any, runtime: Any) -> None:
    panel = load(TITLES[2])["panel_type"](runtime.qt, lambda: facts)()
    panel.items.selected = [1, 4]
    panel.items.startDrag(0)
    assert runtime.drags[-1].mime.text() == "/A.alt/part"
    assert runtime.drags[-1].deleted and not panel.busy
    panel.entry.setText("ALT")
    panel.use_input()
    assert panel.text_items() == ("/A.alt",)
    panel.items.selected = []
    panel.drag_output()
    assert "select glyph" in panel.status.text


def test_shelf_drop_is_atomic_and_exports_urls(
    tmp_path: Path, facts: Any, runtime: Any
) -> None:
    panel = load(TITLES[1])["panel_type"](runtime.qt, lambda: facts)()
    font = tmp_path / "a.ttf"
    font.write_bytes(b"owned")
    mime = Mime()
    mime.setUrls([Url(str(font)), Url(str(tmp_path / "missing.otf"))])
    event = Event(mime)
    panel.items.dropEvent(event)
    assert event.ignored and panel.text_items() == ()
    mime.setUrls([Url(str(font)), Url(str(font))])
    event = Event(mime)
    panel.items.dropEvent(event)
    assert event.accepted and panel.text_items() == (str(font),)
    panel.items.selected = [0]
    panel.items.startDrag(0)
    assert runtime.drags[-1].mime.urls()[0].toLocalFile() == str(font)
    mime.setUrls([Url("https://example.org/a.ttf", False)])
    event = Event(mime)
    panel.items.dropEvent(event)
    assert event.ignored and panel.text_items() == (str(font),)


def test_inspector_plain_text_urls_and_binary(facts: Any, runtime: Any) -> None:
    panel = load(TITLES[3])["panel_type"](runtime.qt, lambda: facts)()
    mime = Mime()
    mime.setText("A?")
    panel.items.dropEvent(Event(mime))
    assert "A, A.alt" in panel.output.plainText and "MISSING" in panel.output.plainText
    mime.setUrls([Url("/tmp/source.ufo")])
    panel.receive(mime)
    assert "/tmp/source.ufo" in panel.output.plainText
    mime = Mime()
    mime.formats = lambda: ["application/octet-stream"]
    event = Event(mime)
    panel.items.dragEnterEvent(event)
    assert event.accepted
    panel.items.dropEvent(event)
    assert "binary content was not decoded" in panel.output.plainText


@pytest.mark.parametrize(
    "title,text,expected",
    [
        (TITLES[4], "AV AV 😀", "😀 AV AV"),
        (TITLES[5], "/A/V/part", "/part/V\n/V/A"),
    ],
)
def test_reorder_proof_exports_actual_row_order(
    title: str,
    text: str,
    expected: str,
    facts: Any,
    runtime: Any,
) -> None:
    panel = load(title)["panel_type"](runtime.qt, lambda: facts)()
    panel.entry.setText(text)
    panel.use_input()
    panel.items.startDrag(0)
    assert panel.output.plainText == expected
    panel.drag_output()
    assert runtime.drags[-1].mime.text() == expected
    panel.copy_output()
    assert runtime.clipboard.text == expected
    panel.clear()
    assert panel.text_items() == () and panel.output.plainText == ""


def test_invalid_glyph_drop_changes_nothing(facts: Any, runtime: Any) -> None:
    panel = load(TITLES[5])["panel_type"](runtime.qt, lambda: facts)()
    mime = Mime()
    mime.setText("/A/absent")
    event = Event(mime)
    panel.items.dropEvent(event)
    assert (
        event.ignored
        and panel.text_items() == ()
        and "Unknown glyph" in panel.status.text
    )


@pytest.mark.parametrize("title", TITLES)
def test_main_uses_existing_app_capture_and_retained_window(
    title: str,
    facts: Any,
    runtime: Any,
    monkeypatch: Any,
) -> None:
    import sys
    from types import ModuleType

    calls: list[Any] = []
    sys.modules["fly"].qt = runtime.qt
    for name in ("fly.ap.character_map_capture", "fly.ap.scripting"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    sys.modules["fly.ap.character_map_capture"].capture = lambda: facts
    sys.modules["fly.ap.scripting"].show_script_dialog = lambda factory, key: (
        calls.append(key) or factory(None)
    )
    controls = ModuleType("fly.ap.controls")
    controls.FontLab = lambda: pytest.fail("Opening must remain lazy")
    monkeypatch.setitem(sys.modules, "fly.ap.controls", controls)
    panel = load(title)["main"]()
    assert panel.title == title and len(calls) == 1


@pytest.mark.parametrize("title", TITLES)
def test_parent_destruction_releases_registry_and_detached_facts(
    title: str,
    facts: Any,
    runtime: Any,
    monkeypatch: Any,
) -> None:
    import sys

    mod = load(title)
    panel = mod["panel_type"](runtime.qt, lambda: facts)()
    registry = {mod["KEY"]: panel}
    monkeypatch.setattr(sys, "_fontlab_samples", registry, raising=False)
    panel.destroyed.emit()
    assert registry == {} and getattr(panel, "facts", None) is None
    assert not panel.scope.pairs and not panel.terminal.pairs


@pytest.mark.parametrize("title", [TITLES[0], TITLES[2], TITLES[5]])
def test_failed_refresh_removes_previous_font_export(
    title: str,
    facts: Any,
    runtime: Any,
) -> None:
    responses = iter([facts, ValueError("Font closed")])

    def capture() -> Any:
        result = next(responses)
        if isinstance(result, Exception):
            raise result
        return result

    panel = load(title)["panel_type"](runtime.qt, capture)()
    panel.refresh()
    assert panel.facts is None and panel.text_items() == ()
    assert panel.output.plainText == "" and panel.status.text == "Font closed"
    panel.drag_output()
    assert runtime.drags == [], "Failed refresh must remove stale export data"


def test_words_still_accept_drop_without_a_font(runtime: Any) -> None:
    def capture() -> None:
        raise ValueError("Open a font")

    panel = load(TITLES[4])["panel_type"](runtime.qt, capture)()
    mime = Mime()
    mime.setText("proof proof")
    event = Event(mime)
    panel.items.dropEvent(event)
    assert event.accepted and not event.ignored
    assert panel.output.plainText == "proof proof"
    assert "Refresh" in panel.status.text


def test_drag_failure_releases_busy_state_and_owned_drag(
    facts: Any, runtime: Any
) -> None:
    panel = load(TITLES[2])["panel_type"](runtime.qt, lambda: facts)()
    panel.items.selected = [0]
    drag_type = runtime.qt.QtGui.QDrag

    def refused(drag: Any, action: Any) -> None:
        raise RuntimeError("Target refused drag")

    drag_type.exec = refused
    panel.drag_output()
    assert not panel.busy and runtime.drags[-1].deleted
    assert panel.status.text == "Target refused drag"


def test_scopes_route_button_errors_without_escape(facts: Any, runtime: Any) -> None:
    panel = load(TITLES[5])["panel_type"](runtime.qt, lambda: facts)()
    panel.entry.setText("/missing")
    button = next(child for child in panel.children if child.text == "Use input")
    button.clicked.emit(True)
    assert panel.text_items() == () and "Unknown glyph" in panel.status.text


def test_two_panels_do_not_route_drag_to_the_other_owner(
    facts: Any, runtime: Any
) -> None:
    kind = load(TITLES[2])["panel_type"](runtime.qt, lambda: facts)
    first, second = kind(), kind()
    first.items.selected = [0]
    second.items.selected = [1]
    first.items.startDrag(0)
    assert runtime.drags[-1].parent is first
    assert runtime.drags[-1].mime.text() == "/A"


@pytest.mark.parametrize(
    "member", ["size", "text", "font", "name", "width", "height", "layout"]
)
def test_widget_double_refuses_native_member_shadowing(member: str) -> None:
    class Child(Widget):
        pass

    with pytest.raises(AttributeError, match="Native QWidget"):
        setattr(Child(), member, "bad")


def test_shelf_has_no_capture_and_opens_only_selected_fonts(
    tmp_path: Path, runtime: Any
) -> None:
    opened = []
    panel = load(TITLES[1])["panel_type"](runtime.qt, opened.append)()
    assert not hasattr(panel, "facts") and not hasattr(panel, "refresh")
    assert "Refresh font" not in [child.text for child in panel.children]
    assert "font paths" in panel.status.text
    a, b = tmp_path / "a.ttf", tmp_path / "b.ufo"
    a.touch()
    b.mkdir()
    panel.add_paths([str(a), str(b)])
    panel.items.selected = [1]
    panel.open_selected()
    assert opened == [str(b)] and "Opened 1" in panel.status.text
    panel.items.selected = []
    panel.drag_output()
    assert panel.status.text == "Select rows to drag"
    with pytest.raises(ValueError, match="Select rows to open"):
        panel.open_selected()
    panel.items.selected = [0, 1]
    a.unlink()
    with pytest.raises(ValueError, match="existing supported"):
        panel.open_selected()
    assert opened == [str(b)], "Validate the whole selection before opening any path"


@pytest.mark.parametrize("title", [TITLES[0], TITLES[2]])
def test_source_panels_ignore_incoming_drags(
    title: str, facts: Any, runtime: Any
) -> None:
    panel = load(title)["panel_type"](runtime.qt, lambda: facts)()
    mime = Mime()
    mime.setText("A")
    event = Event(mime)
    panel.items.dragEnterEvent(event)
    assert event.ignored and not event.accepted
    if title == TITLES[0]:
        assert not hasattr(panel, "entry")
        assert "Use input" not in [child.text for child in panel.children]


@pytest.mark.parametrize(
    "title,text", [(TITLES[4], "AV AV smile"), (TITLES[5], "/A/V/part")]
)
def test_remove_selected_rows_and_input_clearing(
    title: str, text: str, facts: Any, runtime: Any
) -> None:
    panel = load(title)["panel_type"](runtime.qt, lambda: facts)()
    panel.entry.setText(text)
    panel.use_input()
    assert panel.entry.text == ""
    panel.items.selected = [1]
    panel.remove_selected()
    assert len(panel.text_items()) == 2 and "V" not in panel.text_items()
    if title == TITLES[4]:
        assert "Copy proof text" in [child.text for child in panel.children]


def test_coverage_limit_and_whitespace(facts: Any) -> None:
    report = load(TITLES[3])["coverage_report"]
    with pytest.raises(ValueError, match="5,000"):
        report(facts, "A" * 5001)
    assert len(report(facts, "A" * 5000).splitlines()) == 5000
    assert "MISSING" not in report(facts, "A \t\n")


@pytest.mark.parametrize("title", TITLES)
def test_drag_distance_uses_components_without_point_operators(
    title: str, facts: Any, runtime: Any
) -> None:
    panel = load(title)["panel_type"](runtime.qt, lambda: facts)()
    calls = []
    panel.drag_output = lambda: calls.append(True)

    class Point:
        def __init__(self, x: int, y: int) -> None:
            self.a, self.b = x, y

        def x(self) -> int:
            return self.a

        def y(self) -> int:
            return self.b

        def __sub__(self, other: Any) -> Any:
            pytest.fail("Do not use Qt wrapper arithmetic")

    panel.export.mousePressEvent(NS(pos=lambda: Point(20, 20), button=lambda: 1))
    panel.export.mouseMoveEvent(NS(pos=lambda: Point(11, 20), buttons=lambda: 1))
    assert calls == []
    panel.export.mouseMoveEvent(NS(pos=lambda: Point(10, 19), buttons=lambda: 1))
    assert calls == [True]


@pytest.mark.parametrize("title", TITLES)
def test_user_docs_and_public_methods_are_documented(title: str) -> None:
    tree = ast.parse((ROOT / "Scripts/Drag And Drop" / (title + ".py")).read_text())
    doc = ast.get_docstring(tree)
    assert "Apache-2.0 (own earlier work)" in doc
    assert not any(
        word in doc
        for word in (
            "App",
            "issue122",
            "D22",
            "SHA256",
            "rescued/",
            "GPL",
            "Native qualification",
            "Run:",
        )
    )
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef)):
            assert ast.get_docstring(node), f"Missing docstring: {node.name}"
    assert load(title)["KEY"].startswith("drag_drop_")


@pytest.mark.parametrize(
    "result,added,raises,success",
    [
        (None, (9,), False, True),
        ("opened", (9,), False, True),
        ({"status": "ok"}, (), False, False),
        (None, (9, 10), False, False),
        ({"status": "error"}, (9,), False, False),
        (None, (9,), True, False),
    ],
)
def test_shelf_uses_workspace_confirmation_for_native_open(
    result: Any,
    added: tuple[int, ...],
    raises: bool,
    success: bool,
    runtime: Any,
    monkeypatch: Any,
) -> None:
    import sys
    from types import ModuleType

    calls = []
    packages = [NS(id=7)]

    def listed() -> list[Any]:
        calls.append("packages")
        return list(packages)

    class Host:
        def __enter__(self) -> Any:
            return self

        def __exit__(self, *args: object) -> None:
            calls.append("closed")

        def open_font(self, *, path: str) -> Any:
            calls.append(path)
            packages.extend(NS(id=ident) for ident in added)
            if raises:
                raise RuntimeError("native open exception")
            return result

    controls = ModuleType("fly.ap.controls")
    controls.FontLab = Host
    monkeypatch.setitem(sys.modules, "fly.ap.controls", controls)
    sys.modules["fly"].fl = NS(flWorkspace=NS(instance=lambda: NS(packages=listed)))
    fn = load(TITLES[1])["open_in_fontlab"]
    if success:
        fn("/absolute/source.ufo")
    else:
        with pytest.raises(RuntimeError):
            fn("/absolute/source.ufo")
    assert calls.count("/absolute/source.ufo") == 1
    assert calls[0] == "packages", "Read workspace before calling the opener"
    if success:
        assert calls.count("packages") == 2
    assert "closed" in calls


def test_shelf_reports_partial_open_without_retry(tmp_path: Path, runtime: Any) -> None:
    paths = [tmp_path / name for name in ("a.ttf", "b.ttf", "c.ttf")]
    for path in paths:
        path.touch()
    opened = []

    def opener(path: str) -> None:
        opened.append(path)
        if path == str(paths[1]):
            raise RuntimeError("native refusal")

    panel = load(TITLES[1])["panel_type"](runtime.qt, opener)()
    panel.add_paths([str(path) for path in paths])
    panel.items.selected = [0, 1, 2]
    with pytest.raises(RuntimeError, match="Opened 1 of 3"):
        panel.open_selected()
    assert opened == [str(paths[0]), str(paths[1])]
    assert len(panel.text_items()) == 3


def test_real_app_names_used_by_scripts_are_callable(monkeypatch: Any) -> None:
    """Resolve actual imported names and their called instance methods from source."""
    import importlib

    app_source = ROOT.parent / "fontlab-fontlabapp" / "src"
    monkeypatch.syspath_prepend(str(app_source))
    checked = set()
    for title in TITLES:
        tree = ast.parse((ROOT / "Scripts/Drag And Drop" / (title + ".py")).read_text())
        imports = {}
        for node in ast.walk(tree):
            if (
                not isinstance(node, ast.ImportFrom)
                or not node.module
                or not node.module.startswith("fly.ap.")
            ):
                continue
            module_name = "fontlabapp." + node.module.removeprefix("fly.ap.")
            module = importlib.import_module(module_name)
            assert (
                Path(module.__file__).resolve().is_relative_to(app_source.resolve())
            ), module.__file__
            for alias in node.names:
                target = getattr(module, alias.name)
                assert callable(target), f"{module_name}.{alias.name} must be callable"
                imports[alias.asname or alias.name] = (
                    target,
                    module_name + "." + alias.name,
                )
                checked.add(module_name + "." + alias.name)
        instances = {}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
            ):
                origin = imports.get(node.value.func.id)
                if origin:
                    for target in node.targets:
                        instances[ast.unparse(target)] = origin
            if isinstance(node, ast.With):
                for item in node.items:
                    call = item.context_expr
                    if (
                        isinstance(call, ast.Call)
                        and isinstance(call.func, ast.Name)
                        and item.optional_vars
                    ):
                        origin = imports.get(call.func.id)
                        if origin:
                            instances[ast.unparse(item.optional_vars)] = origin
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                origin = instances.get(ast.unparse(node.func.value))
                if origin:
                    owner, owner_name = origin
                    assert callable(getattr(owner, node.func.attr)), (
                        f"{owner_name}.{node.func.attr} must be callable"
                    )
                    checked.add(owner_name + "." + node.func.attr)
    assert {
        "fontlabapp.draft_signals.Scope",
        "fontlabapp.draft_signals.Scope.connect",
        "fontlabapp.draft_signals.Scope.finish",
        "fontlabapp.qt_properties.value",
        "fontlabapp.controls.FontLab.open_font",
        "fontlabapp.scripting.show_script_dialog",
        "fontlabapp.character_map_capture.capture",
    } <= checked, "Derive all script imports and their called methods from source"


@pytest.mark.parametrize("title", [TITLES[i] for i in (0, 1, 2, 3)])
def test_non_reordering_panels_have_no_reorder_flag(title: str) -> None:
    tree = ast.parse((ROOT / "Scripts/Drag And Drop" / (title + ".py")).read_text())
    assert not any(
        isinstance(node, ast.Name) and node.id == "REORDER" for node in ast.walk(tree)
    )


def test_shelf_batch_counts_only_workspace_confirmed_opens(
    tmp_path: Path,
    runtime: Any,
    monkeypatch: Any,
) -> None:
    import sys
    from types import ModuleType

    paths = [tmp_path / name for name in ("one.otf", "two.otf", "three.otf")]
    for path in paths:
        path.touch()
    packages, calls = [NS(id=1)], []

    class Host:
        def __enter__(self) -> Any:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def open_font(self, *, path: str) -> None:
            calls.append(path)
            if path == str(paths[0]):
                packages.append(NS(id=2))

    controls = ModuleType("fly.ap.controls")
    controls.FontLab = Host
    monkeypatch.setitem(sys.modules, "fly.ap.controls", controls)
    sys.modules["fly"].fl = NS(
        flWorkspace=NS(instance=lambda: NS(packages=lambda: packages))
    )
    module = load(TITLES[1])
    panel = module["panel_type"](runtime.qt, module["open_in_fontlab"])()
    panel.add_paths([str(path) for path in paths])
    panel.items.selected = [0, 1, 2]
    with pytest.raises(RuntimeError, match="Opened 1 of 3"):
        panel.open_selected()
    assert calls == [str(paths[0]), str(paths[1])], (
        "Stop when the workspace cannot confirm an open"
    )
