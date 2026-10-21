# this_file: Scripts/Text/Script Snippet Notebook.py
# SPDX-License-Identifier: Apache-2.0
"""What: Keep named FontLab scripting snippets in a local notebook.

How: Store code as text. Search, browse, edit or remove named records. JSON
stores the collection. Snippet export saves one record as a Python file.

Why: A text notebook keeps reusable code available without executing it.

Usage: Enter a title and code. Select Add or Replace before navigation. Use
Cancel Draft to restore the current record. Load JSON reads a collection.
Export New saves JSON. Export Snippet saves the current record. Copy copies it.

Benefit: Reuse scripting knowledge while keeping the current font unchanged.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.
"""

TITLE = "Script Snippet Notebook"

from collections.abc import Callable
from pathlib import Path
from typing import Any

_PANELS: list[Any] = []


def capture_names() -> tuple[str, ...]:
    """Read the current font's glyph names. Refuse missing or unstable font context."""
    from fly.ap._glyph_catalog_native import capture

    return tuple(row[0] for row in capture().rows)


def check_text(text: str) -> str:
    """Reject character classes that can change in a Qt plain-text document."""
    classes = []
    for character, label in (
        ("\x00", "NUL"),
        ("\u00a0", "NBSP (U+00A0); replace with a normal space"),
        ("\u2028", "U+2028 line separator"),
        ("\u2029", "U+2029 paragraph separator"),
        ("\r", "CR line ending"),
    ):
        if character in text:
            classes.append(label)
    if any(0xD800 <= ord(character) <= 0xDFFF for character in text):
        classes.append("lone surrogate")
    if classes:
        raise ValueError(
            "Unsupported text: " + ", ".join(classes) + ". Content retained; no export."
        )
    return text


def set_plain_exact(editor: Any, text: str) -> None:
    """Set checked text and verify the result. Restore the old text on mismatch."""
    check_text(text)
    previous = str(editor.toPlainText())
    editor.setPlainText(text)
    if str(editor.toPlainText()) != text:
        editor.setPlainText(previous)
        raise ValueError(
            "Qt plain-text normalization changed the text (line endings or unsupported characters). Content retained; no export."
        )


def read_editor_exact(editor: Any, gui: Any) -> str:
    """Check an export in a detached editor so draft text and Undo stay intact."""
    text = check_text(str(editor.toPlainText()))
    probe = gui.QPlainTextEdit()
    try:
        set_plain_exact(probe, text)
    finally:
        probe.deleteLater()
    return text


def export_new(filename: str, text: str) -> None:
    """Export UTF-8 to a new absolute path. Refuse existing files and links."""
    path = Path(filename).expanduser()
    if not path.is_absolute():
        raise ValueError("Enter an absolute destination path.")
    check_text(text).encode("utf-8")
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(text)


def show(qt: Any, parent: Any) -> Any:
    """Build one modeless tool; retain every exact connection until safe close."""
    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own draft state on a Python subclass, never on a native wrapper."""

        def __init__(self) -> None:
            """Initialize the owned controls and the local draft state."""
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.connections: list[tuple[Any, Callable[..., Any]]] = []
            self.dirty = False
            self.closed = False
            self.highlighter: Any = None
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(720, 560)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(18, 18, 18, 18)
            self.stack.setSpacing(10)
            self.status = gui.QLabel("Local draft. Font data stays unchanged.", self)
            self.stack.addWidget(self.status)
            self.buttons = gui.QHBoxLayout()

        def wire(self, signal: Any, callback: Callable[..., Any]) -> None:
            """Retain a guarded signal callback until safe disconnection."""

            def route(*args: Any) -> None:
                """Ignore callbacks after the panel has closed."""
                if not self.closed:
                    callback(*args)

            signal.connect(route)
            self.connections.append((signal, route))

        def button(self, title: str, callback: Callable[[], Any]) -> None:
            """Add a button that contains callback errors in the status line."""
            button = gui.QPushButton(title, self)
            self.buttons.addWidget(button)
            self.wire(button.clicked, lambda *args: self.run(callback))

        def run(self, callback: Callable[[], Any]) -> None:
            """Run a UI action and show an error without closing the draft."""
            try:
                callback()
            except Exception as error:  # noqa: BLE001 - contain native callback/lifecycle failures
                self.status.setText(str(error))

        def edited(self, *args: Any) -> None:
            """Mark local text changes as unsaved."""
            self.dirty = True
            self.status.setText(
                "Unsaved draft. Export before closing, or Discard and Close."
            )

        def save(self) -> None:
            """Validate and export the current draft to a new file."""
            from fly.ap.qt_properties import value

            content = self.payload()
            check_text(content)
            if hasattr(self, "editor"):
                read_editor_exact(self.editor, gui)
            export_new(str(value(self.destination, "text")), content)
            self.dirty = False
            if hasattr(self, "after_save"):
                self.after_save()
            self.status.setText("Export saved. Existing files are never overwritten.")

        def copy_text(self) -> None:
            """Copy checked plain text using the host clipboard."""
            content = (
                self.copy_payload() if hasattr(self, "copy_payload") else self.payload()
            )
            check_text(content)
            if hasattr(self, "editor"):
                read_editor_exact(self.editor, gui)
            gui.QApplication.clipboard().setText(content)
            self.status.setText("Text copied.")

        def discard(self) -> None:
            """Discard unsaved state and request a safe close."""
            self.dirty = False
            self.close()

        def closeEvent(self, event: Any) -> None:
            """Keep unsaved text open; disconnect callbacks before deletion."""
            if self.dirty:
                self.status.setText("Unsaved draft. Export, or use Discard and Close.")
                event.ignore()
                return
            try:
                while self.connections:
                    signal, slot = self.connections[-1]
                    signal.disconnect(slot)
                    self.connections.pop()
                if self.highlighter is not None:
                    self.highlighter.setDocument(None)
            except Exception as error:  # noqa: BLE001 - contain native callback/lifecycle failures
                self.status.setText(f"Close paused: {error}. Retry Close.")
                event.ignore()
                return
            self.closed = True
            event.accept()
            if self in _PANELS:
                _PANELS.remove(self)
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        _populate(panel, qt)
        panel.stack.addLayout(panel.buttons)
        panel.destination = gui.QLineEdit(panel)
        panel.destination.setPlaceholderText("Absolute path to a NEW export file")
        panel.stack.addWidget(panel.destination)
        panel.button("Copy", panel.copy_text)
        panel.button("Export New", panel.save)
        panel.button("Discard and Close", panel.discard)
        panel.dirty = False
        panel.show()
    except Exception:
        panel.dirty = False
        panel.close()
        raise
    return panel


class Notebook:
    """Keep named plain-text records. Never import or execute their contents."""

    def __init__(self) -> None:
        """Initialize the owned controls and the local draft state."""
        self.items: dict[str, str] = {}

    def put(self, title: str, body: str, old: str | None = None) -> None:
        """Add or rename a record; reject collisions before changing the mapping."""
        check_text(title)
        check_text(body)
        if not title.strip() or not body.strip() or "\n" in title or "\r" in title:
            raise ValueError("Use a single-line title and nonempty snippet.")
        if old is not None and old not in self.items:
            raise ValueError("The record to replace is missing.")
        if title in self.items and title != old:
            raise ValueError("That title already exists.")
        if old is not None:
            del self.items[old]
        self.items[title] = body

    def remove(self, title: str) -> None:
        """Remove only an existing committed record."""
        if title not in self.items:
            raise ValueError("Select an existing record first.")
        del self.items[title]

    def navigate(self, current: str | None, delta: int) -> str:
        """Wrap through sorted titles in either direction."""
        keys = sorted(self.items)
        if not keys:
            raise ValueError("Add a snippet first.")
        index = keys.index(current) if current in keys else -1 if delta > 0 else 0
        return keys[(index + delta) % len(keys)]

    def find(self, query: str) -> list[str]:
        """Search titles and code without case sensitivity, in stable order."""
        return [
            key
            for key in sorted(self.items)
            if query.casefold() in (key + "\n" + self.items[key]).casefold()
        ]

    def encode(self) -> str:
        """Return human-readable Unicode JSON; no executable serialization."""
        import json

        return (
            json.dumps(self.items, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        )

    def decode(self, text: str) -> None:
        """Parse into a detached notebook; malformed input preserves existing data."""
        import json

        def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
            """Reject duplicate JSON record titles before creating a mapping."""
            result: dict[str, Any] = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate snippet title in JSON.")
                result[key] = value
            return result

        data = json.loads(text, object_pairs_hook=unique)
        if not isinstance(data, dict):
            raise ValueError("A notebook must be a JSON object of text records.")  # noqa: TRY004 - malformed JSON value
        draft = Notebook()
        for key, body in data.items():
            if not isinstance(body, str):
                raise ValueError("Every snippet body must be text.")  # noqa: TRY004 - malformed JSON value
            draft.put(key, body)
        self.items = draft.items

    def export(self, title: str) -> str:
        """Export one committed snippet as Python text without executing it."""
        if title not in self.items:
            raise ValueError("Select an existing record first.")
        return (
            f"# {title}\n"
            + self.items[title]
            + ("" if self.items[title].endswith("\n") else "\n")
        )


def _populate(panel: Any, qt: Any) -> None:
    """Keep record drafts separate from the committed, exportable collection."""
    from fly.ap.qt_properties import value

    gui = qt.QtGui
    panel.book = Notebook()
    panel.current = None
    panel.record_dirty = False
    panel.collection_dirty = False
    panel.loading = False
    panel.title_field = gui.QLineEdit(panel)
    panel.title_field.setPlaceholderText("Snippet title")
    panel.editor = gui.QPlainTextEdit(panel)
    panel.editor.setPlaceholderText("Python code, stored as text. Never executed here.")
    panel.query = gui.QLineEdit(panel)
    panel.query.setPlaceholderText("Find in titles and code")
    panel.source = gui.QLineEdit(panel)
    panel.source.setPlaceholderText("Absolute JSON notebook source path")
    for widget in (panel.title_field, panel.editor, panel.query, panel.source):
        panel.stack.addWidget(widget)

    def edited(*args: Any) -> None:
        """Mark local text changes as unsaved."""
        if not panel.loading:
            panel.record_dirty = True
            panel.edited()

    def display(title: str | None) -> None:
        """Display one committed record without marking it as a new edit."""
        panel.loading = True
        try:
            panel.current = title
            panel.title_field.setText(title or "")
            set_plain_exact(panel.editor, panel.book.items.get(title, ""))
            panel.record_dirty = False
        finally:
            panel.loading = False

    def require_stored() -> None:
        """Refuse navigation while the current record has uncommitted edits."""
        if panel.record_dirty:
            raise ValueError("Add, Replace or Cancel Draft before continuing.")

    def store(replace: bool) -> None:
        """Add or replace one checked record, then display its committed text."""
        title = str(value(panel.title_field, "text"))
        if replace and panel.current is None:
            raise ValueError("Select a record to replace first.")
        panel.book.put(
            title,
            read_editor_exact(panel.editor, gui),
            old=panel.current if replace else None,
        )
        display(title)
        panel.collection_dirty = True
        panel.edited()

    def navigate(delta: int) -> None:
        """Move to a neighbouring committed record in title order."""
        require_stored()
        display(panel.book.navigate(panel.current, delta))

    def remove() -> None:
        """Remove the current record from the local collection."""
        require_stored()
        panel.book.remove(panel.current)
        display(next(iter(sorted(panel.book.items)), None))
        panel.collection_dirty = True
        panel.edited()

    def find() -> None:
        """Display the next record that matches the search text."""
        require_stored()
        matches = panel.book.find(str(value(panel.query, "text")))
        if not matches:
            raise ValueError("No matching snippet.")
        current = matches.index(panel.current) if panel.current in matches else -1
        display(matches[(current + 1) % len(matches)])

    def load() -> None:
        """Load checked UTF-8 text while retaining the previous draft on failure."""
        require_stored()
        if panel.dirty:
            raise ValueError("Export the notebook before loading another collection.")
        path = Path(str(value(panel.source, "text"))).expanduser()
        if not path.is_absolute():
            raise ValueError("Enter an absolute source path.")
        candidate = Notebook()
        candidate.decode(path.read_text(encoding="utf-8", errors="surrogatepass"))
        probe = gui.QPlainTextEdit()
        try:
            for body in candidate.items.values():
                set_plain_exact(probe, body)
        finally:
            probe.deleteLater()
        panel.book = candidate
        display(next(iter(sorted(panel.book.items)), None))
        panel.status.setText("Notebook loaded. No code was executed.")

    def payload() -> str:
        """Return the checked content for export."""
        require_stored()
        read_editor_exact(panel.editor, gui)
        return panel.book.encode()

    def export_snippet() -> None:
        """Export one committed snippet to a new Python source file."""
        require_stored()
        read_editor_exact(panel.editor, gui)
        export_new(
            str(value(panel.destination, "text")), panel.book.export(panel.current)
        )
        panel.status.setText(
            "Snippet exported. Export New still saves the complete notebook."
        )

    def cancel_draft() -> None:
        """Restore the current committed record and its saved-state marker."""
        display(panel.current)
        panel.dirty = panel.collection_dirty
        panel.status.setText("Draft cancelled. Committed snippets retained.")

    def saved() -> None:
        """Mark the collection as saved after successful JSON export."""
        panel.collection_dirty = False

    panel.after_save = saved

    def insert_context() -> None:
        """Add the current font glyph names without executing code."""
        panel.editor.insertPlainText(
            check_text("\n# Current font glyphs: " + " ".join(capture_names()) + "\n")
        )

    panel.wire(panel.title_field.textChanged, edited)
    panel.wire(panel.editor.textChanged, edited)
    for label, action in (
        ("Add", lambda: store(False)),
        ("Replace", lambda: store(True)),
        ("Cancel Draft", cancel_draft),
        ("Remove", remove),
    ):
        panel.button(label, action)
    panel.stack.addLayout(panel.buttons)
    panel.buttons = gui.QHBoxLayout()
    for label, action in (
        ("Previous", lambda: navigate(-1)),
        ("Next", lambda: navigate(1)),
        ("Find", find),
        ("Font Names", insert_context),
    ):
        panel.button(label, action)
    panel.stack.addLayout(panel.buttons)
    panel.buttons = gui.QHBoxLayout()
    panel.button("Load JSON", load)
    panel.button("Export Snippet", export_snippet)
    panel.copy_payload = lambda: read_editor_exact(panel.editor, gui)
    panel.payload = payload


def main() -> None:
    """Open through Fly. Never create an application or run a global event loop."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
