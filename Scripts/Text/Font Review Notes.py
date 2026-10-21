# this_file: Scripts/Text/Font Review Notes.py
# SPDX-License-Identifier: Apache-2.0
"""What: Edit Markdown notes beside the current FontLab font.

How: Keep notes in a local text document. Add a font heading or checklist.

Why: Review notes need glyph references without changes to glyph note fields.

Usage: Type notes or Load a UTF-8 file from an absolute path. Select Font Heading
to add current-font names. Copy or Export New transfers the notes.

Benefit: Keep a clear checklist for spacing, accents and other review tasks.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.
"""

TITLE = "Font Review Notes"

from collections.abc import Callable
from pathlib import Path
from typing import Any

_PANELS: list[Any] = []


def capture_names() -> tuple[str, ...]:
    """Read the current font's glyph names. Refuse missing or unstable font context."""
    from fly.ap.glyph_catalog import capture

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


def review_heading(names: tuple[str, ...]) -> str:
    """Make a Markdown checklist header from a complete font name snapshot."""
    if not names:
        raise ValueError("The current font has no glyphs to review.")
    return (
        f"\n## Font review: {len(names)} glyphs\n"
        + " ".join("/" + name for name in names)
        + "\n- [ ] \n"
    )


def _populate(panel: Any, qt: Any) -> None:
    """Use literal text so pasted HTML cannot become document markup."""
    from fly.ap.qt_properties import value

    gui = qt.QtGui
    panel.editor = gui.QPlainTextEdit(panel)
    panel.editor.setPlaceholderText(
        "# Review notes\n- [ ] Check spacing\n- [ ] Check accents"
    )
    panel.stack.addWidget(panel.editor)
    panel.source = gui.QLineEdit(panel)
    panel.source.setPlaceholderText("Absolute UTF-8 notes source path")
    panel.stack.addWidget(panel.source)

    def load() -> None:
        """Load checked UTF-8 text while retaining the previous draft on failure."""
        if panel.dirty:
            raise ValueError("Export the draft before loading another file.")
        path = Path(str(value(panel.source, "text"))).expanduser()
        if not path.is_absolute():
            raise ValueError("Enter an absolute source path.")
        with path.open(
            encoding="utf-8-sig", errors="surrogatepass", newline=None
        ) as stream:
            had_bom = stream.buffer.peek(3).startswith(b"\xef\xbb\xbf")
            text = stream.read()
            endings = stream.newlines or ()
        if isinstance(endings, str):
            endings = (endings,)
        notes = []
        if any("\r" in ending for ending in endings):
            notes.append("Line endings converted to LF.")
        if had_bom:
            notes.append("BOM removed.")
        was_dirty = panel.dirty
        try:
            set_plain_exact(panel.editor, text)
        except ValueError:
            panel.dirty = was_dirty
            raise
        panel.dirty = False
        panel.status.setText(
            " ".join(["Loaded.", *notes, "Edits stay local until Export New."])
        )

    panel.wire(panel.editor.textChanged, panel.edited)
    panel.payload = lambda: read_editor_exact(panel.editor, gui)
    panel.button("Load", load)
    panel.button(
        "Font Heading",
        lambda: panel.editor.insertPlainText(
            check_text(review_heading(capture_names()))
        ),
    )
    panel.button("Checklist", lambda: panel.editor.insertPlainText("\n- [ ] "))


def main() -> None:
    """Open through Fly. Never create an application or run a global event loop."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
