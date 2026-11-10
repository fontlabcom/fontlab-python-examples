# this_file: tests/test_scriptmix_pin_freshness.py
"""Scriptmix-hosted destinations must still hash to the pins recorded in menu-adaptations.json."""

import hashlib
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "fontlab-python-scriptmix/"
ADAPTATIONS = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]


def stale_pins(rows: list[dict], scriptmix_root: Path) -> list[str]:
    """Return one problem per Scriptmix-hosted row whose file is missing or hashes differently."""
    problems = []
    for row in rows:
        menu = row["menu"]
        if not menu.startswith(PREFIX):
            continue
        path = scriptmix_root / menu.removeprefix(PREFIX)
        if not path.is_file():
            problems.append(f"missing: {menu}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != row["destination_sha256"]:
            problems.append(f"stale pin: {menu}")
    return problems


def test_stale_pins_when_file_changed_or_missing_then_reported(tmp_path):
    body = b"print('x')\n"
    (tmp_path / "Scripts").mkdir()
    (tmp_path / "Scripts/A.py").write_bytes(body)
    (tmp_path / "Scripts/B.py").write_bytes(b"changed\n")
    rows = [
        {"menu": f"{PREFIX}Scripts/A.py", "destination_sha256": hashlib.sha256(body).hexdigest()},
        {"menu": f"{PREFIX}Scripts/B.py", "destination_sha256": hashlib.sha256(body).hexdigest()},
        {"menu": f"{PREFIX}Scripts/C.py", "destination_sha256": "0" * 64},
        {"menu": "Scripts/Local.py", "destination_sha256": "1" * 64},
    ]
    assert stale_pins(rows, tmp_path) == [
        f"stale pin: {PREFIX}Scripts/B.py",
        f"missing: {PREFIX}Scripts/C.py",
    ]


def test_scriptmix_pins_when_sibling_checkout_present_then_all_current():
    root = Path(
        os.environ.get("FONTLAB_SCRIPTMIX_ROOT", str(ROOT.parent / "fontlab-python-scriptmix"))
    )
    if not root.is_dir():
        pytest.skip("no Scriptmix checkout; set FONTLAB_SCRIPTMIX_ROOT")
    rows = [r for r in ADAPTATIONS if r["menu"].startswith(PREFIX)]
    assert len(rows) == 24, "the recorded Scriptmix-hosted row count changed"
    assert stale_pins(rows, root) == []
