# this_file: tests/test_rescued_menus.py
"""Keep original identities and bytes without presenting archive dispatch as a tool."""

import hashlib
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
INDEX = json.loads((ROOT / "rescue-index.json").read_text())
ADAPTATIONS = json.loads((ROOT / "menu-adaptations.json").read_text())
ROWS = INDEX["menus"]


def test_index_when_loaded_then_complete_unique_source_scope_remains_pending():
    assert len(ROWS) == INDEX["new_menu_count"] == 494, (
        "Keep all original source identities"
    )
    assert len({row["menu"] for row in ROWS}) == 494
    assert (
        hashlib.sha256((ROOT / "rescue-index.json").read_bytes()).hexdigest()
        == ADAPTATIONS["source_index_sha256"]
    )
    adapted = {row["source_menu"] for row in ADAPTATIONS["adaptations"]}
    assert len(adapted) == 73 and len(ROWS) - len(adapted) == 421
    assert adapted <= {row["menu"] for row in ROWS}
    for row in ADAPTATIONS["adaptations"]:
        assert (ROOT / row["menu"]).is_file(), (
            "Keep each reviewed practical destination active"
        )
        assert (
            row["native_acceptance"] == "pending"
            and row["original_workflow_accepted"] is False
        )


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["menu"])
def test_source_when_retired_from_menu_then_original_bytes_preserved_and_no_dispatcher(
    row,
):
    assert not (ROOT / row["menu"]).exists(), (
        "Archived dispatchers must stay outside active Scripts"
    )
    source = ARCHIVE / row["target"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == row["target_sha256"], (
        "Never change preserved source bytes"
    )
