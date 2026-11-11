# this_file: tests/test_calendar_adaptation.py
"""The part2 calendar keeps a hash-bound source identity and distinct part3 route."""

import ast
import hashlib
import json
from pathlib import Path

from _wp09_routes import assert_compat_route, source_bytes

ROOT = Path(__file__).resolve().parents[1]


def test_calendar_adaptation_keeps_all_sources_and_distinct_part3_route():
    manifest = json.loads((ROOT / "menu-adaptations.json").read_text())
    rows = [r for r in manifest["adaptations"] if r.get("family") == "calendar-part2"]
    assert len(manifest["adaptations"]) == 231 and len(rows) == 1
    row = rows[0]
    assert row["api_module"] == "glyphs.calendar.model" and row["entry_point"] == "show"
    index = json.loads((ROOT / "rescue-index.json").read_text())
    source = next(r for r in index["menus"] if r["menu"] == row["source_menu"])
    assert (
        source["target"] == row["source"]
        and source["target_sha256"] == row["source_sha256"]
    )
    assert not (ROOT / row["source_menu"]).exists()
    assert (
        hashlib.sha256(source_bytes(ROOT / row["menu"])).hexdigest()
        == row["destination_sha256"]
    )
    assert (
        row["native_acceptance"] == "pending" and not row["original_workflow_accepted"]
    )
    assert "complete" in row["scope"].lower() and "January 1" in row["scope"]
    part3 = next(
        r
        for r in index["menus"]
        if "calendarwidget" in r["target"] and "/part3/" in r["target"]
    )
    official = next(
        r for r in manifest["adaptations"] if r.get("family") == "calendar-part3"
    )
    assert (
        official["source_menu"] == part3["menu"]
        and official["source_sha256"] == part3["target_sha256"]
    )
    assert (ROOT / official["menu"]).is_file() and official[
        "entry_point"
    ] == "show_official"
    assert row["entry_point"] == "show", "keep the distinct part2 policy"


def test_calendar_facade_is_lazy_typed_and_routes_through_fly(monkeypatch):
    path = ROOT / "Scripts/Widgets/Glyph Modification Calendar.py"
    assert_compat_route(monkeypatch, path, 'show', 'fly.ap.glyphs.calendar.model')
    assert "App>=0.2.60.dev0" in ast.get_docstring(
        ast.parse(path.read_text(), feature_version=(3, 11))
    )
