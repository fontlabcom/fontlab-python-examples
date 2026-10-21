# this_file: tests/test_spacing_menu_integration.py
"""Preserve the curated28 and all Lessons/licences when adding only this pair."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "tests/spacing-curated-baseline.json").read_text())
NEW = {
    "Scripts/Tools/Glyph Spacing Worksheet.py",
    "Scripts/Tools/Glyph Spacing Worksheet - Frameless.py",
}
EXAMPLE_BATCHES = {
    "Scripts/Dialogs/Expandable Glyph Search.py",
    "Scripts/Dialogs/Font Glyph Inventory Tabs.py",
    "Scripts/Dialogs/FontLab Script Scaffold Wizard.py",
    "Scripts/Dialogs/Glyph Batch Recipe Settings.py",
    "Scripts/Dialogs/Glyph Proof Batch Wizard.py",
    "Scripts/Dialogs/Proof Text Coverage Dialog.py",
    "Scripts/Drag And Drop/Deferred Glyph Report Drag.py",
    "Scripts/Drag And Drop/Draggable Glyph Names.py",
    "Scripts/Drag And Drop/Font Drop Inspector.py",
    "Scripts/Drag And Drop/Font File Drop Shelf.py",
    "Scripts/Drag And Drop/Glyph Pair Board.py",
    "Scripts/Drag And Drop/Proof Word Magnets.py",
    "Scripts/Models/Glyph Coverage Grid.py",
    "Scripts/Models/Glyph Encoding Chart.py",
    "Scripts/Models/Glyph Inventory XML.py",
    "Scripts/Models/Glyph Mark Colours.py",
    "Scripts/Models/Glyph Proof Worksheet.py",
    "Scripts/Models/Glyph Review Form.py",
    "Scripts/Models/Glyph Review Priorities.py",
    "Scripts/Text/Calendar Proof Builder.py",
    "Scripts/Text/Feature Code Draft.py",
    "Scripts/Text/Font Handoff Letter.py",
    "Scripts/Text/Font Review Notes.py",
    "Scripts/Text/Script Snippet Notebook.py",
}


def test_spacing_pair_when_added_then_only_two_new_one_level_scripts():
    paths = {p.relative_to(ROOT).as_posix() for p in (ROOT / "Scripts").rglob("*.py")}
    assert paths == set(BASE["menus"]) | NEW | {"Scripts/Tools/Glyph Name Pattern Lab.py", "Scripts/Tools/Component Dependency Graph.py", "Scripts/Tools/Component Dependency Graph - Degree Forces.py", "Scripts/Widgets/Glyph Metrics and Revisions.py", "Scripts/Widgets/Glyph Metrics and Revisions - Detailed.py", "Scripts/Widgets/Glyph Spacing Offset.py", "Scripts/Widgets/Glyph Spacing Offset - Stacked.py", "Scripts/Widgets/Glyph Character Map.py", "Scripts/Widgets/Glyph Character Map - Styles.py", "Scripts/Tools/Find Font Source Files.py", "Scripts/Tools/Find Font Source Files - Bytes.py", "Scripts/Tools/Font Reference Image Viewer.py", "Scripts/Tools/Font Reference Image Viewer - Bounded Zoom.py"} | EXAMPLE_BATCHES, (
        "Keep every curated menu and add exactly the two reviewed tools"
    )
    assert len(paths) == 67 and not any(
        path.startswith("Scripts/Archived") for path in paths
    )
    for path, digest in BASE["menus"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path


def test_spacing_pair_when_integrated_then_all_lessons_and_license_bytes_preserved():
    for path, digest in {**BASE["lessons"], **BASE["licences"]}.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    prior = BASE["notice_prefix"]
    assert (
        hashlib.sha256((ROOT / "NOTICE").read_bytes()[: prior["bytes"]]).hexdigest()
        == prior["sha256"]
    )


def test_spacing_pair_when_mapped_then_original_provenance_and_native_pending_remain():
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    assert data["adaptations"][:12] == BASE["prior_adaptations"]
    assert len(data["adaptations"]) == 99
    assert (
        hashlib.sha256((ROOT / "rescue-index.json").read_bytes()).hexdigest()
        == BASE["rescue_index_sha256"]
    )
    assert all(
        row["native_acceptance"] == "pending"
        and row["original_workflow_accepted"] is False
        for row in data["adaptations"]
    )
    rows = [row for row in data["adaptations"] if row.get("family", "").startswith("spacing-worksheet-")]
    assert {row["menu"] for row in rows} == NEW
    for row in rows:
        assert (
            hashlib.sha256((ROOT / row["menu"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        )
        assert not (ROOT / row["source_menu"]).exists()
