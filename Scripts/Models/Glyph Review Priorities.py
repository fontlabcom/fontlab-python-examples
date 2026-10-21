# this_file: Scripts/Models/Glyph Review Priorities.py
# SPDX-License-Identifier: Apache-2.0
"""What: Keep a resumable zero-to-five-star review queue for the current font.
How: A painted five-star delegate sets scores by click and edits existing items.
Export JSON retains
the full queue; Import reloads it after checking glyph names, score ranges,
star consistency, duplicate keys and characters that PythonQt can replace.
Why: A portable queue can be resumed without modifying native glyph metadata.
Usage: Open a font and Refresh. Click within a star cell to set its score; Delete clears it.
Export New before closing. To resume, Refresh the matching font and Import an
exported queue. Import accepts UTF-8 BOM and normalizes CRLF or CR to LF.
Benefit: Carry a review across sessions and reject incompatible queues clearly.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Invalid imports keep the visible queue and current scores.

Independent rewrite of the Qt stardelegate example idea. Based on the author's own FontLab sample,
Apache-2.0.
Source: rescued/part2/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py
SHA256: ab5c5904d2ca3688def0ad17a8a48ac63f507e7a77778a888f14e04a89b0c079
Source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py
SHA256: d11286ceb3e9b813bbda21d1f820c224694722b2b3476c7b19a0791cd6fcc311
"""

from __future__ import annotations

import json
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


TITLE = "Glyph Review Priorities"
HEADERS = ("Glyph name", "Priority", "Score")
MAX_QUEUE_BYTES = 4 * 1024 * 1024
HELP = "Open a font and Refresh. Click within a star cell to set its score; Delete clears it."


def validate_draft(text: str) -> str:
    """Require an exact score token; refuse partial or decimal scores."""
    if text not in ("0", "1", "2", "3", "4", "5"):
        raise ValueError("Priority score, 0 to 5")
    return text


def build_rows(rows: Rows, drafts: dict[str, str]) -> Rows:
    """Display star text with an explicit numeric column for accessibility."""
    return tuple(
        (
            row[0],
            "★" * int(validate_draft(drafts.get(row[0], "0"))),
            drafts.get(row[0], "0"),
        )
        for row in rows
    )


def report(rows: Rows, drafts: dict[str, str]) -> str:
    """Serialize complete source metadata and local drafts without data loss."""
    return (
        json.dumps(
            {"columns": HEADERS, "rows": build_rows(rows, drafts), "drafts": drafts},
            ensure_ascii=True,
            indent=2,
        )
        + "\n"
    )


def score_at(position: int, width: int) -> int:
    """Map the five painted star slots to a bounded score; the left edge clears."""
    if width <= 0:
        raise ValueError("Star cell width must be positive.")
    return max(0, min(5, (position * 5 + width - 1) // width))


def delegate_type(qt: Any) -> type:
    """Paint five star slots and set a score directly from a cell click."""
    gui, core = qt.QtGui, qt.QtCore

    class StarDelegate(gui.QStyledItemDelegate):
        """Use Qt's painter and native item events; create no editor widgets."""

        def __init__(self, owner: Any) -> None:
            gui.QStyledItemDelegate.__init__(self, owner)
            self.owner_panel = owner

        def paint(self, painter: Any, option: Any, index: Any) -> None:
            """Paint filled and empty stars. Restore, but never end, Qt's painter."""
            painter.save()
            try:
                value = self.owner_panel.cell_value(index.row())
                selected = bool(option.state & gui.QStyle.State_Selected)
                background = gui.QPalette.Highlight if selected else gui.QPalette.Base
                ink = gui.QPalette.HighlightedText if selected else gui.QPalette.Text
                painter.fillRect(option.rect, option.palette.color(background))
                painter.setPen(option.palette.color(ink))
                painter.drawText(
                    option.rect, core.Qt.AlignCenter, "★" * value + "☆" * (5 - value)
                )
            except Exception as error:  # noqa: BLE001 - native paint boundary
                self.owner_panel.status_line.setText(str(error))
            finally:
                painter.restore()

        def sizeHint(self, option: Any, index: Any) -> Any:
            """Reserve a stable five-star click surface in every row."""
            return core.QSize(130, 28)

        def editorEvent(self, event: Any, model: Any, option: Any, index: Any) -> bool:
            """Set a clicked score, or clear it with Delete or Backspace."""
            if self.owner_panel.scope.closed:
                return False
            try:
                if (
                    event.type() == core.QEvent.MouseButtonRelease
                    and event.button() == core.Qt.LeftButton
                ):
                    value = score_at(
                        event.pos().x() - option.rect.left(), option.rect.width()
                    )
                elif event.type() == core.QEvent.KeyPress and event.key() in (
                    core.Qt.Key_Delete,
                    core.Qt.Key_Backspace,
                ):
                    value = 0
                else:
                    return False
                self.owner_panel.change_cell(index.row(), value)
                return True
            except Exception as error:  # noqa: BLE001 - native delegate boundary
                self.owner_panel.status_line.setText(str(error))
                return False

        def createEditor(self, parent: Any, option: Any, index: Any) -> Any:
            """Suppress text editing; mouse and clear-key events own score changes."""
            return None

    return StarDelegate


def import_queue(path: Path, names: set[str]) -> tuple[dict[str, str], str]:
    """Parse one exported queue at the boundary before changing any panel state."""
    if not path.is_absolute():
        raise ValueError("Enter an absolute queue source path.")
    if not path.is_file():
        raise ValueError("Queue source must be a regular file.")
    if path.stat().st_size > MAX_QUEUE_BYTES:
        raise ValueError("Queue exceeds the 4 MiB import limit.")
    with path.open(newline=None, encoding="utf-8-sig") as stream:
        bom = stream.buffer.peek(3).startswith(b"\xef\xbb\xbf")
        text = stream.read(MAX_QUEUE_BYTES + 1)
        endings = stream.newlines or ()
    if len(text.encode("utf-8")) > MAX_QUEUE_BYTES:
        raise ValueError("Queue exceeds the 4 MiB import limit.")
    checked(text)

    def unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        """Refuse duplicate keys instead of silently replacing review scores."""
        result = {}
        for name, value in pairs:
            if name in result:
                raise ValueError(f"Duplicate queue key: {name}.")
            result[name] = value
        return result

    payload = json.loads(text, object_pairs_hook=unique_pairs)
    if (
        not isinstance(payload, dict)
        or set(payload) != {"columns", "rows", "drafts"}
        or payload["columns"] != list(HEADERS)
    ):
        raise ValueError("Use a Glyph Review Priorities exported queue.")
    drafts = payload["drafts"]
    if not isinstance(drafts, dict) or not isinstance(payload["rows"], list):
        raise ValueError("Queue rows and drafts have invalid types.")  # noqa: TRY004 - malformed external file
    rows_seen = set()
    imported = {}
    for row in payload["rows"]:
        if (
            not isinstance(row, list)
            or len(row) != 3
            or any(not isinstance(cell, str) for cell in row)
        ):
            raise ValueError("Each queue row needs three text cells.")
        name, stars, score = (checked(cell) for cell in row)
        validate_draft(score)
        if name not in names or name in rows_seen or stars != "★" * int(score):
            raise ValueError(f"Unknown, duplicate or inconsistent queue glyph: {name}.")
        rows_seen.add(name)
        if score != "0":
            imported[name] = score
    for name, score in drafts.items():
        if not isinstance(name, str) or not isinstance(score, str):
            raise ValueError("Queue draft names and scores must be text.")  # noqa: TRY004 - malformed external file
        checked(name)
        checked(score)
        validate_draft(score)
        if (
            name not in names
            or name not in rows_seen
            or score != imported.get(name, "0")
        ):
            raise ValueError(f"Unknown or inconsistent queue draft: {name}.")
    notes = []
    if bom:
        notes.append("BOM removed.")
    if any(
        "\r" in ending
        for ending in ((endings,) if isinstance(endings, str) else endings)
    ):
        notes.append("Line endings converted to LF.")
    return imported, " ".join(notes)


def show(qt: Any, parent: Any = None, capture: Callable[[], Any] | None = None) -> Any:
    """Open through the existing host. Keep exact callback and model owners."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    if capture is None:
        import fly.ap.glyph_catalog as catalogue

        capture = catalogue.capture
    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own controls and stage captures before replacing visible results."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.snapshot: Rows = ()
            self.owned_model: Any = None
            self.editor_delegate: Any = None
            self.dirty = False
            self.capture_font = capture
            self.drafts: dict[str, str] = {}
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(820, 540)
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
            """Connect only after the module retains this window for cleanup."""
            self.scope.connect(
                self.destroyed,
                lambda *args: self.destroyed_owner(),
                closing=True,
                retry=True,
            )
            self.table_view = gui.QTableView(self)
            self.stack.addWidget(self.table_view)
            self.action_strip = gui.QHBoxLayout()
            self.stack.addLayout(self.action_strip)
            self.editor_delegate = delegate_type(qt)(self)
            self.table_view.setItemDelegateForColumn(1, self.editor_delegate)
            self.button("Refresh", self.refresh)
            self.source_field = gui.QLineEdit(self)
            self.source_field.setPlaceholderText("Absolute exported queue source path")
            self.stack.addWidget(self.source_field)
            self.button("Import", self.import_file)
            self.export_field = gui.QLineEdit(self)
            self.export_field.setPlaceholderText("Absolute NEW report path")
            self.stack.addWidget(self.export_field)
            self.button("Copy Report", self.copy_report)
            self.button("Export New", self.export_report)
            self.button("Discard Changes", self.discard_changes)
            self.button("Close", lambda: self.close(), closing=True)

        def button(
            self, label: str, action: Callable[[], Any], *, closing: bool = False
        ) -> None:
            """Own a plain callback that accepts native clicked(bool)."""
            control = gui.QPushButton(label, self)
            self.action_strip.addWidget(control)
            self.scope.connect(
                control.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def stage(self, display: Rows) -> Any:
            """Build one model per capture. Cell edits never call this function."""
            model = gui.QStandardItemModel(self)
            try:
                model.setHorizontalHeaderLabels(list(HEADERS))
                for row in display:
                    cells = []
                    for column, text in enumerate(row):
                        item = gui.QStandardItem(checked(text))
                        item.setEditable(column == 1)
                        cells.append(item)
                    model.appendRow(cells)
            except Exception:
                model.deleteLater()
                raise
            return model

        def install(self, model: Any) -> None:
            """Swap a complete model, then release its obsolete selection owner."""
            old = self.owned_model
            selection = self.table_view.selectionModel()
            self.table_view.setModel(model)
            self.owned_model = model
            if selection is not None:
                selection.deleteLater()
            if old is not None:
                old.deleteLater()

        def refresh(self) -> None:
            """Capture names before replacing the queue. Refuse unsaved work."""
            if self.dirty:
                raise ValueError("Export or Discard Changes before Refresh.")
            rows = tuple(
                tuple(checked(cell) for cell in row) for row in self.capture_font().rows
            )
            self.install(self.stage(build_rows(rows, {})))
            self.snapshot, self.drafts = rows, {}
            self.status_line.setText(
                f"{len(rows)} glyphs ready for review. Click stars to edit; Delete clears."
            )

        def cell_value(self, row: int) -> int:
            """Return the local score for the delegate's current glyph row."""
            return int(self.drafts.get(self.snapshot[row][0], "0"))

        def change_cell(self, row: int, value: int) -> None:
            """Update only the edited star and score items in the existing model."""
            score = validate_draft(str(value))
            name = self.snapshot[row][0]
            previous = self.drafts.get(name, "0")
            if score == previous:
                return
            if score == "0":
                self.drafts.pop(name, None)
            else:
                self.drafts[name] = score
            self.owned_model.item(row, 1).setText("★" * int(score))
            self.owned_model.item(row, 2).setText(score)
            self.dirty = True

        def import_file(self) -> None:
            """Validate the whole queue before replacing scores; preserve invalid drafts."""
            if self.dirty:
                raise ValueError("Export or Discard Changes before Import.")
            if self.owned_model is None:
                raise ValueError("Open a font and Refresh first.")
            path = Path(str(properties.value(self.source_field, "text"))).expanduser()
            imported, notes = import_queue(path, {row[0] for row in self.snapshot})
            for row, (name, _unicodes, _modified) in enumerate(self.snapshot):
                before, after = self.drafts.get(name, "0"), imported.get(name, "0")
                if before != after:
                    self.owned_model.item(row, 1).setText("★" * int(after))
                    self.owned_model.item(row, 2).setText(after)
            self.drafts = imported
            self.status_line.setText("Queue imported. " + notes)

        def discard_changes(self) -> None:
            """Clear local scores explicitly without re-reading native glyphs."""
            for row, record in enumerate(self.snapshot):
                if record[0] in self.drafts:
                    self.owned_model.item(row, 1).setText("")
                    self.owned_model.item(row, 2).setText("0")
            self.drafts.clear()
            self.dirty = False

        def copy_report(self) -> None:
            """Copy the complete report. Refuse a missing capture."""
            if self.owned_model is None:
                raise ValueError("Refresh first.")
            gui.QApplication.clipboard().setText(
                checked(report(self.snapshot, self.drafts))
            )
            self.status_line.setText("Report copied.")

        def export_report(self) -> None:
            """Validate before creating an exclusive UTF-8 output file."""
            if self.owned_model is None:
                raise ValueError("Refresh first.")
            content = checked(report(self.snapshot, self.drafts))
            path = Path(str(properties.value(self.export_field, "text"))).expanduser()
            if not path.is_absolute():
                raise ValueError("Enter an absolute new report path.")
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            self.dirty = False
            self.status_line.setText("Report exported.")

        def destroyed_owner(self) -> None:
            """Fence retained callbacks when the native parent destroys the panel."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Contain cleanup failures and retain ownership for a Close retry."""
            try:
                if self.dirty:
                    self.status_line.setText(
                        "Unsaved queue. Export or Discard Changes before Close."
                    )
                    event.ignore()
                    return
                if not self.scope.finish():
                    event.ignore()
                    return
                if hasattr(self, "table_view"):
                    self.table_view.setItemDelegate(None)
                    self.table_view.setModel(None)
                if self.owned_model is not None:
                    self.owned_model.deleteLater()
                    self.owned_model = None
            except Exception as error:  # noqa: BLE001 - contain native cleanup errors
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
    except (ValueError, RuntimeError, TimeoutError) as error:
        panel.status_line.setText(str(error))
    panel.show()
    return panel


def main() -> None:
    """Use FontLab's application, main window and lazy Fly namespaces."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
