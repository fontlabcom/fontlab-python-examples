# this_file: tests/test_adaptation_records.py
"""Pin the record schema of menu-adaptations.json.

What: Check the keys of every adaptation and retirement record, the native
duplicate convention and the counts stated in README.md.
Why: Batches add records in parallel. One schema keeps the file readable by
the docs, the tests and the coverage checker.
Rules:
- An adaptation names an active destination script and its SHA256.
- A retirement has no script in this collection and states its reason.
- A FontLab command can do the job of a source. Such a retirement keeps
  disposition "retired"; its reason starts with "duplicate-of native " and
  names the menu command. It has no destination script.
- The App floor is stated in each script's Setup line, not in the records.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = json.loads((ROOT / "menu-adaptations.json").read_text())
NATIVE = "duplicate-of native "
ADAPTATION_REQUIRED = {
    "source_menu",
    "source",
    "source_sha256",
    "license",
    "menu",
    "destination_sha256",
    "entry_point",
    "scope",
    "native_acceptance",
    "original_workflow_accepted",
}
ADAPTATION_OPTIONAL = {
    "family",
    "disposition",
    "assets",
    "source_body_redistributed",
    "api_module",
    "helper_executed",
}
RETIREMENT_REQUIRED = {
    "source_menu",
    "source",
    "source_sha256",
    "license",
    "disposition",
    "reason",
}
RETIREMENT_OPTIONAL = {
    "family",
    "scope",
    "assets",
    "source_body_redistributed",
    "menu",
    "destination_sha256",
    "entry_point",
    "native_acceptance",
    "original_workflow_accepted",
}


def test_records_when_loaded_then_keys_follow_the_schema() -> None:
    for row in RECORDS["adaptations"]:
        keys = set(row)
        assert ADAPTATION_REQUIRED <= keys, row["source"]
        assert keys <= ADAPTATION_REQUIRED | ADAPTATION_OPTIONAL, row["source"]
        assert row.get("disposition", "ported") in {"ported", "duplicate-of"}
    for row in RECORDS["retirements"]:
        keys = set(row)
        assert RETIREMENT_REQUIRED <= keys, row["source"]
        assert keys <= RETIREMENT_REQUIRED | RETIREMENT_OPTIONAL, row["source"]
        assert row["disposition"] == "retired", row["source"]
        assert row["reason"].strip(), row["source"]
        assert row.get("menu") is None, "A retirement has no destination script"


def test_records_when_loaded_then_each_source_has_one_record() -> None:
    rows = RECORDS["adaptations"] + RECORDS["retirements"]
    menus = [row["source_menu"] for row in rows]
    assert len(menus) == len(set(menus)), "One record per historical identity"


def test_native_duplicates_when_retired_then_reason_names_the_command() -> None:
    native = [r for r in RECORDS["retirements"] if r["reason"].startswith(NATIVE)]
    for row in native:
        command = row["reason"].removeprefix(NATIVE)
        assert " > " in command.split(".")[0], row["source"]
    for row in RECORDS["adaptations"]:
        assert not str(row["scope"]).startswith(NATIVE), "A native duplicate is a retirement"
    readme = (ROOT / "README.md").read_text()
    assert f"For {len(native)} of them" in readme, "README native-duplicate count"
    assert "retired without a replacement" not in readme


def test_app_floor_when_recorded_then_only_in_script_setup_lines() -> None:
    for row in RECORDS["adaptations"] + RECORDS["retirements"]:
        assert "app_minimum" not in row, row["source"]
