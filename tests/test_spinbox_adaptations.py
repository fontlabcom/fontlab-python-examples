# this_file: tests/test_spinbox_adaptations.py
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
        (2, "cbaed2d33a67865efa54c15f71701d7b62c6d2bda69a111e6351fac866f972db", "show"),
        (
            3,
            "e25b26cd135fd40ef1ed9316a402483d676ba7606da94007f00078993b5fa54b",
            "show_detailed",
        ),
    ],
)
def test_complete_family_identity_and_lazy_fly_menu(monkeypatch, part, sha, entry):
    record = json.loads((ROOT / "menu-adaptations.json").read_text())
    rows = [
        r for r in record["adaptations"] if r.get("family") == f"spinboxes-part{part}"
    ]
    assert len(rows) == 1
    row = rows[0]
    assert row["source_sha256"] == sha and row["assets"] == []
    assert (
        row["native_acceptance"] == "pending"
        and row["original_workflow_accepted"] is False
    )
    assert f"part{part}" in row["source"] and "spinboxes-" in row["source"]
    path = ROOT / row["menu"]
    assert len(Path(row["menu"]).parts) == 3
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["destination_sha256"]
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.glyph_numeric"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.glyph_numeric"], entry, lambda: calls.append(entry))
    body = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    body["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]
    assert sha in (ROOT / "NOTICE").read_text()
    assert "this_file: " + row["menu"] in path.read_text()


def test_all_prior_runtime_and_provenance_rows_remain_exact():
    baseline = json.loads((ROOT / "tests/spinbox-prior-baseline.json").read_text())
    for path, digest in baseline["prior_runtime"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    rows = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
    assert rows[:17] == baseline["prior_adaptations"]
    assert len(rows) == 23
