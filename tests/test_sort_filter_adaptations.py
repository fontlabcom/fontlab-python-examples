# this_file: tests/test_sort_filter_adaptations.py
"""Both full part2 lessons replace their wrappers; original bytes remain external."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def adaptations():
    return json.loads((ROOT / "menu-adaptations.json").read_text())


def test_adaptations_when_loaded_then_two_full_part2_workflows_preserve_frozen_index():
    data = adaptations()
    assert data["this_file"] == "menu-adaptations.json"
    assert (
        data["source_index_sha256"]
        == hashlib.sha256((ROOT / "rescue-index.json").read_bytes()).hexdigest()
    )
    rows = [row for row in data["adaptations"] if row.get("family") != "part3-official"]
    assert len(rows) == 2 and len({r["menu"] for r in rows}) == 2
    original = {
        r["menu"]: r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    assert {r["entry_point"] for r in rows} == {"show_basic", "show_custom"}
    for row in rows:
        assert row["source_menu"] in original
        assert row["source"] == original[row["source_menu"]]["target"]
        assert row["source_sha256"] == original[row["source_menu"]]["target_sha256"]
        assert row["source"].startswith("rescued/part2/")
        assert not (ROOT / row["source_menu"]).exists()
        assert (
            row["native_acceptance"] == "pending"
            and row["original_workflow_accepted"] is False
        )
        assert row["license"] == "Apache-2.0 (owner D22)"
        assert (
            row["destination_sha256"]
            == hashlib.sha256((ROOT / row["menu"]).read_bytes()).hexdigest()
        )


@pytest.mark.parametrize("entry", ["show_basic", "show_custom"])
def test_practical_menu_when_imported_then_lazy_and_exact_public_fly_dispatch(
    monkeypatch, entry
):
    row = next(r for r in adaptations()["adaptations"] if r["entry_point"] == entry)
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.glyph_catalog"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.glyph_catalog"], entry, lambda: calls.append(entry))
    path = ROOT / row["menu"]
    ns = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    ns["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert "App>=0.2.54.dev0" in ast.get_docstring(tree)
    assert len(path.relative_to(ROOT / "Scripts").parts) == 2
