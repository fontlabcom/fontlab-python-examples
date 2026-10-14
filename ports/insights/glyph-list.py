# this_file: ports/insights/glyph-list.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/exp111_pyTSon-Scripts/include/ts3widgets/filetransfer.py:660 — source licence unresolved; see catalog/insights.json.
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    names = ("A", "Aacute", "H", "O", "space")
    with owned(gui.QWidget(), "Sample glyph names — list model") as handle:
        window = handle.widget
        layout = gui.QVBoxLayout(window)
        query = gui.QLineEdit(window)
        query.setPlaceholderText("Glyph name prefix (empty shows all)")
        button = gui.QPushButton("Apply prefix", window)
        view = gui.QListView(window)
        model = gui.QStringListModel(list(names), window)
        view.setModel(model)
        for widget in (query, button, view):
            layout.addWidget(widget)

        def apply() -> None:
            prefix = str(query.text).casefold()
            model.setStringList([n for n in names if n.casefold().startswith(prefix)])

        handle.model = model
        handle.connect_old(button, "clicked()", apply)
        handle.controls.update(filter=query, apply=button, view=view)
        handle.inspect_ui = lambda: {
            "prefix": str(query.text),
            "glyph_names": list(model.stringList()),
        }
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("glyph-list")
