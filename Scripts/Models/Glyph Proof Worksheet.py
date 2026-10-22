# this_file: Scripts/Models/Glyph Proof Worksheet.py
# SPDX-License-Identifier: Apache-2.0
"""What: Calculate repeated FontLab slash-name proof lines for captured glyphs.
How: Keep one count per glyph. Apply Draft updates only that row's count and
proof items in the existing model. Refuse invalid counts and excessive output.
Why: Slash names retain alternate and unencoded glyph identities in proof text.
Usage: Open a font and Refresh. Choose a row, enter 1 to 1000 and Apply Draft.
Copy or Export New to use the proof in a Glyph window text bar. Export before
closing, or choose Discard and Close. Reset Draft explicitly discards changes.
Benefit: Prepare repeated spacing checks without typing each glyph occurrence.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Failed captures retain the current proof and pending count.

Independent rewrite of the Qt spreadsheet example idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py
SHA256: b491650437d8faa9b59a6f4859bdb420c8507e4fde37fecc95ef87e7d0a2cd1d
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py
SHA256: 09ded2c0d8220569aadaa24f61bc7adc08c771ec364b6a1c6ef7d47ef76fddf7
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

Rows = tuple[tuple[str, ...], ...]
_PANELS: list[Any] = []


def checked(text: str) -> str:
    """Refuse characters which PythonQt can replace during text conversion."""
    for char, name in (
        ("\0", "NUL"),
        ("\r", "CR"),
        ("\u00a0", "NBSP; replace with a normal space"),
        ("\u2028", "line separator"),
        ("\u2029", "paragraph separator"),
    ):
        if char in text:
            raise ValueError(f"Refuse {name} in text.")
    text.encode("utf-8")
    return text


TITLE = "Glyph Proof Worksheet"
HEADERS = ("Glyph name", "Repeat count", "Proof line")
HELP = "Choose a glyph row and enter a repeat count from 1 to 1000, then Apply Draft. Copy or export plain proof lines to use in a Glyph window text bar."


DRAFT_HINT = "Repeat count, 1 to 1000"
MAX_PROOF_CHARS = 2_000_000


def validate_draft(text: str) -> str:
    """Accept only a bounded whole-number repeat count."""
    if not text.isascii() or not text.isdecimal() or not 1 <= int(text) <= 1000:
        raise ValueError(DRAFT_HINT)
    return str(int(text))


def build_rows(rows: Rows, drafts: dict[str, str]) -> Rows:
    """Compute proof strings without interpreting formula text or Python code."""
    result = []
    total = 0
    for name, _unicodes, _modified in rows:
        if not name or "/" in name or any(char.isspace() for char in name):
            raise ValueError("Glyph names must fit FontLab slash-name proof syntax.")
        count = validate_draft(drafts.get(name, "1"))
        total += (len(name) + 1) * int(count) + 1
        if total > MAX_PROOF_CHARS:
            raise ValueError(
                "Proof exceeds two million characters. Reduce repeat counts."
            )
        result.append((name, count, ("/" + name) * int(count)))
    return tuple(result)


def report(rows: Rows, drafts: dict[str, str]) -> str:
    """Produce plain proof lines for FontLab's text bar."""
    return "\n".join(row[2] for row in build_rows(rows, drafts))


def show(qt: Any, parent: Any = None, capture: Callable[[], Any] | None = None) -> Any:
    """Open one owned modeless panel. Inject detached capture in offline tests."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore
    if capture is None:
        import fly.ap.glyph_catalog as catalogue

        capture = catalogue.capture

    class Panel(gui.QWidget):
        """Keep Python state on a subclass and never shadow a native member."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.snapshot: Rows = ()
            self.drafts: dict[str, str] = {}
            self.dirty = False
            self.pending = False
            self.loading_field = False
            self.current_row = 1
            self.proof_chars = 0
            self.capture_font = capture
            self.owned_model: Any = None
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(860, 580)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(16, 16, 16, 16)
            self.stack.setSpacing(8)
            self.status_line = gui.QLabel(HELP, self)
            self.status_line.setTextFormat(core.Qt.PlainText)
            self.status_line.setWordWrap(True)
            self.stack.addWidget(self.status_line)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def populate(self) -> None:
            """Create controls after ownership is retained; permit setup cleanup."""
            self.scope.connect(
                self.destroyed, lambda *args: self.destroyed_owner(), closing=True
            )
            self.table_strip = gui.QHBoxLayout()
            self.table_view = gui.QTableView(self)
            self.table_strip.addWidget(self.table_view)
            self.stack.addLayout(self.table_strip)
            self.action_strip = gui.QHBoxLayout()
            self.stack.addLayout(self.action_strip)
            self.button("Refresh", self.refresh)
            self.button("Reset Draft", lambda: self.refresh(reset=True))
            self.row_number = gui.QSpinBox(self)
            self.stack.addWidget(self.row_number)
            self.row_detail = gui.QPlainTextEdit(self)
            self.row_detail.setReadOnly(True)
            self.stack.addWidget(self.row_detail)
            self.draft_field = gui.QLineEdit(self)
            self.draft_field.setPlaceholderText(DRAFT_HINT)
            self.stack.addWidget(self.draft_field)
            self.scope.connect(
                self.draft_field.textChanged, lambda *args: self.field_edited()
            )
            self.scope.connect(
                self.row_number.valueChanged, lambda *args: self.describe_row()
            )
            self.scope.connect(
                self.table_view.clicked,
                lambda index: self.row_number.setValue(index.row() + 1),
            )
            self.button("Apply Draft", self.apply_draft)
            self.export_field = gui.QLineEdit(self)
            self.export_field.setPlaceholderText("Absolute NEW report path")
            self.stack.addWidget(self.export_field)
            self.button("Copy Report", self.copy_report)
            self.button("Export New", self.export_report)
            self.button("Discard and Close", self.discard, closing=True)

        def button(
            self, text: str, action: Callable[[], Any], *, closing: bool = False
        ) -> None:
            """Adapt clicked(bool) explicitly and retain its exact connection."""
            control = gui.QPushButton(text, self)
            self.action_strip.addWidget(control)
            self.scope.connect(
                control.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def stage(self, rows: Rows, drafts: dict[str, str]) -> Any:
            """Build a detached read-only model before replacing a visible model."""
            model = gui.QStandardItemModel(self)
            try:
                model.setHorizontalHeaderLabels(list(HEADERS))
                display = build_rows(rows, drafts)
                for row in display:
                    cells = []
                    for text in row:
                        item = gui.QStandardItem(checked(text))
                        item.setEditable(False)
                        cells.append(item)
                    model.appendRow(cells)
            except Exception:
                model.deleteLater()
                raise
            return model

        def install(self, model: Any) -> None:
            """Bind peers to the same model and selection owner; release old owners."""
            old = self.owned_model
            old_selection = (
                self.table_view.selectionModel() if old is not None else None
            )
            self.table_view.setModel(model)
            self.owned_model = model
            if old_selection is not None:
                old_selection.deleteLater()
            if old is not None:
                old.deleteLater()

        def refresh(self, *, reset: bool = False) -> None:
            """Keep the previous snapshot and drafts when a new read fails."""
            if self.dirty and not reset:
                raise ValueError("Export the draft or use Reset Draft before Refresh.")
            rows = tuple(
                tuple(checked(cell) for cell in row) for row in self.capture_font().rows
            )
            drafts: dict[str, str] = {}
            model = self.stage(rows, drafts)
            self.install(model)
            self.snapshot, self.drafts = rows, dict(drafts)
            self.proof_chars = sum(len(row[0]) + 2 for row in rows)
            self.dirty, self.pending = False, False
            self.row_number.setRange(1, max(1, len(rows)))
            self.describe_row()
            self.status_line.setText(f"Captured {len(rows)} glyphs. " + HELP)

        def describe_row(self) -> None:
            """Show complete metadata and the saved local value for one glyph."""
            if not self.snapshot:
                self.row_detail.setPlainText("No glyphs in this snapshot.")
                return
            number = int(properties.value(self.row_number, "value"))
            if self.pending:
                if number != self.current_row:
                    self.row_number.setValue(self.current_row)
                    raise ValueError("Apply Draft before changing rows.")
                return
            self.current_row = number
            row = self.snapshot[number - 1]
            self.row_detail.setPlainText("\n".join(row))
            self.loading_field = True
            try:
                self.draft_field.setText(self.drafts.get(row[0], ""))
            finally:
                self.loading_field = False

        def field_edited(self) -> None:
            """Retain unsubmitted text until Apply Draft, Reset or explicit Discard."""
            if not self.loading_field:
                self.pending = self.dirty = True
                self.status_line.setText(
                    "Apply Draft before changing rows or exporting."
                )

        def apply_draft(self) -> None:
            """Validate a local edit before constructing the replacement model."""
            if not self.snapshot:
                raise ValueError("Open a font and Refresh first.")
            name = self.snapshot[int(properties.value(self.row_number, "value")) - 1][0]
            text = validate_draft(
                checked(str(properties.value(self.draft_field, "text")))
            )
            drafts = {**self.drafts, name: text}
            # Adjust the cached budget and construct only this row's proof string.
            row_index = int(properties.value(self.row_number, "value")) - 1
            previous_count = int(self.drafts.get(name, "1"))
            total = self.proof_chars + (int(text) - previous_count) * (len(name) + 1)
            if total > MAX_PROOF_CHARS:
                raise ValueError(
                    "Proof exceeds two million characters. Reduce repeat counts."
                )
            display = build_rows((self.snapshot[row_index],), {name: text})[0]
            self.owned_model.item(row_index, 1).setText(display[1])
            self.owned_model.item(row_index, 2).setText(display[2])
            self.proof_chars = total
            self.drafts, self.dirty, self.pending = drafts, True, False
            self.status_line.setText("Local draft changed. Export New before closing.")

        def copy_report(self) -> None:
            """Copy the full captured report, including rows beyond the visible page."""
            if self.pending:
                raise ValueError("Apply Draft before exporting or copying.")
            if self.owned_model is None:
                raise ValueError("Read a snapshot before copying.")
            gui.QApplication.clipboard().setText(
                checked(report(self.snapshot, self.drafts))
            )
            self.status_line.setText(
                "Report copied. Use Export New to save local drafts."
            )

        def export_report(self) -> None:
            """Write UTF-8 to a new absolute path; never overwrite an existing file."""
            if self.pending:
                raise ValueError("Apply Draft before exporting or copying.")
            if self.owned_model is None:
                raise ValueError("Read a snapshot before exporting.")
            content = checked(report(self.snapshot, self.drafts))
            path = Path(str(properties.value(self.export_field, "text"))).expanduser()
            if not path.is_absolute():
                raise ValueError("Enter an absolute new report path.")
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            self.dirty = False
            self.status_line.setText("Report exported. Font data stays unchanged.")

        def discard(self) -> None:
            """Explicitly discard local changes before requesting safe Close."""
            self.dirty = False
            self.close()

        def destroyed_owner(self) -> None:
            """Fence callbacks when the parent destroys the window externally."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Refuse unsaved edits and failed disconnects; detach views last."""
            if self.dirty:
                self.status_line.setText(
                    "Unsaved draft. Export New or Discard and Close."
                )
                event.ignore()
                return
            if not self.scope.finish():
                event.ignore()
                return
            try:
                if hasattr(self, "table_view"):
                    self.table_view.setModel(None)
                if self.owned_model is not None:
                    self.owned_model.deleteLater()
                    self.owned_model = None
            except Exception as error:  # noqa: BLE001 - contain native close failures
                self.status_line.setText(f"Close paused: {error}. Retry window Close.")
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.populate()
    except Exception:
        panel.dirty = False
        panel.close()
        raise
    try:
        panel.refresh()
    except (ValueError, RuntimeError, TimeoutError, UnicodeError) as error:
        panel.status_line.setText(str(error))
    panel.show()
    return panel


def main() -> None:
    """Use the existing FontLab application and public lazy Fly aliases."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
