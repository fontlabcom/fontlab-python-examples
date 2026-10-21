# this_file: tests/test_editable_tree_adaptations.py
"""Both complete editable-tree facades keep frozen source identity and Fly routing."""
import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("part,entry", [("part2", "show_outline"), ("part3", "show_tree")])
def test_editable_tree_pair_is_source_bound_and_native_pending(part, entry, monkeypatch):
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    assert len(data["adaptations"]) == 27
    row = next(r for r in data["adaptations"] if r.get("family") == "editable-tree-" + part)
    source = next(r for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"] if r["menu"] == row["source_menu"])
    assert row["source"] == source["target"] and row["source_sha256"] == source["target_sha256"]
    assert row["entry_point"] == entry and row["api_module"] == "editable_glyph_tree"
    assert row["native_acceptance"] == "pending" and not row["original_workflow_accepted"]
    assert not (ROOT / row["source_menu"]).exists()
    path = ROOT / row["menu"]
    body = path.read_bytes()
    assert hashlib.sha256(body).hexdigest() == row["destination_sha256"]
    tree = ast.parse(body, feature_version=(3, 11))
    assert "App>=0.2.66.dev0" in ast.get_docstring(tree)
    assert "this_file: " + row["menu"] in body.decode().splitlines()[0]
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.editable_glyph_tree"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.editable_glyph_tree"], entry, lambda: calls.append(entry))
    values = runpy.run_path(str(path), run_name="inspection")
    assert calls == [], "Import must be lazy"
    values["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]
