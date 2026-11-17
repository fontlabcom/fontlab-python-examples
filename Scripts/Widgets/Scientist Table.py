# this_file: Scripts/Widgets/Scientist Table.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/14 QAbstractTableModel example/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
"""Show scientist table using FontLab PythonQt; no font data is changed."""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle

HEADERS = ["Scientist name", "Birthdate", "Contribution"]
ROWS = [
    ("Newton", "1643-01-04", "Classical mechanics"),
    ("Einstein", "1879-03-14", "Relativity"),
    ("Darwin", "1809-02-12", "Evolution"),
]


def build(qt: Any) -> ExampleHandle:
    core = qt.QtCore

    class TableModel(qt.QtGui.QAbstractTableModel):  # PythonQt places it in QtGui
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



def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_main-31fc7691c18d55f2', 'Scientist Table')


if __name__ == "__main__":
    main()

# ## MIT License
# 
# Upstream authorship attribution: Michael Herrmann. No copyright year or notice
# appears in the reviewed original files; none is inferred here.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
