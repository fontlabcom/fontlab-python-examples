# this_file: tests/test_tree_adaptations.py
"""Both frozen simple-tree identities route to complete distinct font workflows."""

import ast
import hashlib
import json
from pathlib import Path

import pytest
from _wp09_routes import assert_compat_route, source_bytes

ROOT = Path(__file__).resolve().parents[1]


def test_tree_pair_keeps_frozen_identities_and_complete_readonly_contracts():
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    assert len(data["adaptations"]) == 231
    rows = [r for r in data["adaptations"] if r.get("family") == "simple-tree"]
    assert len(rows) == 2 and {r["entry_point"] for r in rows} == {
        "show_outline",
        "show_tree",
    }
    original = {
        r["menu"]: r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    for row in rows:
        assert row["api_module"] == "glyphs.tree.model"
        assert row["source"] == original[row["source_menu"]]["target"]
        assert row["source_sha256"] == original[row["source_menu"]]["target_sha256"]
        assert (
            hashlib.sha256(source_bytes(ROOT / row["menu"])).hexdigest()
            == row["destination_sha256"]
        )
        assert not (ROOT / row["source_menu"]).exists()
        assert (
            row["native_acceptance"] == "pending"
            and row["original_workflow_accepted"] is False
        )
        assert "complete" in row["scope"].lower() and "read-only" in row["scope"]


@pytest.mark.parametrize("entry", ["show_outline", "show_tree"])
def test_tree_menus_remain_lazy_typed_python311_fly_facades(monkeypatch, entry):
    rows = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
    row = next(r for r in rows if r["entry_point"] == entry)
    path = ROOT / row["menu"]
    assert_compat_route(monkeypatch, path, entry, 'fly.ap.glyphs.tree.model')
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert "App>=0.2.57.dev0" in ast.get_docstring(tree)
