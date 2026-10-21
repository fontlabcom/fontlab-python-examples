# this_file: Scripts/Drag And Drop/Proof Word Magnets.py
# SPDX-License-Identifier: Apache-2.0
"""Arrange proof words for a FontLab Glyph window text bar.

Type words and choose Use input, or drop plain text. Drag rows to reorder them;
select rows and choose Remove selected to delete individual words. Repeated
words remain separate. Copy proof text copies the assembled line to the
clipboard; paste it into a Glyph window text bar, or drag output there.
Refresh checks the current font for missing characters. Without a font, the
local draft still works. The panel uses the UI font and does not render outlines.
Prepare quick proof variations without changing glyphs or metrics.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

TITLE = "Proof Word Magnets"
KEY = "drag_drop_fridgemagnets"
HELP = (
    "Drop or type proof words. Drag rows to reorder; copy or drag the assembled proof."
)
PLACEHOLDER = "Proof words to append"
REORDER = True


def words(text: str) -> tuple[str, ...]:
    """Split proof text at whitespace; retain repeats and reject lone surrogates."""
    if any(0xD800 <= ord(char) <= 0xDFFF for char in text):
        raise ValueError("Text contains an incomplete Unicode character.")
    return tuple(text.split())


def missing_characters(facts: Any, text: str) -> tuple[str, ...]:
    """Return unique uncovered nonspace scalars in first-occurrence order."""
    if facts is None:
        raise ValueError("Open a font and refresh to check proof coverage.")
    covered = {code for row in facts.rows for code in row.unicodes}
    return tuple(
        dict.fromkeys(
            f"U+{ord(char):04X}"
            for char in text
            if not char.isspace() and ord(char) not in covered
        )
    )


def panel_type(qt: Any, capture: Callable[[], Any]) -> type:
    """Build an owned modeless panel. Inject Qt and capture for offline checks."""
    from fly.ap.draft_signals import Scope
    from fly.ap.qt_properties import value

    gui, core = qt.QtGui, qt.QtCore

    class Items(gui.QListWidget):
        """Display staged rows and route drag events."""

        def __init__(self, owner: Any) -> None:
            """Create controls and retain their Python callbacks."""
            gui.QListWidget.__init__(self, owner)
            self.owner = owner

        def startDrag(self, actions: Any) -> None:
            """Drag selected rows or reorder the local proof."""
            if REORDER:
                self.owner.busy = True
                try:
                    gui.QListWidget.startDrag(self, actions)
                finally:
                    self.owner.busy = False
                    self.owner.changed()
            else:
                self.owner.drag_selected()

        def dragEnterEvent(self, event: Any) -> None:
            """Accept supported payloads; refuse unrelated drags."""
            if REORDER and event.source() == self:
                gui.QListWidget.dragEnterEvent(self, event)
            elif event.mimeData().hasText() or event.mimeData().hasUrls():
                event.setDropAction(core.Qt.CopyAction)
                event.accept()
            else:
                event.ignore()

        def dragMoveEvent(self, event: Any) -> None:
            """Update acceptance while the pointer moves."""
            if REORDER and event.source() == self:
                gui.QListWidget.dragMoveEvent(self, event)
            else:
                self.dragEnterEvent(event)

        def dropEvent(self, event: Any) -> None:
            """Apply a valid local drop and report refusals."""
            try:
                if REORDER and event.source() == self:
                    gui.QListWidget.dropEvent(self, event)
                    self.owner.changed()
                else:
                    self.owner.receive(event.mimeData())
                    event.setDropAction(core.Qt.CopyAction)
                    event.accept()
            except Exception as error:  # noqa: BLE001 - native callback boundary
                self.owner.failure(error)
                event.ignore()

    class Export(gui.QLabel):
        """Provide a drag handle for the current output."""

        def __init__(self, text: str, owner: Any) -> None:
            """Create controls and retain their Python callbacks."""
            gui.QLabel.__init__(self, text, owner)
            self.owner = owner

        def mousePressEvent(self, event: Any) -> None:
            """Remember the left-button drag origin."""
            self.origin = event.pos() if event.button() == core.Qt.LeftButton else None

        def mouseMoveEvent(self, event: Any) -> None:
            """Start export after the drag-distance threshold."""
            if self.origin is None or not event.buttons() & core.Qt.LeftButton:
                return
            point, origin = event.pos(), self.origin
            distance = abs(point.x() - origin.x()) + abs(point.y() - origin.y())
            if distance >= value(gui.QApplication, "startDragDistance"):
                self.origin = None
                self.owner.drag_output()

    class Panel(gui.QWidget):
        """Keep this tool and its callbacks alive until Close."""

        def __init__(self, parent: Any = None) -> None:
            """Create controls and retain their Python callbacks."""
            gui.QWidget.__init__(self, parent, core.Qt.Window)
            self.busy, self.facts = False, None
            self.scope = Scope(self.failure)
            self.terminal = Scope(self.failure)
            self.terminal.connect(
                self.destroyed, lambda *args: self.dispose(destroyed=True)
            )
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(640, 540)
            layout = gui.QVBoxLayout(self)
            layout.setContentsMargins(18, 18, 18, 18)
            heading = gui.QLabel(HELP, self)
            heading.setTextFormat(core.Qt.PlainText)
            heading.setWordWrap(True)
            layout.addWidget(heading)
            self.entry = gui.QLineEdit(self)
            self.entry.setPlaceholderText(PLACEHOLDER)
            layout.addWidget(self.entry)
            self.items = Items(self)
            self.items.setAcceptDrops(True)
            self.items.setDragEnabled(True)
            self.items.setSelectionMode(gui.QAbstractItemView.ExtendedSelection)
            if REORDER:
                self.items.setDragDropMode(gui.QAbstractItemView.InternalMove)
            layout.addWidget(self.items)
            self.output = gui.QPlainTextEdit(self)
            self.output.setReadOnly(True)
            layout.addWidget(self.output)
            self.export = Export("Drag output ↗", self)
            self.export.origin = None
            self.export.setStyleSheet(
                "padding: 10px; border: 1px solid #8596a0; border-radius: 5px;"
            )
            layout.addWidget(self.export)
            row = gui.QHBoxLayout()
            layout.addLayout(row)
            for label, action in (
                ("Refresh font", self.refresh),
                ("Use input", self.use_input),
                ("Remove selected", self.remove_selected),
                ("Clear", self.clear),
                ("Copy proof text", self.copy_output),
            ):
                button = gui.QPushButton(label, self)
                row.addWidget(button)
                self.scope.connect(button.clicked, lambda *args, fn=action: fn())
            self.status = gui.QLabel("", self)
            self.status.setTextFormat(core.Qt.PlainText)
            self.status.setWordWrap(True)
            layout.addWidget(self.status)
            self.refresh()

        def failure(self, error: Exception) -> None:
            """Report at the callback boundary; keep the panel available for retry."""
            self.status.setText(str(error))

        def text_items(self) -> tuple[str, ...]:
            """Read displayed rows in their current order."""
            return tuple(
                str(value(self.items.item(i), "text"))
                for i in range(value(self.items, "count"))
            )

        def refresh(self) -> None:
            """Capture the current font and clear stale facts on failure."""
            self.facts = None
            try:
                self.facts = capture()
                self.status.setText(
                    "Current-font snapshot captured. Refresh after changing fonts."
                )
                self.seed()
                self.changed()
            except Exception as error:  # noqa: BLE001 - native callback boundary
                self.facts = None
                self.invalidate()
                self.failure(error)

        def clear(self) -> None:
            """Remove the local draft and its displayed output."""
            self.items.clear()
            self.output.clear()
            self.status.setText("Draft cleared.")

        def copy_output(self) -> None:
            """Copy the current output to the clipboard."""
            text = str(value(self.output, "plainText"))
            if not text:
                raise ValueError("There is no output to copy.")
            gui.QApplication.clipboard().setText(text)

        def execute_drag(self, mime: Any) -> None:
            """Run a copy-only drag and release it on completion."""
            drag = gui.QDrag(self)
            drag.setMimeData(mime)
            self.busy = True
            try:
                drag.exec(core.Qt.CopyAction)
            finally:
                self.busy = False
                drag.deleteLater()

        def drag_output(self) -> None:
            """Export the prepared payload; show target errors."""
            try:
                self.execute_drag(self.output_mime())
            except Exception as error:  # noqa: BLE001 - native callback boundary
                self.failure(error)

        def drag_selected(self) -> None:
            """Export the selected source rows."""
            self.drag_output()

        def dispose(self, *, destroyed: bool = False) -> bool:
            """Drain owned signals, then remove the retained script-window key."""
            if not self.scope.finish(destroyed=destroyed):
                return False
            if not self.terminal.finish(destroyed=destroyed):
                return False
            import sys

            registry = getattr(sys, "_fontlab_samples", {})
            if registry.get(KEY) is self:
                registry.pop(KEY)
            self.facts = None
            return True

        def closeEvent(self, event: Any) -> None:
            """Refuse Close during drag or failed disconnect; delete after cleanup."""
            if self.busy or not self.dispose():
                event.ignore()
                return
            event.accept()
            self.deleteLater()

        def seed(self) -> None:
            """Prepare the display from the latest font capture."""

        def invalidate(self) -> None:
            """Remove data that belongs to an unavailable font."""
            # A local proof draft remains useful without font coverage.

        def changed(self) -> None:
            """Rebuild the output from the current local state."""
            text = " ".join(self.text_items())
            self.output.setPlainText(text)
            if self.facts is None:
                self.status.setText(
                    "Draft ready. Open a font and Refresh to check coverage."
                )
                return
            missing = missing_characters(self.facts, text)
            self.status.setText(
                "Missing: " + ", ".join(missing)
                if missing
                else "All proof characters are covered."
            )

        def remove_selected(self) -> None:
            """Remove only selected proof rows and rebuild output."""
            rows = sorted(
                (self.items.row(item) for item in self.items.selectedItems()),
                reverse=True,
            )
            if not rows:
                raise ValueError("Select rows to remove.")
            for row in rows:
                self.items.takeItem(row)
            self.changed()

        def use_input(self) -> None:
            """Use the entered text, then clear it after success."""
            tokens = words(str(value(self.entry, "text")))
            self.items.addItems(tokens)
            self.changed()
            self.entry.clear()

        def receive(self, mime: Any) -> None:
            """Validate the complete drop before updating local rows."""
            if not mime.hasText() or mime.hasUrls():
                raise ValueError("Drop proof text, not file URLs.")
            tokens = words(str(mime.text()))
            self.items.addItems(tokens)
            self.changed()

        def output_mime(self) -> Any:
            """Build the advertised export formats."""
            text = " ".join(self.text_items())
            if not text:
                raise ValueError("Add proof words before exporting.")
            mime = core.QMimeData()
            mime.setText(text)
            return mime

    return Panel


def main() -> Any:
    """Show the retained modeless panel through Fly."""
    from fly import qt
    from fly.ap.character_map_capture import capture
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(panel_type(qt, capture), KEY)


if __name__ == "__main__":
    main()
