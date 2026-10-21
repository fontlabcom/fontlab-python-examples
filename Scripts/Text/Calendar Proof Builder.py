# this_file: Scripts/Text/Calendar Proof Builder.py
# SPDX-License-Identifier: Apache-2.0
"""What: Create a monthly numeral proof for the current font.

How: Read Unicode assignments. Build a Monday-first calendar and report missing
ASCII digits and the space separator. The HTML preview uses a reference font.

Why: Glyph names do not identify Unicode coverage reliably.

Usage: Set year and month. Select Build, then Copy. Paste into FontLab Metrics
to proof the actual font. Export New saves a complete UTF-8 HTML document.

Benefit: Check date spacing with realistic numeral sequences.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Panels stay open beside the
font. Export uses a new absolute path and never overwrites an existing file.

Idea from the Qt/PyQt examples (Riverbank Computing, Nokia, 2010-2013).
Independent rewrite. Apache-2.0.
"""

TITLE = "Calendar Proof Builder"

from collections.abc import Callable
from pathlib import Path
from typing import Any

_PANELS: list[Any] = []


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


def capture_codes() -> frozenset[int]:
    """Read Unicode coverage from the snapshot's Unicode column, not glyph names."""
    from fly.ap.glyph_catalog import capture

    return frozenset(
        int(code.removeprefix("U+"), 16)
        for row in capture().rows
        for code in row[1].split()
    )


def calendar_proof(year: int, month: int, codes: frozenset[int]) -> tuple[str, str]:
    """Return calendar text and complete HTML with numeral and space coverage."""
    import calendar
    from html import escape

    if not 1 <= year <= 9999 or not 1 <= month <= 12:
        raise ValueError("Use a year from 1 to 9999 and a month from 1 to 12.")
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(year, month)
    plain = calendar.month_name[month] + f" {year}\nMo Tu We Th Fr Sa Su\n"
    plain += "\n".join(
        " ".join(f"{day:02}" if day else "  " for day in week) for week in weeks
    )
    required = {0x20, *range(0x30, 0x3A)}
    missing = ", ".join(f"U+{code:04X}" for code in sorted(required - codes)) or "None"
    cells = "".join(
        "<tr>" + "".join(f"<td>{day or ''}</td>" for day in week) + "</tr>"
        for week in weeks
    )
    body = (
        f"<h1>{escape(calendar.month_name[month])} {year}</h1>"
        "<p>Reference rendering. Paste plain text into FontLab Metrics to proof the font.</p>"
        '<table border="1" cellpadding="8"><tr>'
        + "".join(
            f"<th>{day}</th>" for day in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
        )
        + f"</tr>{cells}</table><p>Missing numeral/separator code points: {missing}</p>"
        "<p>Coverage checks U+0030–U+0039 and U+0020. Headers are labels; newlines are layout.</p>"
    )
    return (
        plain,
        '<!DOCTYPE html><html><head><meta charset="utf-8"><title>Calendar Proof</title></head><body>'
        + body
        + "</body></html>",
    )


def _populate(panel: Any, qt: Any) -> None:
    """Keep explicit Build so changing font context never replaces a proof silently."""
    from datetime import datetime

    from fly.ap.qt_properties import value

    gui = qt.QtGui
    controls = gui.QHBoxLayout()
    today = datetime.now().astimezone().date()  # local calendar date of the user
    year, month = gui.QSpinBox(panel), gui.QSpinBox(panel)
    year.setRange(1, 9999)
    year.setValue(today.year)
    month.setRange(1, 12)
    month.setValue(today.month)
    for label, control in (("Year", year), ("Month", month)):
        controls.addWidget(gui.QLabel(label, panel))
        controls.addWidget(control)
    panel.stack.addLayout(controls)
    panel.preview = gui.QTextBrowser(panel)
    panel.editor = gui.QPlainTextEdit(panel)
    panel.editor.setReadOnly(True)
    panel.stack.addWidget(panel.preview)
    panel.stack.addWidget(panel.editor)
    panel.proof_html = ""

    def build() -> None:
        """Generate the preview from current controls and font metadata."""
        codes = capture_codes()
        plain, html = calendar_proof(
            int(value(year, "value")), int(value(month, "value")), codes
        )
        set_plain_exact(panel.editor, plain)
        panel.proof_html = html
        panel.preview.setHtml(html)
        panel.status.setText(
            "Proof ready. Copy text into FontLab Metrics to proof the font."
        )

    def payload() -> str:
        """Return the checked content for export."""
        if not panel.proof_html:
            raise ValueError("Build a proof from an open font first.")
        return panel.proof_html

    panel.copy_payload = lambda: read_editor_exact(panel.editor, gui)
    panel.payload = payload
    panel.button("Build", build)


def main() -> None:
    """Open through Fly. Never create an application or run a global event loop."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
