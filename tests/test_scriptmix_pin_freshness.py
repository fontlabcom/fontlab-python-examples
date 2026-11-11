# this_file: tests/test_scriptmix_pin_freshness.py
"""Scriptmix-hosted destinations must still hash to the pins recorded in menu-adaptations.json."""

import hashlib
import json
import os
from pathlib import Path

import pytest
from scriptmix_destinations import check_destination

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "fontlab-python-scriptmix/"
ADAPTATIONS = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]


def stale_pins(rows: list[dict], scriptmix_root: Path, skipped: list[str] | None = None) -> list[str]:
    """Return one problem per Scriptmix-hosted row whose file is missing or hashes differently.

    A row whose only unchecked part is a skip (App tab check in public CI) is appended to
    ``skipped`` so every other row is still checked; without ``skipped`` the skip propagates.
    """
    problems = []
    for row in rows:
        menu = row["menu"]
        if not menu.startswith(PREFIX):
            continue
        try:
            check_destination(menu, row["destination_sha256"], scriptmix=scriptmix_root)
        except AssertionError as error:
            problems.append(str(error))
        except pytest.skip.Exception as skip:
            if skipped is None:
                raise
            skipped.append(str(skip.msg))
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


def test_stale_pins_when_a_row_skips_then_later_rows_are_still_checked(tmp_path, monkeypatch):
    def fake(menu, pin, *, scriptmix):
        if menu.endswith("A.py"):
            pytest.skip("App tab check skipped: test")
        raise AssertionError(f"stale pin: {menu}")

    monkeypatch.setitem(globals(), "check_destination", fake)
    rows = [{"menu": f"{PREFIX}Scripts/A.py", "destination_sha256": "0" * 64},
            {"menu": f"{PREFIX}Scripts/B.py", "destination_sha256": "0" * 64}]
    skipped: list[str] = []
    try:
        problems = stale_pins(rows, tmp_path, skipped)
    except pytest.skip.Exception:
        pytest.fail("a skipped row must be collected, not stop the remaining rows")
    assert problems == [f"stale pin: {PREFIX}Scripts/B.py"]
    assert skipped == ["App tab check skipped: test"]
    with pytest.raises(pytest.skip.Exception):
        stale_pins(rows, tmp_path)


def resolve_scriptmix_root() -> Path | None:
    """Return the Scriptmix checkout; None only when the variable is unset and no sibling exists.

    An explicit FONTLAB_SCRIPTMIX_ROOT that is not a directory is an error, never a skip.
    """
    explicit = os.environ.get("FONTLAB_SCRIPTMIX_ROOT")
    if explicit is not None:
        root = Path(explicit)
        assert root.is_dir(), f"FONTLAB_SCRIPTMIX_ROOT is not a directory: {explicit}"
        return root
    sibling = ROOT.parent / "fontlab-python-scriptmix"
    return sibling if sibling.is_dir() else None


def test_resolve_scriptmix_root_when_env_points_to_missing_dir_then_fails(monkeypatch, tmp_path):
    monkeypatch.setenv("FONTLAB_SCRIPTMIX_ROOT", str(tmp_path / "nope"))
    with pytest.raises(AssertionError, match="not a directory"):
        resolve_scriptmix_root()


def test_resolve_scriptmix_root_when_env_set_to_dir_then_returns_it(monkeypatch, tmp_path):
    monkeypatch.setenv("FONTLAB_SCRIPTMIX_ROOT", str(tmp_path))
    assert resolve_scriptmix_root() == tmp_path


def test_scriptmix_pins_when_sibling_checkout_present_then_all_current():
    root = resolve_scriptmix_root()
    if root is None:
        pytest.skip("no Scriptmix checkout; set FONTLAB_SCRIPTMIX_ROOT")
    rows = [r for r in ADAPTATIONS if r["menu"].startswith(PREFIX)]
    assert len(rows) == 24, "the recorded Scriptmix-hosted row count changed"
    skipped: list[str] = []
    assert stale_pins(rows, root, skipped) == []
    if skipped:
        pytest.skip(f"App tab check skipped for {len(skipped)} absorbed rows; all other checks passed: {skipped[0]}")
