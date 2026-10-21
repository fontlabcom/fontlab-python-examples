# this_file: tests/test_find_files_adaptations.py
"""Both original identities remain pinned; public menu dispatch never scans on import."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_both_complete_original_profiles_and_prior_catalogue_remain():
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    rows = [
        r for r in data["adaptations"] if r.get("family", "").startswith("find-files-")
    ]
    assert len(rows) == 2 and {r["entry_point"] for r in rows} == {"show", "show_bytes"}
    index = {
        r["menu"]: r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    }
    assert len(index) == 494
    for row in rows:
        assert row["source"] == index[row["source_menu"]]["target"]
        assert row["source_sha256"] == index[row["source_menu"]]["target_sha256"]
        assert (
            hashlib.sha256((ROOT / row["menu"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        )
        assert (
            row["native_acceptance"] == "pending"
            and row["original_workflow_accepted"] is False
        )
        assert not (ROOT / row["source_menu"]).exists()


@pytest.mark.parametrize(
    "name,entry",
    [
        ("Find Font Source Files", "show"),
        ("Find Font Source Files - Bytes", "show_bytes"),
    ],
)
def test_exact_lazy_public_Fly_menu_dispatch(monkeypatch, name, entry):
    calls = []
    module = ModuleType("fly.ap.find_files")
    setattr(module, entry, lambda: calls.append(entry))
    monkeypatch.setitem(sys.modules, "fly.ap.find_files", module)
    menu = ROOT / f"Scripts/Tools/{name}.py"
    scope = runpy.run_path(str(menu), run_name="inspection")
    assert calls == []
    scope["main"]()
    assert calls == [entry]
    runpy.run_path(str(menu), run_name="__main__")
    assert calls == [entry, entry]
