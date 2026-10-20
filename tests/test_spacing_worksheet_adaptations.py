# this_file: tests/test_spacing_worksheet_adaptations.py
"""Both lazy worksheet menus preserve exact source identity and native status."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("part,entry", [("part2", "show"), ("part3", "show_official")])
def test_complete_spacing_pair_identity_lazy_fly_and_notices(part, entry, monkeypatch):
    rows = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
    row = next(r for r in rows if r.get("family") == "spacing-worksheet-" + part)
    original = next(
        r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
        if r["menu"] == row["source_menu"]
    )
    assert (
        row["source"] == original["target"]
        and row["source_sha256"] == original["target_sha256"]
    )
    assert row["entry_point"] == entry and row["api_module"] == "spacing_worksheet"
    assert (
        row["native_acceptance"] == "pending"
        and row["original_workflow_accepted"] is False
    )
    assert not (ROOT / row["source_menu"]).exists()
    path = ROOT / row["menu"]
    body = path.read_bytes()
    assert hashlib.sha256(body).hexdigest() == row["destination_sha256"]
    tree = ast.parse(body, feature_version=(3, 11))
    doc = ast.get_docstring(tree)
    for word in (
        "App>=0.2.70.dev0",
        "Purpose:",
        "Setup:",
        "Run:",
        "Result:",
        "Compatibility:",
        "pending",
        "preserved",
    ):
        assert word in doc
    assert (
        len(body.splitlines()) < 55
        and len(path.relative_to(ROOT / "Scripts").parts) == 2
    )
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.spacing_worksheet"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.spacing_worksheet"], entry, lambda: calls.append(entry))
    values = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    values["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]
    notice = (ROOT / "NOTICE").read_text()
    assert (
        row["source_sha256"] in notice
        and "2017 Riverbank" in notice
        and "2010 Nokia" in notice
    )
    assert "$QT_BEGIN_LICENSE:BSD$" in notice and "$QT_END_LICENSE$" in notice
    assert row["assets"] == [] and row["helper_executed"] is False
