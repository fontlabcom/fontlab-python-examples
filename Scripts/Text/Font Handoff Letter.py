# this_file: Scripts/Text/Font Handoff Letter.py
# SPDX-License-Identifier: Apache-2.0
"""What: Prepare a font handoff letter with a complete glyph-name inventory.

How: Prefill the family and version from the current font. Combine your review
instructions with the current font's glyph names in an HTML letter.

Why: A precise review scope helps the recipient return useful corrections.

Usage: Check the project, enter a recipient and instructions, then select Build.
Use Copy for plain text or Export New for a complete UTF-8 HTML document.

Benefit: Send clear review instructions without changing font data.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.
"""

TITLE = "Font Handoff Letter"

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


def handoff_letter(
    project: str, recipient: str, instructions: str, names: tuple[str, ...]
) -> str:
    """Escape literal fields and every glyph name before composing an HTML letter."""
    from html import escape

    if not project.strip() or not recipient.strip() or not instructions.strip():
        raise ValueError("Enter a project, recipient and review instructions.")
    for text in (project, recipient, instructions, *names):
        check_text(text)
    inventory = " ".join("/" + escape(name) for name in names)
    return (
        '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Font Handoff</title></head><body>'
        f"<h1>{escape(project)}</h1><p>To: {escape(recipient)}</p>"
        f"<p>{escape(instructions).replace(chr(10), '<br>')}</p>"
        f"<h2>Review scope: {len(names)} glyphs</h2><p>{inventory}</p>"
        "<p>Please return corrections by glyph name.</p></body></html>"
    )


def current_font_label() -> str:
    """Read the current font's family and numeric version for the project field."""
    from fly import fl

    font = fl.CurrentFont()
    if font is None:
        raise ValueError("Open a font to prefill the family and version.")
    info = font.info
    family = info.familyName
    major, minor = info.versionMajor, info.versionMinor
    if not isinstance(family, str) or not family.strip():
        raise ValueError(
            "The current font has no family name. Enter a project manually."
        )
    suffix = (
        f" {major}.{minor:03d}" if type(major) is int and type(minor) is int else ""
    )
    return check_text(family + suffix)


def _populate(panel: Any, qt: Any) -> None:
    """Use one small form and an explicit current-font snapshot."""
    from fly.ap.qt_properties import value

    gui = qt.QtGui
    panel.project, panel.recipient = gui.QLineEdit(panel), gui.QLineEdit(panel)
    panel.project.setPlaceholderText("Project / font revision")
    try:
        panel.project.setText(current_font_label())
    except (ValueError, AttributeError, RuntimeError) as error:
        panel.status.setText(str(error))
    panel.recipient.setPlaceholderText("Recipient")
    panel.editor = gui.QPlainTextEdit(panel)
    panel.editor.setPlaceholderText("Review instructions")
    panel.preview = gui.QTextBrowser(panel)
    for widget in (panel.project, panel.recipient, panel.editor, panel.preview):
        panel.stack.addWidget(widget)
    panel.letter = ""
    for widget in (panel.project, panel.recipient, panel.editor):
        panel.wire(widget.textChanged, panel.edited)

    def build() -> None:
        """Generate the preview from current controls and font metadata."""
        result = handoff_letter(
            str(value(panel.project, "text")),
            str(value(panel.recipient, "text")),
            panel.editor.toPlainText(),
            capture_names(),
        )
        panel.letter = result
        panel.preview.setHtml(result)
        panel.status.setText("Letter ready. Copy text or export the HTML document.")

    def payload() -> str:
        # Always rebuild: never export a stale preview after form edits.
        """Return the checked content for export."""
        build()
        return panel.letter

    def copy_payload() -> str:
        """Compose a current-font handoff in plain text for the clipboard."""
        project = check_text(str(value(panel.project, "text")))
        recipient = check_text(str(value(panel.recipient, "text")))
        instructions = read_editor_exact(panel.editor, gui)
        names = capture_names()
        return (
            project
            + "\nTo: "
            + recipient
            + "\n"
            + instructions
            + f"\n{len(names)} glyphs\n"
            + " ".join("/" + name for name in names)
        )

    panel.copy_payload = copy_payload
    panel.payload = payload
    panel.button("Build", build)


def main() -> None:
    """Open through Fly. Never create an application or run a global event loop."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
