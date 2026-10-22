# this_file: tests/test_slider_adaptations.py
"""Distinct source identities, complete facades and additive original preservation."""

import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

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
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["destination_sha256"]
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.slider_spacing"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.slider_spacing"], entry, lambda: calls.append(entry))
    body = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    body["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]
    assert sha in (ROOT / "NOTICE").read_text()
    assert "this_file: " + row["menu"] in path.read_text()


def test_all_prior_runtime_and_provenance_rows_remain_exact():
    baseline = json.loads((ROOT / "tests/sliders-prior-baseline.json").read_text())
    for path, digest in baseline["prior_runtime"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    rows = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
    assert rows[:19] == baseline["prior_adaptations"]
    assert len(rows) == 208
