# this_file: tests/test_elastic_adaptations.py
"""Both complete variants keep pinned original identities and lazy Fly routes."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "part,digest,entry",
    [
        (2, "d65729560a7b649d21bcffcd176aaba7541920cc427548c6e17c1269c70d6bef", "show"),
        (
            3,
            "fa1dc74f37f29a33afd673b5e4a399838797d8cc355079d512769ec6d10e6a99",
            "show_official",
        ),
    ],
)
def test_distinct_elastic_provenance_and_exact_public_fly_launch(
    monkeypatch, part, digest, entry
):
    row = next(
        r
        for r in json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
        if r.get("family") == f"elastic-nodes-part{part}"
    )
    assert (
        row["source_sha256"] == digest
        and row["assets"] == []
        and row["helper_executed"] is False
    )
    assert (
        row["native_acceptance"] == "pending"
        and row["original_workflow_accepted"] is False
    )
    assert f"part{part}/" in row["source"] and not (ROOT / row["source_menu"]).exists()
    path = ROOT / row["menu"]
    text = path.read_text()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == row["destination_sha256"]
    assert digest in text and digest in (ROOT / "NOTICE").read_text()
    ast.parse(text, feature_version=(3, 11))
    calls = []
    for name in ("fly", "fly.ap", "fly.ap.component_graph"):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    setattr(sys.modules["fly.ap.component_graph"], entry, lambda: calls.append(entry))
    namespace = runpy.run_path(str(path), run_name="inspection")
    assert calls == []
    namespace["main"]()
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry]


def test_all_31_prior_menu_bytes_and_15_provenance_rows_unchanged():
    baseline = json.loads((ROOT / "tests/elastic-baseline.json").read_text())
    for path, digest in baseline["menus"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    data = json.loads((ROOT / "menu-adaptations.json").read_text())
    assert data["adaptations"][:15] == baseline["adaptations"]
    assert (
        hashlib.sha256((ROOT / "rescue-index.json").read_bytes()).hexdigest()
        == baseline["source_index_sha256"]
    )
    assert len(list((ROOT / "Scripts").rglob("*.py"))) == 90
