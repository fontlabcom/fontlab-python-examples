# this_file: tests/test_official_interaction_regressions.py
"""Reported native interactions, with deliberately lossy PythonQt doubles."""

import ast

import pytest

from fontlab_python_examples.official import read
from tests.test_official_batch import ROOT
from tests.test_official_batch import official_qt as official_qt  # noqa: PLC0414


def test_every_port_avoids_sender():
    calls = []
    for path in (ROOT / "ports").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "sender"
            ):
                calls.append(f"{path.name}:{node.lineno}")
    assert not calls, f"PythonQt slots have no sender: {calls}"


def test_table_lookup_loses_python_subclass(official_qt):
    qt, _ = official_qt

    class Cell(qt.QtGui.QTableWidgetItem):
        def formula(self):
            return "lost"

    table = qt.QtGui.QTableWidget(1, 1)
    table.setItem(0, 0, Cell("raw"))
    item = table.item(0, 0)
    assert not isinstance(item, Cell), "Native wrappers lose Python subclass methods"
    with pytest.raises(AttributeError):
        item.formula()
    item.setText("changed")
    assert read(table.item(0, 0), "text") == "changed", "Wrappers share native data"
