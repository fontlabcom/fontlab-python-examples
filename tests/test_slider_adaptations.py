# this_file: tests/test_slider_adaptations.py
"""Distinct source identities, complete facades and additive original preservation."""

import hashlib
import json
from pathlib import Path

import pytest
from _wp09_routes import assert_compat_route, source_bytes
from test_spacing_menu_integration import lesson_contract_successors

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "part,sha,entry",
    [
        (2, "aa662a1158ce7f691d467ef90974895e39ef05ce33098ac7072b7cca5efbad56", "show"),
        (
            3,
            "24312666a881173fd0a203fd1217ea8d13be8edc0e70b08628e3c4addc49cc5d",
            "show_stacked",
        ),
    ],
)
def test_complete_family_identity_and_lazy_fly_menu(monkeypatch, part, sha, entry):
    record = json.loads((ROOT / "menu-adaptations.json").read_text())
    rows = [
        r for r in record["adaptations"] if r.get("family") == f"sliders-part{part}"
    ]
    assert len(rows) == 1
    row = rows[0]
    assert row["source_sha256"] == sha and row["assets"] == []
    assert (
        row["native_acceptance"] == "pending"
        and row["original_workflow_accepted"] is False
    )
    assert f"part{part}" in row["source"] and "sliders-" in row["source"]
    path = ROOT / row["menu"]
    assert len(Path(row["menu"]).parts) == 3
    assert hashlib.sha256(source_bytes(path)).hexdigest() == row["destination_sha256"]
    assert_compat_route(monkeypatch, path, entry, 'fly.ap.metrics.offset.model')
    assert sha in (ROOT / "NOTICE").read_text()
    assert "this_file: " + row["menu"] in path.read_text()


def test_all_prior_runtime_and_provenance_rows_remain_exact():
    baseline = json.loads((ROOT / "tests/sliders-prior-baseline.json").read_text())
    successors = lesson_contract_successors(
        json.loads((ROOT / "tests/lesson-contract-successors.json").read_text())
    )
    for path, digest in baseline["prior_runtime"].items():
        expected = successors.get(path, digest)
        assert hashlib.sha256(source_bytes(ROOT / path)).hexdigest() == expected, path
    rows = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
    assert rows[:19] == baseline["prior_adaptations"]
    assert len(rows) == 231
