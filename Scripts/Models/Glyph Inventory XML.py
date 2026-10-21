# this_file: Scripts/Models/Glyph Inventory XML.py
# SPDX-License-Identifier: Apache-2.0
"""What: Export the current font's glyph names, Unicode values and revision dates.
How: Read the App glyph catalogue and build XML elements with the standard
library. Escape names and refuse characters that XML cannot represent.
Why: Explicit elements retain every Unicode assignment for later scripts.
Usage: Open a font and Refresh. Inspect the rows, then Copy Report or Export New.
Benefit: Feed a small glyph inventory to a scripting or comparison pipeline.
Requires: FontLab 9, Python 3.11, Fly and App glyph_catalog, draft_signals and
qt_properties. Export requires a new absolute path and never overwrites a file.

Independent rewrite of the Qt simpledommodel example idea. Based on the author's own FontLab sample,
Apache-2.0.
Source: rescued/part2/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py
SHA256: c17809b93a3fff1601c20e15f233edbf687f023430e86bf1986772e38bf712d6
Source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py
SHA256: 50abde2890c2ca53384733ee94f77b54e3b4b7783efba2a965fc8b68a9becb42
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


TITLE = "Glyph Inventory XML"
HEADERS = ("Glyph name", "Unicode", "Modified")
HELP = "Open a font and Refresh. Inspect the rows, then Copy Report or Export New."


def build_rows(rows: Rows) -> Rows:
    """Show the three source columns before XML serialization."""
    return rows


def report(rows: Rows) -> str:
    """Build an escaped XML inventory with one element per glyph and scalar."""
    from xml.etree.ElementTree import Element, SubElement, tostring

    for row in rows:
        for text in row:
            if any(
                ord(char) < 32 and char not in "\t\n" or ord(char) in (0xFFFE, 0xFFFF)
                for char in text
            ):
                raise ValueError("Metadata contains an invalid XML character.")
    root = Element("glyph-inventory")
    for name, unicodes, modified in rows:
        glyph = SubElement(root, "glyph", name=name, modified=modified)
        for token in unicodes.split():
            SubElement(glyph, "unicode").text = token
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        + tostring(root, encoding="unicode")
        + "\n"
    )


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
            self.capture_font = capture
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
            self.button("Refresh", self.refresh)
            self.export_field = gui.QLineEdit(self)
            self.export_field.setPlaceholderText("Absolute NEW report path")
            self.stack.addWidget(self.export_field)
            self.button("Copy Report", self.copy_report)
            self.button("Export New", self.export_report)
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
                        item.setEditable(False)
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
            """Capture first. A failed read or model build keeps the prior result."""
            rows = tuple(
                tuple(checked(cell) for cell in row) for row in self.capture_font().rows
            )
            model = self.stage(build_rows(rows))
            self.install(model)
            self.snapshot = rows
            self.status_line.setText(f"Captured {len(rows)} glyphs.")

        def copy_report(self) -> None:
            """Copy the complete report. Refuse a missing capture."""
            if self.owned_model is None:
                raise ValueError("Refresh first.")

            gui.QApplication.clipboard().setText(checked(report(self.snapshot)))
            self.status_line.setText("Report copied.")

        def export_report(self) -> None:
            """Validate before creating an exclusive UTF-8 output file."""
            if self.owned_model is None:
                raise ValueError("Refresh first.")

            content = checked(report(self.snapshot))
            path = Path(str(properties.value(self.export_field, "text"))).expanduser()
            if not path.is_absolute():
                raise ValueError("Enter an absolute new report path.")
            with path.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)

            self.status_line.setText("Report exported.")

        def destroyed_owner(self) -> None:
            """Fence retained callbacks when the native parent destroys the panel."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Contain cleanup failures and retain ownership for a Close retry."""
            try:
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
