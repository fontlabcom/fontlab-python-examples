# this_file: examples/pythonqt/glyph_table_model.py
# SPDX-License-Identifier: Apache-2.0
"""What: A sortable, filterable table of the current font's glyphs.
Shows: QStandardItemModel + QSortFilterProxyModel + QTableView from
PythonQt.QtGui, a line edit that filters rows as you type, and numeric sorting.
Run: run from the Scripts menu with a font open. Type in the box to filter by
glyph name; click a column header to sort. Selecting rows changes nothing in
the font; this is a read-only view.
Setup: FontLab 9, Python 3.11, Fly with App (fly.ap.scripting).

Item models and views live in PythonQt.QtGui (there is no QtWidgets). The model
holds plain Python values; numbers are stored as numbers so they sort as
numbers, not as text.
"""

from __future__ import annotations

from typing import Any

KEY = "pythonqt-example-glyph-table"
HEADERS = ("Name", "Layers", "Advance")


def read(owner: Any, name: str) -> Any:
    """Return a Qt-style property whether PythonQt exposes it as value or method."""
    item = getattr(owner, name)
    return item() if callable(item) else item


def rows(font: Any) -> list[tuple[str, int, float]]:
    """One (name, layer count, advance of the active layer) row per glyph."""
    result = []
    for glyph in read(font, "glyphs"):
        layer = read(glyph, "activeLayer")
        advance = float(read(layer, "advanceWidth")) if layer is not None else 0.0
        result.append((str(read(glyph, "name")), len(list(read(glyph, "layers") or ())), advance))
    return result


def build(parent: Any) -> Any:
    from fly import fl, qt

    font = fl.CurrentFont()
    if font is None:
        raise RuntimeError("Open a font first.")
    core, gui = qt.QtCore, qt.QtGui
    panel = gui.QWidget(parent)
    panel.setWindowFlags(core.Qt.Tool)
    panel.setWindowTitle("Glyph Table")
    panel.setAttribute(core.Qt.WA_DeleteOnClose)
    panel.resize(420, 480)

    model = gui.QStandardItemModel(0, len(HEADERS), panel)
    model.setHorizontalHeaderLabels(list(HEADERS))
    for name, layers, advance in rows(font):
        items = []
        for value in (name, layers, advance):
            item = gui.QStandardItem()
            # EditRole carries the real value, so sorting compares numbers as numbers.
            item.setData(value, core.Qt.EditRole)
            item.setEditable(False)
            items.append(item)
        model.appendRow(items)

    proxy = gui.QSortFilterProxyModel(panel)  # Sorting/filtering without touching the model.
    proxy.setSourceModel(model)
    proxy.setFilterKeyColumn(0)
    proxy.setFilterCaseSensitivity(core.Qt.CaseInsensitive)
    proxy.setSortRole(core.Qt.EditRole)

    view = gui.QTableView(panel)
    view.setModel(proxy)
    view.setSortingEnabled(True)
    view.setSelectionBehavior(gui.QAbstractItemView.SelectRows)

    box = gui.QLineEdit(panel)
    box.setPlaceholderText("Filter by glyph name")
    # Wrap the slot so it accepts and ignores the signal's text argument.
    box.textChanged.connect(lambda text="": proxy.setFilterFixedString(str(text)))

    layout = gui.QVBoxLayout(panel)
    layout.addWidget(box)
    layout.addWidget(view)
    return panel


def main() -> Any:
    from fly.ap.scripting import show_script_dialog

    return show_script_dialog(build, KEY)


if __name__ == "__main__":
    main()
