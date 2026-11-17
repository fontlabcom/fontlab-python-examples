# this_file: Scripts/Insights/Metrics Table.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/exp111_pyTSon-Scripts/include/ts3widgets/filetransfer.py:240 — source licence unresolved; see catalog/insights.json.
"""Demonstrate metrics table with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui, core = qt.QtGui, qt.QtCore
    rows = (("A", 600, 40), ("H", 620, 50), ("O", 640, 30))
    headers = ("Glyph", "Advance", "LSB")

    class Metrics(gui.QAbstractTableModel):
        """Immutable sample rows; no access to FontLab font data."""

        def rowCount(self, parent: Any = None) -> int:
            return 0 if parent is not None and parent.isValid() else len(rows)

        def columnCount(self, parent: Any = None) -> int:
            return 0 if parent is not None and parent.isValid() else len(headers)

        def data(self, index: Any, role: int = core.Qt.DisplayRole) -> Any:
            if role != core.Qt.DisplayRole or not index.isValid():
                return None
            row, column = index.row(), index.column()
            if 0 <= row < len(rows) and 0 <= column < len(headers):
                return rows[row][column]
            return None

        def headerData(
            self, section: int, orientation: int, role: int = core.Qt.DisplayRole
        ) -> Any:
            if (
                role == core.Qt.DisplayRole
                and orientation == core.Qt.Horizontal
                and 0 <= section < len(headers)
            ):
                return headers[section]
            return None

    with S.Session(qt, "Sample metrics — table model", gui.QTableView()) as session:
        handle = session.h
        model = Metrics(handle.widget)
        handle.widget.setModel(model)
        handle.model = model
        handle.inspect_ui = lambda: {
            "headers": list(headers),
            "rows": [list(row) for row in rows],
            "row_count": model.rowCount(),
            "column_count": model.columnCount(),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_metrics-table", "Metrics Table")


if __name__ == "__main__":
    main()
