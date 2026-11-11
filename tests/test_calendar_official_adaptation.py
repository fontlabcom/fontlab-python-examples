# this_file: tests/test_calendar_official_adaptation.py
"""Part3 has its own complete hash-bound route; part2 remains a distinct caller."""

import ast
import hashlib
import json
from pathlib import Path

from _wp09_routes import assert_compat_route, source_bytes

ROOT = Path(__file__).resolve().parents[1]


def test_official_calendar_keeps_frozen_source_and_all_distinct_options():
    manifest = json.loads((ROOT / "menu-adaptations.json").read_text())
    row = next(
        r for r in manifest["adaptations"] if r.get("family") == "calendar-part3"
    )
    assert len(manifest["adaptations"]) == 231
    original = next(
        r
        for r in json.loads((ROOT / "rescue-index.json").read_text())["menus"]
        if r["menu"] == row["source_menu"]
    )
    assert (
        original["target"] == row["source"]
        and original["target_sha256"] == row["source_sha256"]
    )
    assert not (ROOT / row["source_menu"]).exists()
    assert (
        hashlib.sha256(source_bytes(ROOT / row["menu"])).hexdigest()
        == row["destination_sha256"]
    )
    assert (
        not row["original_workflow_accepted"] and row["native_acceptance"] == "pending"
    )
    assert (
        row["api_module"] == "glyphs.calendar.model" and row["entry_point"] == "show_official"
    )
    assert all(
        word in row["scope"]
        for word in ["seven", "May1", "Italic", "ordered Qt locale"]
    )
    assert (
        next(r for r in manifest["adaptations"] if r.get("family") == "calendar-part2")[
            "entry_point"
        ]
        == "show"
    )


def test_official_calendar_import_is_lazy_and_exactly_routes_through_fly(monkeypatch):
    path = ROOT / "Scripts/Widgets/Glyph Modification Calendar with Formats.py"
    assert_compat_route(monkeypatch, path, 'show_official', 'fly.ap.glyphs.calendar.model')
    assert "App>=0.2.61.dev0" in ast.get_docstring(
        ast.parse(path.read_text(), feature_version=(3, 11))
    )
