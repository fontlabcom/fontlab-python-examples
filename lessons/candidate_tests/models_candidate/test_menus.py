# this_file: lessons/candidate_tests/models_candidate/test_menus.py
"""Execute the three real menu entry points without opening a native window."""

import importlib.util
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "relative,lesson",
    [
        ("Models/Glyph Name Filter.py", "glyph-name-filter"),
        ("Models/Glyph Metrics Model.py", "glyph-metrics-model"),
        ("Forms/Glyph Metrics Form.py", "glyph-metrics-form"),
    ],
)
def test_menu_when_imported_and_executed_then_launches_only_its_lesson(
    monkeypatch, relative, lesson
):
    calls = []
    monkeypatch.setattr(sys, "dont_write_bytecode", True)
    monkeypatch.setitem(
        sys.modules, "fontlab_python_lessons", SimpleNamespace(launch=calls.append)
    )
    paths = [ROOT / "Scripts" / relative]
    checkout_menu = ROOT.parent / "Scripts" / relative
    if checkout_menu.is_file():
        paths.append(checkout_menu)
    for path in paths:
        calls.clear()
        spec = importlib.util.spec_from_file_location("owned_lesson_menu", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert not calls, "Import must not launch a dialog"
        runpy.run_path(str(path), run_name="__main__")
        assert calls == [lesson], "The menu must launch exactly its documented lesson"
    normalize = lambda path: "\n".join(line for line in path.read_text().splitlines() if not line.startswith("# this_file:"))
    assert len({normalize(path) for path in paths}) == 1, "Checkout and installed menu bodies must agree"
