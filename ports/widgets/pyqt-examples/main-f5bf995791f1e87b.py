# this_file: ports/widgets/pyqt-examples/main-f5bf995791f1e87b.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/12 QTreeView example in Python/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from pathlib import Path
from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    view = qt.QtGui.QTreeView()
    model = qt.QtGui.QDirModel(view)
    home = str(Path.home())
    view.setModel(model)
    view.setRootIndex(model.index(home))
    handle = ExampleHandle(
        view,
        lambda: {
            "root_path": str(model.filePath(view.rootIndex())),
            "row_count": int(model.rowCount(view.rootIndex())),
            "column_count": int(model.columnCount(view.rootIndex())),
        },
    )
    handle.model = model
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("f5bf995791f1e87b")
