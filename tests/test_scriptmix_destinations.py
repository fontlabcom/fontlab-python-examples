# this_file: tests/test_scriptmix_destinations.py
"""A Scriptmix destination is either present with its pinned bytes or a verified absorption."""

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
import scriptmix_destinations
from scriptmix_destinations import ABSORPTIONS, GIT, check_destination

OLD = b"print('old')\n"
PIN = hashlib.sha256(OLD).hexdigest()
MENU = "Scripts/Contours/Old.py"
LAUNCHER = "Scripts/Contours/Studio.py"


def git(root: Path, *args: str) -> str:
    if GIT is None:
        pytest.skip("no git executable to build the synthetic Scriptmix history")
    return subprocess.run(
        [GIT, "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def make(tmp_path: Path, *, state="implemented", tab="Old Tab", declared="Old Tab", repo=True):
    """Build a Scriptmix checkout that removed MENU, plus an App module declaring its tab."""
    mix, app = tmp_path / "mix", tmp_path / "app"
    (mix / "Scripts/Contours").mkdir(parents=True)
    (app / "src").mkdir(parents=True)
    (app / "src/tabs.py").write_text(f"TABS = ({declared!r},)\n")
    (mix / MENU).write_bytes(OLD)
    if repo:
        git(mix, "init", "-q")
        git(mix, "-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
        git(mix, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "old")
    (mix / MENU).unlink()
    (mix / LAUNCHER).write_text("def main():\n    pass\n")
    transition = {
        "source": {"path": MENU, "commit": "c" * 40, "sha256": PIN},
        "disposition": "absorbed",
        "destination": {"path": LAUNCHER, "tab": tab},
        "acceptance": {"state": state},
    }
    (mix / "menu-consolidations.json").write_text(json.dumps({"transitions": [transition]}))
    removed = "0" * 40
    if repo:
        git(mix, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
        git(mix, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "absorb")
        removed = git(mix, "rev-parse", "HEAD")
    row = {
        "menu": MENU,
        "last_sha256": PIN,
        "removed_by": removed,
        "consolidation_source_commit": "c" * 40,
        "absorbed_into": {"path": LAUNCHER, "tab": "Old Tab"},
        "tab_declared_in": "src/tabs.py",
    }
    return mix, app, row


def check(menu, pin, mix, app, rows):
    return check_destination(menu, pin, scriptmix=mix, app=app, rows=rows)


def test_present_file_when_pin_matches_then_its_hash_is_returned(tmp_path):
    mix, app, _ = make(tmp_path)
    (mix / "Scripts/A.py").write_bytes(OLD)
    assert check("fontlab-python-scriptmix/Scripts/A.py", PIN, mix, app, []) == PIN


def test_present_file_when_listed_with_wrong_pin_then_strict_check_wins(tmp_path):
    mix, app, row = make(tmp_path)
    (mix / MENU).write_bytes(b"reappeared after a revert\n")
    with pytest.raises(AssertionError, match="stale pin"):
        check(MENU, PIN, mix, app, [row])


def test_absent_file_when_unlisted_then_missing(tmp_path):
    mix, app, _ = make(tmp_path)
    with pytest.raises(AssertionError, match="missing"):
        check(MENU, PIN, mix, app, [])


def test_absent_file_when_fully_absorbed_then_frozen_pin_is_returned(tmp_path):
    mix, app, row = make(tmp_path)
    assert check(MENU, PIN, mix, app, [row]) == PIN
    assert check("fontlab-python-scriptmix/" + MENU, None, mix, app, [row]) == PIN


def test_absent_file_when_row_hash_differs_from_pin_then_rejected(tmp_path):
    mix, app, row = make(tmp_path)
    with pytest.raises(AssertionError, match="pin"):
        check(MENU, "1" * 64, mix, app, [row])


def test_absent_file_when_consolidation_is_only_proposed_then_rejected(tmp_path):
    mix, app, row = make(tmp_path, state="proposed")
    with pytest.raises(AssertionError, match="implemented"):
        check(MENU, PIN, mix, app, [row])


def test_absent_file_when_consolidation_tab_differs_then_rejected(tmp_path):
    mix, app, row = make(tmp_path, tab="Other Tab")
    with pytest.raises(AssertionError, match="consolidation"):
        check(MENU, PIN, mix, app, [row])


def test_absent_file_when_launcher_missing_then_rejected(tmp_path):
    mix, app, row = make(tmp_path)
    (mix / LAUNCHER).unlink()
    with pytest.raises(AssertionError, match="launcher"):
        check(MENU, PIN, mix, app, [row])


def test_absent_file_when_app_does_not_declare_tab_then_rejected(tmp_path):
    mix, app, row = make(tmp_path, declared="Renamed Tab")
    with pytest.raises(AssertionError, match="tab"):
        check(MENU, PIN, mix, app, [row])


def test_absent_file_when_removal_commit_is_wrong_then_rejected(tmp_path):
    mix, app, row = make(tmp_path)
    row["removed_by"] = git(mix, "rev-parse", "HEAD~1")
    with pytest.raises(AssertionError, match="removed_by"):
        check(MENU, PIN, mix, app, [row])


def test_unpinned_absent_file_when_history_unavailable_then_skipped(tmp_path):
    mix, app, row = make(tmp_path, repo=False)
    assert check(MENU, PIN, mix, app, [row]) == PIN
    with pytest.raises(pytest.skip.Exception, match="git history"):
        check(MENU, None, mix, app, [row])


def test_unpinned_absent_file_when_git_executable_missing_then_skipped(tmp_path, monkeypatch):
    mix, app, row = make(tmp_path)
    monkeypatch.setattr(scriptmix_destinations, "GIT", None)
    assert check(MENU, PIN, mix, app, [row]) == PIN
    with pytest.raises(pytest.skip.Exception, match="no git executable"):
        check(MENU, None, mix, app, [row])


def test_recorded_absorptions_when_loaded_then_name_one_removal_per_path():
    menus = [row["menu"] for row in ABSORPTIONS]
    assert len(menus) == len(set(menus)) == 7
    assert {row["removed_by"] for row in ABSORPTIONS} == {
        "cb3a95057641f3b2382a887172fab524dbc4901a"
    }
