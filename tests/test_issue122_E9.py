# this_file: tests/test_issue122_E9.py
"""E9 algorithms and complete menu lifetimes with explicit PythonQt doubles.

These tests execute only new scripts. Preserved sources are data, never imports.
Native overloads, appearance and whole-font preservation need controller proof.
"""

import ast
import importlib
import json
import re
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
    "Calendar Proof Builder",
    "Font Handoff Letter",
    "Feature Code Draft",
    "Font Review Notes",
    "Script Snippet Notebook",
)


def load(title: str) -> dict[str, Any]:
    """Read the new menu with its host entry disabled."""
    return runpy.run_path(str(ROOT / "Scripts" / "Text" / f"{title}.py"))


def test_calendar_leap_year_and_reference_html() -> None:
    module = load(TITLES[0])
    plain, html = module["calendar_proof"](2024, 2, frozenset({32, *range(48, 58)}))
    assert "29" in plain and "30" not in plain
    assert plain.count("\n") >= 5 and "Reference rendering" in html
    assert "Missing numeral/separator code points: None" in html
    assert '<meta charset="utf-8">' in html
    with pytest.raises(ValueError):
        module["calendar_proof"](2024, 13, ())


def test_handoff_escapes_all_user_and_font_text() -> None:
    render = load(TITLES[1])["handoff_letter"]
    text = render("A&B", "<Client>", "Review <now>", ("A", "B.alt"))
    assert "A&amp;B" in text and "&lt;Client&gt;" in text
    assert "2 glyphs" in text and "B.alt" in text
    with pytest.raises(ValueError):
        render("", "Client", "review", ())


def test_feature_lexer_handles_comments_strings_and_utf16() -> None:
    module = load(TITLES[2])
    text = "😀 feature liga { sub f i by fi; } liga; # sub by"
    spans = module["feature_spans"](text)
    assert spans[0] == (3, 7, "keyword")
    assert spans[-1] == (41, 8, "comment")
    assert module["feature_spans"]('name "# sub"; # tail') == [
        (5, 7, "string"),
        (14, 6, "comment"),
    ]
    assert module["feature_spans"]("") == []


def test_notes_context_is_plain_text() -> None:
    render = load(TITLES[3])["review_heading"]
    assert render(("A", "a.alt")) == "\n## Font review: 2 glyphs\n/A /a.alt\n- [ ] \n"
    with pytest.raises(ValueError):
        render(())


def test_notebook_crud_navigation_json_and_export() -> None:
    module = load(TITLES[4])
    book = module["Notebook"]()
    book.put("Spacing", "print('A')")
    book.put("Anchors", "# inspect anchors")
    assert book.navigate("Spacing", 1) == "Anchors"
    assert book.find("PRINT") == ["Spacing"]
    with pytest.raises(ValueError):
        book.put("Spacing", "collision")
    book.put("Metrics", "# edited", old="Spacing")
    assert "Spacing" not in book.items
    restored = module["Notebook"]()
    restored.decode(book.encode())
    assert restored.items == book.items
    assert restored.export("Metrics") == "# Metrics\n# edited\n"
    before = dict(restored.items)
    for bad in ("[]", '{"x": 1}', '{"": "body"}', '{"x":"a","x":"b"}'):
        with pytest.raises(ValueError):
            restored.decode(bad)
        assert restored.items == before
    restored.remove("Metrics")
    with pytest.raises(ValueError):
        restored.remove("missing")


@pytest.mark.parametrize("title", TITLES)
def test_new_file_export_is_utf8_absolute_and_never_overwrites(
    title: str, tmp_path: Path
) -> None:
    module = load(title)
    target = tmp_path / "draft.txt"
    module["export_new"](str(target), "ą\n")
    assert target.read_bytes() == "ą\n".encode()
    with pytest.raises(FileExistsError):
        module["export_new"](str(target), "changed")
    with pytest.raises(ValueError):
        module["export_new"]("relative.txt", "x")
    assert target.read_text() == "ą\n"


class Signal:
    """Keep exact slots, including disconnection failure injection."""

    def __init__(self) -> None:
        self.slots: list[Any] = []
        self.fail = False

    def connect(self, slot: Any) -> None:
        self.slots.append(slot)

    def disconnect(self, slot: Any) -> None:
        if self.fail:
            raise RuntimeError("disconnect failed")
        self.slots.remove(slot)

    def emit(self, *args: Any) -> None:
        for slot in list(self.slots):
            slot(*args)


class Widget:
    """Small double; unknown native methods deliberately raise AttributeError."""

    def __init__(self, *args: Any) -> None:
        self.children: list[Any] = []
        if args and isinstance(args[-1], Widget):
            args[-1].children.append(self)
        self.clicked = Signal()
        self.textChanged = Signal()
        self.valueChanged = Signal()
        self.currentIndexChanged = Signal()
        self.text = args[0] if args and isinstance(args[0], str) else ""
        self.value = 0
        self.deleted = False
        self.visible = False
        self.html = ""

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
        self.text = text
        self.textChanged.emit()

    def setPlainText(self, text: str) -> None:
        self.text = text
        self.textChanged.emit()

    def toPlainText(self) -> str:
        return self.text

    def insertPlainText(self, text: str) -> None:
        self.setPlainText(self.text + text)

    def setHtml(self, text: str) -> None:
        self.html = text

    def setPlaceholderText(self, text: str) -> None:
        pass

    def setReadOnly(self, flag: bool) -> None:
        self.read_only = flag

    def setRange(self, low: int, high: int) -> None:
        pass

    def setValue(self, value: int) -> None:
        self.value = value

    def document(self) -> Any:
        return self

    def show(self) -> None:
        self.visible = True

    def deleteLater(self) -> None:
        assert not any(signal.slots for signal, _ in getattr(self, "connections", []))
        self.deleted = True

    def close(self) -> None:
        event = SimpleNamespace(accept=lambda: None, ignore=lambda: None)
        self.closeEvent(event)


class WindowFlags(int):
    """Represent the explicit native flags value class."""


class PanelWidget(Widget):
    """Reject Python attributes which shadow native QWidget members."""

    forbidden = frozenset(
        {
            "size",
            "text",
            "font",
            "name",
            "width",
            "height",
            "layout",
            "children",
            "parent",
            "windowTitle",
            "objectName",
            "palette",
            "geometry",
            "connect",
            "close",
            "show",
            "hide",
            "resize",
            "deleteLater",
        }
    )

    def __init__(self, *args: Any) -> None:
        assert isinstance(args[-1], WindowFlags), "Tool window flags need a value class"
        object.__setattr__(self, "_initializing", True)
        super().__init__(*args)
        object.__setattr__(self, "_initializing", False)

    def __setattr__(self, name: str, value: Any) -> None:
        if not getattr(self, "_initializing", True) and name in self.forbidden:
            raise AttributeError(f"Native QWidget member: {name}")
        object.__setattr__(self, name, value)


@pytest.fixture
def app_module(monkeypatch: Any) -> Any:
    """Import the actual host-free App source; never plant its capture symbol."""
    if not APP_SOURCE.is_dir():
        pytest.fail(f"The App source checkout is required: {APP_SOURCE}")
    monkeypatch.syspath_prepend(str(APP_SOURCE))
    module = importlib.import_module("fontlabapp.glyph_catalog")
    assert Path(module.__file__).resolve().is_relative_to(APP_SOURCE.resolve())
    assert callable(module.capture), "The real capture import must exist"
    return module


def test_capture_symbol_exists_in_real_app(app_module: Any) -> None:
    """Catch an import mismatch even when UI tests use detached snapshots."""
    assert app_module.capture.__module__ == "fontlabapp.glyph_catalog"


@pytest.mark.parametrize("title", TITLES)
def test_native_widget_attribute_collision_guard(title: str, host: Any) -> None:
    panel = load(title)["show"](host.qt, None)
    for name in PanelWidget.forbidden:
        with pytest.raises(AttributeError, match="Native QWidget member"):
            setattr(panel, name, object())
    click(panel, "Discard and Close")


@pytest.fixture
def host(monkeypatch: Any) -> Any:
    """Inject only read-only capture and documented App property access."""
    names = ["A", "zero", "one"]
    for name in (
        "fly",
        "fly.ap",
        "fly.ap.qt_properties",
        "fly.ap.glyph_catalog",
    ):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))

    def value(obj: Any, name: str) -> Any:
        item = getattr(obj, name)
        return item() if callable(item) else item

    sys.modules["fly.ap.qt_properties"].value = value
    sys.modules["fly.ap.glyph_catalog"].capture = lambda: SimpleNamespace(
        rows=[(n, "", "") for n in names]
    )
    clipboard = SimpleNamespace(text="")
    clipboard.setText = lambda text: setattr(clipboard, "text", text)
    gui = SimpleNamespace(
        **{
            name: Widget
            for name in (
                "QWidget",
                "QLabel",
                "QPushButton",
                "QLineEdit",
                "QPlainTextEdit",
                "QTextBrowser",
                "QVBoxLayout",
                "QHBoxLayout",
                "QSpinBox",
            )
        }
    )
    gui.QWidget = PanelWidget
    gui.QApplication = SimpleNamespace(clipboard=lambda: clipboard)
    qt = SimpleNamespace(
        QtGui=gui,
        QtCore=SimpleNamespace(
            Qt=SimpleNamespace(Tool=1, WA_QuitOnClose=2, WindowFlags=WindowFlags)
        ),
    )
    sys.modules["fly"].fl = SimpleNamespace(
        CurrentFont=lambda: SimpleNamespace(
            info=SimpleNamespace(familyName="Example", versionMajor=1, versionMinor=23)
        )
    )
    return SimpleNamespace(qt=qt, names=names)


@pytest.mark.parametrize("title", TITLES)
def test_modeless_ui_close_dirty_refusal_and_disconnect_retry(
    title: str, host: Any
) -> None:
    module = load(title)
    panel = module["show"](host.qt, None)
    assert panel.visible and panel.title == title
    assert panel.connections
    if hasattr(panel, "editor") and title != TITLES[0]:
        panel.editor.setPlainText("unsaved")
        panel.close()
        assert not panel.deleted, "Close must retain an unsaved draft"
    panel.dirty = False
    signal, _ = panel.connections[-1]
    signal.fail = True
    panel.close()
    assert not panel.deleted, "Disconnect failure must preserve the owner for retry"
    signal.fail = False
    panel.close()
    assert panel.deleted and not panel.connections


def click(panel: Any, title: str) -> None:
    """Deliver native clicked(bool), including an argument a native slot rejects."""
    button = next(child for child in panel.children if child.text == title)
    button.clicked.emit(False)


@pytest.mark.parametrize(
    "title,button",
    [
        (TITLES[0], "Build"),
        (TITLES[1], "Build"),
        (TITLES[2], "Insert Names"),
        (TITLES[3], "Font Heading"),
        (TITLES[4], "Font Names"),
    ],
)
def test_real_font_action_and_no_font_error_keep_draft(
    title: str, button: str, host: Any, app_module: Any, monkeypatch: Any
) -> None:
    panel = load(title)["show"](host.qt, None)
    if title == TITLES[1]:
        panel.project.setText("Proof")
        panel.recipient.setText("Reviewer")
        panel.editor.setPlainText("Review accents")
    click(panel, button)
    assert panel.dirty is (title != TITLES[0])
    if title in (TITLES[2], TITLES[3], TITLES[4]):
        assert "A" in panel.editor.toPlainText()
    before = panel.editor.toPlainText()
    panel.dirty = False

    native = importlib.import_module("fontlabapp._glyph_catalog_native")
    monkeypatch.setattr(
        native,
        "_native",
        lambda name: SimpleNamespace(
            flWorkspace=SimpleNamespace(
                instance=lambda: SimpleNamespace(currentPackage=None)
            )
        ),
    )
    monkeypatch.setitem(sys.modules, "fly.ap.glyph_catalog", app_module)
    click(panel, button)
    assert "Open a font" in panel.status.text
    assert panel.editor.toPlainText() == before
    click(panel, "Discard and Close")
    assert panel.deleted


def test_notebook_ui_draft_navigation_cancel_and_exports(
    host: Any, tmp_path: Path
) -> None:
    panel = load(TITLES[4])["show"](host.qt, None)
    panel.title_field.setText("A")
    panel.editor.setPlainText("# first")
    click(panel, "Add")
    assert panel.book.items == {"A": "# first"} and not panel.record_dirty
    panel.title_field.setText("B")
    panel.editor.setPlainText("# second")
    click(panel, "Next")
    assert "before continuing" in panel.status.text
    click(panel, "Add")
    click(panel, "Previous")
    assert panel.title_field.text == "A"
    panel.editor.setPlainText("unsaved change")
    click(panel, "Cancel Draft")
    assert panel.editor.text == "# first" and panel.dirty
    panel.destination.setText(str(tmp_path / "book.json"))
    click(panel, "Export New")
    assert not panel.dirty and not panel.collection_dirty
    assert json.loads((tmp_path / "book.json").read_text()) == panel.book.items
    panel.editor.setPlainText("cancel me")
    click(panel, "Cancel Draft")
    assert not panel.dirty, "Cancel restores the saved collection's clean state"
    panel.destination.setText(str(tmp_path / "snippet.py"))
    click(panel, "Export Snippet")
    assert (tmp_path / "snippet.py").read_text() == "# A\n# first\n"
    click(panel, "Remove")
    assert list(panel.book.items) == ["B"] and panel.dirty
    click(panel, "Discard and Close")


@pytest.mark.parametrize("title", [TITLES[2], TITLES[3]])
def test_local_editor_load_guard_and_export_errors_preserve_draft(
    title: str, host: Any, tmp_path: Path
) -> None:
    panel = load(title)["show"](host.qt, None)
    source = tmp_path / "input.txt"
    source.write_text("source ą", encoding="utf-8")
    panel.source.setText(str(source))
    click(panel, "Load")
    assert panel.editor.text == "source ą" and not panel.dirty
    panel.editor.setPlainText("edited")
    click(panel, "Load")
    assert panel.editor.text == "edited" and panel.dirty
    panel.destination.setText(str(source))
    click(panel, "Export New")
    assert panel.dirty and source.read_text() == "source ą"
    panel.destination.setText(str(tmp_path / "new.txt"))
    click(panel, "Export New")
    assert not panel.dirty and (tmp_path / "new.txt").read_text() == "edited"
    click(panel, "Discard and Close")


@pytest.mark.parametrize("title", TITLES)
def test_failed_construction_drains_connections(
    title: str, host: Any, monkeypatch: Any
) -> None:
    def fail(*args: Any) -> None:
        raise RuntimeError("injected construction failure")

    # This is the last common widget: several connections already exist.
    native_line = host.qt.QtGui.QLineEdit

    def line(*args: Any) -> Any:
        widget = native_line(*args)
        original = widget.setPlaceholderText

        def placeholder(text: str) -> None:
            if text.startswith("Absolute path to a NEW"):
                fail()
            original(text)

        widget.setPlaceholderText = placeholder
        return widget

    host.qt.QtGui.QLineEdit = line
    module = load(title)
    with pytest.raises(RuntimeError, match="construction failure"):
        module["show"](host.qt, None)
    assert not module["_PANELS"], "Construction failure must release its owner"


def test_batch_source_identity_denominator() -> None:
    rows = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    paths = [
        r["target"]
        for r in rows
        if any(
            f"/ports/{g}/" in r["target"]
            for g in ("richtext", "tutorials", "xmlpatterns")
        )
    ]
    assert len(paths) == 25


def test_every_identity_is_hash_bound_and_classified() -> None:
    """Verify recorded historical hashes and exact current destination attribution."""
    family_titles = {
        "calendar": TITLES[0],
        "orderform": TITLES[1],
        "syntaxhighlighter": TITLES[2],
        "textedit": TITLES[3],
        **{f"part{i}": TITLES[4] for i in range(1, 8)},
    }
    rows = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    counts = {"ported": 0, "duplicate-of": 0, "retired": 0}
    for row in rows:
        source = row["target"]
        if not any(
            f"/ports/{g}/" in source for g in ("richtext", "tutorials", "xmlpatterns")
        ):
            continue
        assert (
            recorded_sha256(source)
            == row["target_sha256"]
        )
        family = Path(source).name.split("-")[0]
        if family in {"textobject", "schema"}:
            counts["retired"] += 1
            continue  # QTextObjectInterface is absent in the captured host binding.
        destination = ROOT / "Scripts/Text" / f"{family_titles[family]}.py"
        body = destination.read_text()
        assert source not in body and row["target_sha256"] not in body
        assert "SPDX-License-Identifier: Apache-2.0" in body
        canonical = "/part2/" in source and (
            not family.startswith("part") or family == "part7"
        )
        counts["ported" if canonical else "duplicate-of"] += 1
    assert counts == {"ported": 5, "duplicate-of": 17, "retired": 3}


@pytest.mark.parametrize("title", TITLES)
def test_menu_main_routes_through_fly(title: str, host: Any, monkeypatch: Any) -> None:
    fly = sys.modules["fly"]
    fly.qt = host.qt
    fly.fl = SimpleNamespace(MainWindow=lambda: None)
    namespace = runpy.run_path(
        str(ROOT / "Scripts/Text" / f"{title}.py"), run_name="__main__"
    )
    assert len(namespace["_PANELS"]) == 1
    panel = namespace["_PANELS"][0]
    click(panel, "Discard and Close")
    assert not namespace["_PANELS"]


def test_highlighter_formats_utf16_and_detaches_before_close(host: Any) -> None:
    colors: list[Any] = []

    class Highlighter:
        def __init__(self, document: Any) -> None:
            self.document = document

        def setFormat(self, start: int, size: int, color: Any) -> None:
            colors.append((start, size, color))

        def setDocument(self, document: Any) -> None:
            self.document = document

    host.qt.QtGui.QSyntaxHighlighter = Highlighter
    host.qt.QtGui.QColor = lambda text: text
    panel = load(TITLES[2])["show"](host.qt, None)
    highlighter = panel.highlighter
    highlighter.highlightBlock("😀 sub A by B; # by")
    assert colors == [(3, 3, "#355fba"), (9, 2, "#355fba"), (15, 4, "#638568")]
    click(panel, "Discard and Close")
    assert highlighter.document is None and panel.deleted


def test_unicode_digit_coverage_ignores_glyph_names(host: Any) -> None:
    """Read exact Unicode cells even when no glyph has a traditional digit name."""
    capture = sys.modules["fly.ap.glyph_catalog"]
    rows = [(f"uni{code:04X}", f"U+{code:04X}", "") for code in range(48, 58)]
    rows.append(("space", "U+0020", ""))
    capture.capture = lambda: SimpleNamespace(rows=rows)
    module = load(TITLES[0])
    assert module["capture_codes"]() == frozenset({32, *range(48, 58)})
    plain, html = module["calendar_proof"](2024, 2, module["capture_codes"]())
    assert (
        plain
        == "February 2024\nMo Tu We Th Fr Sa Su\n         01 02 03 04\n05 06 07 08 09 10 11\n12 13 14 15 16 17 18\n19 20 21 22 23 24 25\n26 27 28 29         "
    )
    assert "Missing numeral/separator code points: None" in html
    _, missing = module["calendar_proof"](2024, 2, frozenset(range(48, 57)))
    assert "Missing numeral/separator code points: U+0020, U+0039" in missing
    panel = module["show"](host.qt, None)
    click(panel, "Build")
    assert not panel.dirty
    click(panel, "Copy")
    assert host.qt.QtGui.QApplication.clipboard().text == panel.editor.text
    panel.close()
    assert panel.deleted


@pytest.mark.parametrize("title", TITLES)
@pytest.mark.parametrize(
    "text,label",
    [
        ("a\x00b", "NUL"),
        ("a\u00a0b", "NBSP"),
        ("a\u2028b", "U+2028"),
        ("a\u2029b", "U+2029"),
        ("a\ud800b", "lone surrogate"),
    ],
)
def test_unsafe_text_refuses_export_before_file_creation(
    title: str, text: str, label: str, tmp_path: Path
) -> None:
    target = tmp_path / "new.txt"
    with pytest.raises(ValueError, match=re.escape(label)):
        load(title)["export_new"](str(target), text)
    assert not target.exists()


@pytest.mark.parametrize("title", [TITLES[2], TITLES[3]])
@pytest.mark.parametrize(
    "text,label",
    [
        ("a\x00b", "NUL"),
        ("a\u00a0b", "NBSP"),
        ("a\u2028b", "U+2028"),
        ("a\ud800b", "lone surrogate"),
    ],
)
def test_unsafe_load_retains_draft_and_names_character_class(
    title: str, text: str, label: str, host: Any, tmp_path: Path
) -> None:
    panel = load(title)["show"](host.qt, None)
    original = panel.editor.text
    source = tmp_path / "bad.txt"
    source.write_bytes(text.encode("utf-8", errors="surrogatepass"))
    panel.source.setText(str(source))
    click(panel, "Load")
    assert label in panel.status.text
    if label == "NBSP":
        assert "replace with a normal space" in panel.status.text
    assert panel.editor.text == original and not panel.dirty
    click(panel, "Discard and Close")


def test_unexpected_qt_normalization_refuses_load_and_export(
    host: Any, tmp_path: Path
) -> None:
    module = load(TITLES[3])
    panel = module["show"](host.qt, None)
    original_set = panel.editor.setPlainText
    panel.editor.setPlainText = lambda text: original_set(
        text.replace("normalize", "changed")
    )
    source = tmp_path / "source.txt"
    source.write_text("normalize", encoding="utf-8")
    panel.source.setText(str(source))
    click(panel, "Load")
    assert "normalization" in panel.status.text and panel.editor.text == ""
    original_set("normalize")
    native_plain = host.qt.QtGui.QPlainTextEdit

    def normalizer(*args: Any) -> Any:
        widget = native_plain(*args)
        setter = widget.setPlainText
        widget.setPlainText = lambda text: setter(text.replace("normalize", "changed"))
        return widget

    host.qt.QtGui.QPlainTextEdit = normalizer
    destination = tmp_path / "output.txt"
    panel.destination.setText(str(destination))
    click(panel, "Export New")
    assert "normalization" in panel.status.text and not destination.exists()
    assert panel.editor.text == "normalize" and panel.dirty
    click(panel, "Discard and Close")


def test_handoff_prefills_family_version_and_exports_complete_html(host: Any) -> None:
    panel = load(TITLES[1])["show"](host.qt, None)
    assert panel.project.text == "Example 1.023"
    panel.recipient.setText("Reviewer")
    panel.editor.setPlainText("Check accents")
    click(panel, "Build")
    assert panel.letter.startswith("<!DOCTYPE html>")
    assert '<meta charset="utf-8">' in panel.letter
    assert panel.letter.endswith("</body></html>")
    click(panel, "Copy")
    assert "Example 1.023" in host.qt.QtGui.QApplication.clipboard().text
    click(panel, "Discard and Close")


def test_added_feature_keywords_respect_full_glyph_name_boundaries() -> None:
    spans = load(TITLES[2])["feature_spans"]
    keywords = "substitute position ignore lookupflag anchor parameters rsub reversesub"
    assert [
        keywords[start : start + size] for start, size, kind in spans(keywords)
    ] == keywords.split()
    assert spans("foo.sub sub.alt @sub x-sub sub-name sub_name .sub ésub") == []


@pytest.mark.parametrize("title", TITLES)
def test_public_documentation_has_no_internal_provenance(title: str) -> None:
    path = ROOT / "Scripts/Text" / f"{title}.py"
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    doc = ast.get_docstring(tree)
    assert all(
        label in doc for label in ("What:", "How:", "Why:", "Usage:", "Benefit:")
    )
    assert not any(
        term in path.read_text()
        for term in (
            "issue 122",
            "E9",
            "D22",
            "reviewed App",
            "no writers",
            "rescued/",
            "SHA-256",
        )
    )
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            assert ast.get_docstring(node), (
                f"Missing function documentation: {node.name}"
            )


def test_xml_tool_is_retired() -> None:
    assert not (ROOT / "Scripts/Text/Glyph XML Schema Lab.py").exists()


@pytest.mark.parametrize(
    "text,label",
    [
        ("a\x00b", "NUL"),
        ("a\u00a0b", "NBSP"),
        ("a\u2028b", "U+2028"),
        ("a\ud800b", "lone surrogate"),
    ],
)
def test_notebook_json_load_refuses_lossy_records_transactionally(
    text: str, label: str, host: Any, tmp_path: Path
) -> None:
    panel = load(TITLES[4])["show"](host.qt, None)
    source = tmp_path / "bad.json"
    source.write_text(json.dumps({"Example": text}), encoding="utf-8")
    panel.source.setText(str(source))
    click(panel, "Load JSON")
    assert label in panel.status.text
    assert panel.book.items == {} and panel.editor.text == "" and not panel.dirty
    click(panel, "Discard and Close")


def test_missing_preserved_root_keeps_record_checks_active(monkeypatch: Any) -> None:
    monkeypatch.delenv("FONTLAB_PRESERVED_ROOT", raising=False)
    test_every_identity_is_hash_bound_and_classified()


@pytest.mark.parametrize("title", [TITLES[2], TITLES[3]])
@pytest.mark.parametrize(
    "raw,expected,notices",
    [
        (b"first\r\nsecond\r\n", "first\nsecond\n", ["Line endings converted to LF"]),
        (b"first\rsecond\r", "first\nsecond\n", ["Line endings converted to LF"]),
        (b"\xef\xbb\xbffirst\n", "first\n", ["BOM removed"]),
        (
            b"\xef\xbb\xbffirst\r\n",
            "first\n",
            ["BOM removed", "Line endings converted to LF"],
        ),
    ],
)
def test_load_normalizes_line_endings_and_bom_with_notice(
    title: str, raw: bytes, expected: str, notices: list[str], host: Any, tmp_path: Path
) -> None:
    """Normalize file encodings before Qt while preserving explicit conversion notices."""
    panel = load(title)["show"](host.qt, None)
    source = tmp_path / "input.txt"
    source.write_bytes(raw)
    panel.source.setText(str(source))
    click(panel, "Load")
    assert panel.editor.text == expected and not panel.dirty
    assert all(notice in panel.status.text for notice in notices)
    with pytest.raises(ValueError, match="CR line ending"):
        load(title)["check_text"]("still\rguarded")
    click(panel, "Discard and Close")


@pytest.mark.parametrize(
    "title,button",
    [
        (TITLES[2], "Insert Names"),
        (TITLES[3], "Font Heading"),
    ],
)
def test_capture_timeout_keeps_draft_and_reports_error(
    title: str, button: str, host: Any, monkeypatch: Any
) -> None:
    """A capture timeout must stay inside the callback boundary and retain the draft."""
    panel = load(title)["show"](host.qt, None)
    panel.editor.setPlainText("Keep this unsaved draft.\n")
    status_widget = panel.status

    def timeout() -> None:
        raise TimeoutError("Font metadata scan expired; try again.")

    monkeypatch.setattr(sys.modules["fly.ap.glyph_catalog"], "capture", timeout)
    click(panel, button)
    assert panel.editor.text == "Keep this unsaved draft.\n" and panel.dirty
    assert panel.status is status_widget
    assert panel.status.text == "Font metadata scan expired; try again."
    assert panel.visible and not panel.deleted
    click(panel, "Discard and Close")


def test_missing_highlighter_has_explicit_status(host: Any) -> None:
    """Keep the feature editor usable and explain the missing colour capability."""
    assert not hasattr(host.qt.QtGui, "QSyntaxHighlighter")
    panel = load(TITLES[2])["show"](host.qt, None)
    assert panel.status.text == "Syntax colouring unavailable"
    assert panel.highlighter is None
    click(panel, "Discard and Close")


def test_calendar_has_no_dead_capture_helper_and_keeps_local_date() -> None:
    source = (ROOT / "Scripts/Text/Calendar Proof Builder.py").read_text()
    assert "def capture_names(" not in source
    assert "datetime.now().astimezone().date()" in source


@pytest.mark.parametrize("title", TITLES)
def test_script_uses_only_the_public_catalog_capture(title: str) -> None:
    """Scripts import the public App capture and no private App module."""
    text = (ROOT / "Scripts/Text" / f"{title}.py").read_text()
    assert "_glyph_catalog_native" not in text
    assert "fly.ap._" not in text
