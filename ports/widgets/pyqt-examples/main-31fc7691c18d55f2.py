# this_file: ports/widgets/pyqt-examples/main-31fc7691c18d55f2.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/14 QAbstractTableModel example/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle

HEADERS = ["Scientist name", "Birthdate", "Contribution"]
ROWS = [
    ("Newton", "1643-01-04", "Classical mechanics"),
    ("Einstein", "1879-03-14", "Relativity"),
    ("Darwin", "1809-02-12", "Evolution"),
]


def build(qt: Any) -> ExampleHandle:
    core = qt.QtCore

    class TableModel(core.QAbstractTableModel):
        def rowCount(self, parent: Any = None) -> int:
            return 0 if parent is not None and parent.isValid() else len(ROWS)

        def columnCount(self, parent: Any = None) -> int:
            return 0 if parent is not None and parent.isValid() else len(HEADERS)

        def data(self, index: Any, role: int = core.Qt.DisplayRole) -> Any:
            if role != core.Qt.DisplayRole or not index.isValid():
                return None
            row, column = index.row(), index.column()
            if 0 <= row < len(ROWS) and 0 <= column < len(HEADERS):
                return ROWS[row][column]
            return None

        def headerData(
            self, section: int, orientation: int, role: int = core.Qt.DisplayRole
        ) -> Any:
            if (
                role == core.Qt.DisplayRole
                and orientation == core.Qt.Horizontal
                and 0 <= section < len(HEADERS)
            ):
                return HEADERS[section]
            return None

    view = qt.QtGui.QTableView()
    model = TableModel(view)
    view.setModel(model)
    handle = ExampleHandle(
        view,
        lambda: {
            "row_count": model.rowCount(),
            "column_count": model.columnCount(),
            "headers": [
                model.headerData(i, core.Qt.Horizontal)
                for i in range(model.columnCount())
            ],
            "rows": [
                [model.data(model.index(r, c)) for c in range(model.columnCount())]
                for r in range(model.rowCount())
            ],
        },
    )
    handle.model = model
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("31fc7691c18d55f2")
