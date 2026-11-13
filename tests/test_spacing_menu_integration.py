# this_file: tests/test_spacing_menu_integration.py
"""Preserve the curated28 and all Lessons/licences when adding only this pair."""

import hashlib
import json
from pathlib import Path

import pytest
from _wp09_routes import source_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = json.loads((ROOT / "tests/spacing-curated-baseline.json").read_text())
NEW = {
    "Scripts/Tools/Glyph Spacing Worksheet.py",
    "Scripts/Tools/Glyph Spacing Worksheet - Frameless.py",
}
EXAMPLE_BATCHES = {
    "Scripts/Contours/Node Slope And Handles.py",
    "Scripts/Contours/Node Table.py",
    "Scripts/Designer/Em Star Polygon.py",
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
    "Scripts/Drawing/Glyph Outline SVG.py",
    "Scripts/Drawing/Glyph SVG Reference.py",
    "Scripts/Drawing/Scale With Stem Compensation.py",
    "Scripts/Drawing/Stem Blend.py",
    "Scripts/Graphics/Glyph Mark Colour Board.py",
    "Scripts/Graphics/Glyph Proof Layout.py",
    "Scripts/Graphics/Glyph Proof Pad.py",
    "Scripts/Graphics/Glyph Review Cards.py",
    "Scripts/Graphics/Glyph Variant Feature Graph.py",
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
    "Scripts/Tools/Apply Unicode Map.py",
    "Scripts/Tools/Copy Layers From Font.py",
    "Scripts/Tools/Font Info Snapshot.py",
    "Scripts/Tools/Font Name Encoding Audit.py",
    "Scripts/Tools/FontLab Qt Slot Reference.py",
    "Scripts/Tools/Glyph Snapshot Console.py",
    "Scripts/Tools/Import Kerning Pair List.py",
    "Scripts/Tools/Kerning Copy Rules.py",
    "Scripts/Tools/Layer Metric Comparison.py",
    "Scripts/Tools/Localized Font Names.py",
    "Scripts/Tools/Pair Proof Generator.py",
    "Scripts/Tools/Path Problem Report.py",
    "Scripts/Tools/Saved Proof Sample.py",
    "Scripts/Tools/Symbol Tag Search.py",
    "Scripts/Widgets/Font Units Calculator.py",
    "Scripts/Widgets/Glyph Proof Groups.py",
    "Scripts/Widgets/Glyph Sketch Pad.py",
    "Scripts/Widgets/Script Icon Browser.py",
    "Scripts/Widgets/Script Palette Roles.py",
    "Scripts/Windows/Glyph Snapshot Diff.py",
    "Scripts/Windows/Unicode Issues Dock.py",
}
LESSON_SUCCESSOR_PATHS = {
    "lessons/DEPENDENCIES.md",
    "lessons/README.md",
    "lessons/pyproject.toml",
    "lessons/candidate_tests/models_candidate/test_getgo.py",
    "lessons/provenance/getgo.json",
    "lessons/src/fontlab_python_lessons/getgo/outline_pens.py",
    "lessons/candidate_tests/models_candidate/test_getgo_package.py",
    "lessons/WORK.md",
    "lessons/CHANGELOG.md",
}


def lesson_contract_successors(record):
    assert record["source_commit"] == "61e114bc9d5512ca445967d420d7e3d48c6ac302"
    frozen = {
        "tests/sliders-prior-baseline.json": "67e2f3a2d3fc7761df5fe3c21d876e7378ba59a5196ff5f7630fa7bcd9c056f8",
        "tests/spacing-curated-baseline.json": "e6c46bbd62757e71ba60868346df28af57631aa8c3fbf92e9e0b774c6bbcc6f3",
        "tests/spacing-guide-successors.json": "d22c767eb9307e65f332770835110d5ec06635e7c4ba543b27b6e76dec196f8e",
    }
    assert record["frozen_references"] == frozen
    for path, digest in frozen.items():
        assert hashlib.sha256(source_bytes(ROOT / path)).hexdigest() == digest, path
    guides = json.loads((ROOT / "tests/spacing-guide-successors.json").read_text())["guides"]
    assert set(record["successors"]) == LESSON_SUCCESSOR_PATHS
    for path, row in record["successors"].items():
        assert set(row) == {"original_sha256", "previous_sha256", "successor_sha256"}
        assert row["original_sha256"] == BASE["lessons"][path], path
        previous = guides[path]["approved_sha256"] if path in guides else BASE["lessons"][path]
        assert row["previous_sha256"] == previous, path
        assert hashlib.sha256(source_bytes(ROOT / path)).hexdigest() == row["successor_sha256"], path
    return {path: row["successor_sha256"] for path, row in record["successors"].items()}


def test_spacing_pair_when_added_then_only_two_new_one_level_scripts():
    paths = {p.relative_to(ROOT).as_posix() for p in (ROOT / "Scripts").rglob("*.py")}
    assert paths == set(BASE["menus"]) | NEW | {"Scripts/Tools/Glyph Name Pattern Lab.py", "Scripts/Tools/Component Dependency Graph.py", "Scripts/Tools/Component Dependency Graph - Degree Forces.py", "Scripts/Widgets/Glyph Metrics and Revisions.py", "Scripts/Widgets/Glyph Metrics and Revisions - Detailed.py", "Scripts/Widgets/Glyph Spacing Offset.py", "Scripts/Widgets/Glyph Spacing Offset - Stacked.py", "Scripts/Widgets/Glyph Character Map.py", "Scripts/Widgets/Glyph Character Map - Styles.py", "Scripts/Tools/Find Font Source Files.py", "Scripts/Tools/Find Font Source Files - Bytes.py", "Scripts/Tools/Font Reference Image Viewer.py", "Scripts/Tools/Font Reference Image Viewer - Bounded Zoom.py"} | EXAMPLE_BATCHES | {row["destination"]["path"] for row in json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"] if row["acceptance"]["state"] == "implemented"}, (
        "Keep every curated menu and add exactly the two reviewed tools"
    )
    assert len(paths) == 109 and not any(
        path.startswith("Scripts/Archived") for path in paths
    )
    for path, digest in BASE["menus"].items():
        assert hashlib.sha256(source_bytes(ROOT / path)).hexdigest() == digest, path


def test_spacing_pair_when_integrated_then_all_lessons_and_license_bytes_preserved():
    lesson_successors = lesson_contract_successors(
        json.loads((ROOT / "tests/lesson-contract-successors.json").read_text())
    )
    successors = json.loads((ROOT / "tests/spacing-guide-successors.json").read_text())["guides"]
    assert set(successors) == {
        "lessons/CHANGELOG.md", "lessons/PLAN.md", "lessons/TODO.md", "lessons/WORK.md",
    }
    for path, row in successors.items():
        assert row["original_sha256"] == BASE["lessons"][path], path
    for path, digest in {**BASE["lessons"], **BASE["licences"]}.items():
        expected = successors[path]["approved_sha256"] if path in successors else digest
        if path in lesson_successors:
            expected = lesson_successors[path]
        assert hashlib.sha256(source_bytes(ROOT / path)).hexdigest() == expected, path
    notice = source_bytes(ROOT / "NOTICE")
    assert (
        hashlib.sha256(notice).hexdigest()
        == "7e9571a2d816af6eb7cee3f0527ad2d58f4751af5db10131de1b7569aac7230d"
    )
    assert b"The author supplies these first-party samples under Apache-2.0." in notice


@pytest.mark.parametrize(
    "damage", ["unauthorized-path", "original_sha256", "previous_sha256", "successor_sha256"]
)
def test_lesson_successor_record_rejects_unapproved_changes(damage):
    record = json.loads((ROOT / "tests/lesson-contract-successors.json").read_text())
    if damage == "unauthorized-path":
        record["successors"]["lessons/unapproved.py"] = {}
    else:
        record["successors"]["lessons/WORK.md"][damage] = "0" * 64
    with pytest.raises(AssertionError):
        lesson_contract_successors(record)


def test_lesson_successor_record_requires_every_current_file(monkeypatch):
    record = json.loads((ROOT / "tests/lesson-contract-successors.json").read_text())
    missing = ROOT / "lessons/WORK.md"
    read_bytes = Path.read_bytes

    def read(path):
        if path == missing:
            raise FileNotFoundError(path)
        return read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", read)
    with pytest.raises(FileNotFoundError):
        lesson_contract_successors(record)


def test_lesson_successors_keep_non_successor_runtime_bytes_protected(monkeypatch):
    protected = ROOT / "lessons/src/fontlab_python_lessons/getgo/__init__.py"
    assert protected.relative_to(ROOT).as_posix() not in LESSON_SUCCESSOR_PATHS
    read_bytes = Path.read_bytes
    monkeypatch.setattr(Path, "read_bytes", lambda path: b"damaged" if path == protected else read_bytes(path))
    with pytest.raises(AssertionError, match="getgo/__init__.py"):
        test_spacing_pair_when_integrated_then_all_lessons_and_license_bytes_preserved()


def test_spacing_pair_when_mapped_then_original_provenance_and_native_pending_remain():
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    assert data["adaptations"][:12] == BASE["prior_adaptations"]
    assert len(data["adaptations"]) == 231
    assert (
        hashlib.sha256(source_bytes(ROOT / "rescue-index.json")).hexdigest()
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
            hashlib.sha256(source_bytes(ROOT / row["menu"])).hexdigest()
            == row["destination_sha256"]
        )
        assert not (ROOT / row["source_menu"]).exists()
