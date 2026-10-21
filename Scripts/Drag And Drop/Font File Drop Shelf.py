# this_file: Scripts/Drag And Drop/Font File Drop Shelf.py
# SPDX-License-Identifier: Apache-2.0
"""Collect font files and open selected entries in FontLab.

Drop local fonts or UFO folders, or enter an absolute path and choose Use input.
Select rows and choose Open in FontLab, or drag their file URLs to another window.
Copy output copies all staged paths for scripts. Clear empties the shelf.
The whole selection is checked before opening starts. A failed open stops the
batch and reports which files already opened. File contents are never changed.
No current font is required. Save repeated trips through the file dialog.
Opening relies on FontLab's own format support.
Requires FontLab 9, Python 3.11, Fly and native font-opening support.
Independent behaviour-only rewrite. Apache-2.0 (own earlier work).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

TITLE = "Font File Drop Shelf"
KEY = "drag_drop_draggableicons"
HELP = (
    "Drop local font files or UFO folders. Select rows and drag their URLs to FontLab."
)
PLACEHOLDER = "Absolute local font path"


def font_paths(paths: list[str]) -> tuple[str, ...]:
    """Accept a whole batch of existing absolute font files or UFO packages."""
    if not paths:
        raise ValueError("Drop local font files or UFO folders.")
    result = []
    for text in paths:
        path = Path(text)
        if not path.is_absolute():
            raise ValueError("Only absolute local paths are accepted.")
        suffix = path.suffix.lower()
        valid = path.is_dir() if suffix == ".ufo" else path.is_file()
        if (
            suffix
            not in {
                ".otf",
                ".ttf",
                ".ttc",
                ".otc",
                ".ufo",
                ".vfj",
                ".vfc",
                ".vfb",
                ".designspace",
            }
            or not valid
        ):
            raise ValueError(f"Not an existing supported font source: {text}")
        if str(path) not in result:
            result.append(str(path))
    return tuple(result)


def panel_type(qt: Any, open_font: Callable[[str], None]) -> type:
    """Build a file shelf with an injected FontLab opener."""
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
            if event.mimeData().hasText() or event.mimeData().hasUrls():
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
            self.busy = False
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
                ("Open in FontLab", self.open_selected),
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
            self.status.setText("Drop font paths, or enter an absolute path to stage.")

        def failure(self, error: Exception) -> None:
            """Report at the callback boundary; keep the panel available for retry."""
            self.status.setText(str(error))

        def text_items(self) -> tuple[str, ...]:
            """Read displayed rows in their current order."""
            return tuple(
                str(value(self.items.item(i), "text"))
                for i in range(value(self.items, "count"))
            )

        def clear(self) -> None:
            """Remove the local draft and its displayed output."""
            self.items.clear()
            self.output.clear()
            self.status.setText("Staged font paths cleared.")

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
            return True

        def closeEvent(self, event: Any) -> None:
            """Refuse Close during drag or failed disconnect; delete after cleanup."""
            if self.busy or not self.dispose():
                event.ignore()
                return
            event.accept()
            self.deleteLater()

        def changed(self) -> None:
            """Rebuild the output from the current local state."""
            self.output.setPlainText("\n".join(self.text_items()))

        def add_paths(self, paths: list[str]) -> None:
            """Stage a validated batch without duplicate paths."""
            complete = font_paths(paths)
            known = set(self.text_items())
            self.items.addItems([path for path in complete if path not in known])
            self.changed()
            self.status.setText(
                "Select staged fonts to open in FontLab or drag their file URLs."
            )

        def use_input(self) -> None:
            """Use the entered text, then clear it after success."""
            self.add_paths([str(value(self.entry, "text"))])
            self.entry.clear()

        def receive(self, mime: Any) -> None:
            """Validate the complete drop before updating local rows."""
            if not mime.hasUrls() or any(not url.isLocalFile() for url in mime.urls()):
                raise ValueError("Drop local file URLs only.")
            self.add_paths([str(url.toLocalFile()) for url in mime.urls()])

        def open_selected(self) -> None:
            """Validate selected font paths, then open them in order."""
            selected = self.items.selectedItems()
            if not selected:
                raise ValueError("Select rows to open")
            paths = font_paths([str(value(item, "text")) for item in selected])
            for count, path in enumerate(paths):
                try:
                    open_font(path)
                except Exception as error:
                    raise RuntimeError(
                        f"Opened {count} of {len(paths)} fonts; failed {path}: {error}"
                    ) from error
            self.status.setText(
                f"Opened {len(paths)} of {len(paths)} selected font paths in FontLab."
            )

        def output_mime(self) -> Any:
            """Build the advertised export formats."""
            selected = self.items.selectedItems()
            if not selected:
                raise ValueError("Select rows to drag")
            paths = font_paths([str(value(item, "text")) for item in selected])
            mime = core.QMimeData()
            mime.setUrls([core.QUrl.fromLocalFile(path) for path in paths])
            mime.setText("\n".join(paths))
            return mime

    return Panel


def open_in_fontlab(path: str) -> None:
    """Require one new workspace package; never infer success from return shape."""
    from fly import fl
    from fly.ap.controls import FontLab

    workspace = fl.flWorkspace.instance()
    before = {package.id for package in workspace.packages()}
    with FontLab() as host:
        result = host.open_font(path=path)
    if isinstance(result, dict) and result.get("status") == "error":
        raise RuntimeError(f"FontLab could not open {path}: {result}")
    added = {package.id for package in workspace.packages()} - before
    if len(added) != 1:
        raise RuntimeError(
            f"Could not confirm opening {path}: expected one new workspace package, found {len(added)}."
        )


def main() -> Any:
    """Show the shelf; defer native file-opening setup until the action runs."""
    from fly import qt
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(panel_type(qt, open_in_fontlab), KEY)


if __name__ == "__main__":
    main()
