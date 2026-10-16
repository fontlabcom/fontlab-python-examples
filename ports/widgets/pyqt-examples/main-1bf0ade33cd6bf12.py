# this_file: ports/widgets/pyqt-examples/main-1bf0ade33cd6bf12.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/13 PyQt6 QListView/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    view = qt.QtGui.QListView()
    model = qt.QtGui.QStringListModel(  # PythonQt places it in QtGui
        ["An element", "Another element", "Yay! Another one."], view
    )
    view.setModel(model)
    handle = ExampleHandle(
        view,
        lambda: {
            "row_count": int(model.rowCount()),
            "strings": list(model.stringList()),
        },
    )
    handle.model = model
    return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("1bf0ade33cd6bf12")
