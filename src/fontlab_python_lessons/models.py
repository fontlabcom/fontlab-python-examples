# this_file: src/fontlab_python_lessons/models.py
# SPDX-License-Identifier: Apache-2.0
"""Build an immutable Qt table model from real, already measured glyph rows.

Use PythonQt.QtGui.QAbstractTableModel in FontLab. Construct a new model when
Refresh succeeds; retain no native glyph wrappers and expose no editing method.
"""
from typing import Any

from .domain import Metric


def metrics_model(qt: Any, rows: tuple[Metric, ...], parent: Any) -> Any:
    """Return a parent-owned table model with exact raw numeric display values.

    The Qt model contract requires rowCount, columnCount and data. Valid child
    parents have no rows/columns because this is a flat table, not a tree.
    Missing layer/outline values display an em dash; zero displays as zero.
    """
    core, gui = qt.QtCore, qt.QtGui
    headings = ("Glyph", "Advance", "LSB")

    class MetricsModel(gui.QAbstractTableModel):
        """Read-only plain rows, with Python ownership retained by the dialog."""

        def rowCount(self, parent: Any = None) -> int:
            return 0 if parent is not None and parent.isValid() else len(rows)

        def columnCount(self, parent: Any = None) -> int:
            return 0 if parent is not None and parent.isValid() else len(headings)

        def data(self, index: Any, role: int = core.Qt.DisplayRole) -> Any:
            if not index.isValid() or not 0 <= index.row() < len(rows):
                return None
            if not 0 <= index.column() < len(headings):
                return None
            if role == core.Qt.DisplayRole:
                row = rows[index.row()]
                value = (row.name, row.advance, row.lsb)[index.column()]
                return "—" if value is None else value
            if role == core.Qt.TextAlignmentRole and index.column():
                return int(core.Qt.AlignRight | core.Qt.AlignVCenter)
            return None

        def headerData(self, section: int, orientation: int,
                       role: int = core.Qt.DisplayRole) -> Any:
            if role == core.Qt.DisplayRole and orientation == core.Qt.Horizontal:
                return headings[section] if 0 <= section < len(headings) else None
            return None

        def flags(self, index: Any) -> Any:
            if not index.isValid():
                return core.Qt.NoItemFlags
            return core.Qt.ItemIsEnabled | core.Qt.ItemIsSelectable

    return MetricsModel(parent)
