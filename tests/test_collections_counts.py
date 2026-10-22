"""The collections page states the real menu, adaptation and backlog counts."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_collections_page_counts_match_the_data() -> None:
    """Catch a stale hand-written count the moment a tool is added or retired."""
    record = json.loads((ROOT / "menu-adaptations.json").read_text())
    index = json.loads((ROOT / "rescue-index.json").read_text())
    identities = len(index["menus"]) if isinstance(index, dict) else len(index)
    menus = len(list((ROOT / "Scripts").glob("*/*.py")))
    # Records without source_menu cover rescued files that had no menu identity.
    rows = record["adaptations"] + record["retirements"]
    adapted = sum("source_menu" in row for row in record["adaptations"])
    retired = sum("source_menu" in row for row in record["retirements"])
    source_only = sum("source_menu" not in row for row in rows)
    backlog = identities - adapted - retired
    text = (ROOT / "src_docs/md/collections.md").read_text()
    assert f"The {menus} entries require" in text, "menu count is stale"
    assert f"remain in `rescue-index.json`; the {adapted}" in text, "adapted count"
    assert f"and {retired} retirements" in text, "retired count"
    assert f"The other {backlog}\nidentities" in text, "backlog count"
    assert f"A further {source_only} rescued files" in text, "source-only count"
