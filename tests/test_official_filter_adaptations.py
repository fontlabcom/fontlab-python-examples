# this_file: tests/test_official_filter_adaptations.py
"""Part3 identities stay distinct from the previously adapted part2 workflows."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_when_official_pair_adapted_then_frozen_source_and_distinct_semantics():
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    assert len(data["adaptations"]) == 51
    rows = [r for r in data["adaptations"] if r.get("family") == "part3-official"]
    assert len(rows) == 2
    assert {r["entry_point"] for r in rows} == {
        "show_official_basic",
        "show_official_custom",
    }
    index = {
        r["menu"]: r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    for row in rows:
        assert row["source"].startswith("rescued/part3/")
        assert index[row["source_menu"]]["target_sha256"] == row["source_sha256"]
        assert not (ROOT / row["source_menu"]).exists()
        assert (
            row["destination_sha256"]
            == hashlib.sha256((ROOT / row["menu"]).read_bytes()).hexdigest()
        )
        assert (
            row["native_acceptance"] == "pending"
            and not row["original_workflow_accepted"]
        )
        assert "QDateTime" in row["scope"]


@pytest.mark.parametrize("entry", ["show_official_basic", "show_official_custom"])
def test_menu_when_loaded_and_run_then_exact_lazy_fly_route(monkeypatch, entry):
    rows = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
    row = next(r for r in rows if r["entry_point"] == entry)
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.glyph_catalog"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.glyph_catalog"], entry, lambda: calls.append(entry))
    path = ROOT / row["menu"]
    values = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    values["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]
    tree = ast.parse(path.read_text(), feature_version=(3, 11))
    assert "App>=0.2.55.dev0" in ast.get_docstring(tree)
