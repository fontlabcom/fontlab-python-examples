# this_file: Scripts/Drag And Drop/Font Drop Inspector.py
# SPDX-License-Identifier: Apache-2.0
"""Check dropped text against the current font and inspect drag formats.

Open a font and Refresh, then drop text or enter it and choose Use input.
The report lists each nonspace character with every matching glyph name.
Uncovered characters show MISSING. Check at most 5,000 characters at a time.
Drop URLs to inspect paths without opening them. Binary drops show format
names only. Copy or drag the report to document drag/drop behavior in scripts.
Plain-text display avoids interpreting HTML. No font data is changed.
Requires FontLab 9, Python 3.11 and Fly.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

TITLE = "Font Drop Inspector"
KEY = "drag_drop_dropsite"
HELP = (
    "Drop text or local font/UFO URLs to inspect their MIME formats and font coverage."
)
PLACEHOLDER = "Text to inspect"


def coverage_report(facts: Any, text: str) -> str:
    """Report every scalar occurrence with all FontLab matches in source order."""
    if len(text) > 5000:
        raise ValueError("Check at most 5,000 characters at a time.")
    if facts is None:
        raise ValueError("Open a font and refresh first.")
    if any(0xD800 <= ord(char) <= 0xDFFF for char in text):
        raise ValueError("Text contains an incomplete Unicode character.")
    mapping: dict[int, list[str]] = {}
    for row in facts.rows:
        for code in row.unicodes:
            mapping.setdefault(code, []).append(row.name)
    return (
        "\n".join(
            f"{i}: U+{ord(char):04X} → {', '.join(mapping.get(ord(char), [])) or 'MISSING'}"
            for i, char in enumerate(text, 1)
            if not char.isspace()
        )
        or "No text received."
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
            """Drag the selected source rows."""
            self.owner.drag_selected()

        def dragEnterEvent(self, event: Any) -> None:
            """Accept supported payloads; refuse unrelated drags."""
            if event.mimeData().formats():
                event.setDropAction(core.Qt.CopyAction)
                event.accept()
            else:
                event.ignore()

        def dragMoveEvent(self, event: Any) -> None:
            """Update acceptance while the pointer moves."""
            self.dragEnterEvent(event)

        def dropEvent(self, event: Any) -> None:
            """Apply a valid local drop and report refusals."""
            try:
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
                ("Clear", self.clear),
                ("Copy output", self.copy_output),
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
            self.output.clear()

        def changed(self) -> None:
            """Rebuild the output from the current local state."""

        def use_input(self) -> None:
            """Use the entered text, then clear it after success."""
            self.output.setPlainText(
                coverage_report(self.facts, str(value(self.entry, "text")))
            )
            self.entry.clear()

        def receive(self, mime: Any) -> None:
            """Validate the complete drop before updating local rows."""
            formats = [str(name) for name in mime.formats()]
            lines = ["MIME formats:", *formats]
            if mime.hasUrls():
                urls = mime.urls()
                lines.append("Dropped URLs (not opened):")
                lines.extend(
                    str(url.toLocalFile()) if url.isLocalFile() else str(url.toString())
                    for url in urls
                )
            elif mime.hasText():
                text = str(mime.text())
                self.entry.setText(text)
                try:
                    lines.append(coverage_report(self.facts, text))
                except ValueError as error:
                    lines.append(str(error))
            else:
                lines.append("No text or URLs; binary content was not decoded.")
            self.items.clear()
            self.items.addItems(formats)
            self.output.setPlainText("\n".join(lines))

        def output_mime(self) -> Any:
            """Build the advertised export formats."""
            text = str(value(self.output, "plainText"))
            if not text:
                raise ValueError("Drop content before dragging the inspection report.")
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
