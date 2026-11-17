# this_file: Scripts/Insights/Glyph List.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (no reference code copied):
# _reference/exp111_pyTSon-Scripts/include/ts3widgets/filetransfer.py:660 — source licence unresolved; see catalog/insights.json.
"""Demonstrate glyph list with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    names = ("A", "Aacute", "H", "O", "space")
    with S.Session(qt, "Sample glyph names — list model", gui.QWidget()) as session:
        handle = session.h
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
            prefix = str(S.value(query, "text")).casefold()
            model.setStringList([n for n in names if n.casefold().startswith(prefix)])

        handle.model = model
        handle.connect_old(button, "clicked()", apply)
        handle.controls.update(filter=query, apply=button, view=view)
        handle.inspect_ui = lambda: {
            "prefix": str(S.value(query, "text")),
            "glyph_names": list(model.stringList()),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_glyph-list", "Glyph List")


if __name__ == "__main__":
    main()
