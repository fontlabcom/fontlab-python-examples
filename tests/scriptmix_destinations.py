# this_file: tests/scriptmix_destinations.py
"""Resolve a Scriptmix destination's identity hash, accepting only verified absorptions when absent.

A present file is always hashed (its pin must match). A file Scriptmix removed passes only when
scriptmix-absorptions.json records it, Scriptmix's own menu-consolidations.json marks the same
source bytes absorbed and implemented into the same launcher tab, the launcher exists and parses,
git shows the recorded removal (when available), and App declares the tab as a string literal.
Where App is absent and FONTLAB_EXAMPLES_SKIP_APP_TAB is set (public CI), only the App check
skips, with that reason; absent App without the variable fails.
Used by the Examples tests that check menu-adaptations.json / rescue-index.json destinations.
"""

import ast
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "fontlab-python-scriptmix/"
HOMEBREW_GIT = "/opt/homebrew/bin/git"
GIT = HOMEBREW_GIT if Path(HOMEBREW_GIT).is_file() else shutil.which("git")
SKIP_APP_TAB = "FONTLAB_EXAMPLES_SKIP_APP_TAB"
"""Set only where App is unavailable (public CI); its value is the stated skip reason."""
ABSORPTIONS = json.loads((ROOT / "scriptmix-absorptions.json").read_text())["absorptions"]


def scriptmix_root() -> Path:
    return Path(os.environ.get("FONTLAB_SCRIPTMIX_ROOT", str(ROOT.parent / "fontlab-python-scriptmix")))


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([GIT, "-C", str(root), *args], capture_output=True, check=False)


def _history(mix: Path, row: dict, pinned: bool) -> None:
    """Check the recorded removal commit in any git checkout; without git, only a pin may vouch."""
    removed, menu = row["removed_by"], row["menu"]
    reason = "no git executable" if GIT is None else None
    if reason is None and _git(mix, "rev-parse", "--git-dir").returncode != 0:
        reason = "Scriptmix is not a git checkout"
    if reason is not None:
        if pinned:
            return
        pytest.skip(f"{menu}: Scriptmix git history for removed_by {removed[:8]} is unavailable ({reason})")
    before = _git(mix, "show", f"{removed}^:{menu}")
    assert before.returncode == 0, f"{menu}: removed_by {removed[:8]} has no parent copy of the file"
    assert hashlib.sha256(before.stdout).hexdigest() == row["last_sha256"], f"{menu}: removed_by parent bytes differ"
    assert _git(mix, "cat-file", "-e", f"{removed}:{menu}").returncode != 0, f"{menu}: still present at removed_by"
    assert _git(mix, "merge-base", "--is-ancestor", removed, "HEAD").returncode == 0, f"{menu}: removed_by is not in this checkout"


def _declares(module: Path, tab: str) -> bool:
    tree = ast.parse(module.read_text(), feature_version=(3, 11))
    return any(isinstance(node, ast.Constant) and node.value == tab for node in ast.walk(tree))


def check_destination(menu, pin=None, *, scriptmix=None, app=None, rows=None) -> str:
    """Return the identity sha256 of a Scriptmix destination, or raise naming the problem."""
    mix = Path(scriptmix) if scriptmix else scriptmix_root()
    app = Path(app) if app else ROOT.parent / "fontlab-fontlabapp"
    relative = menu.removeprefix(PREFIX)
    path = mix / relative
    if path.is_file():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert pin is None or digest == pin, f"stale pin: {menu}"
        return digest
    row = next((r for r in (ABSORPTIONS if rows is None else rows) if r["menu"] == relative), None)
    assert row is not None, f"missing: {menu}"
    assert pin is None or row["last_sha256"] == pin, f"{menu}: absorption hash differs from the pin"
    into = row["absorbed_into"]
    transitions = json.loads((mix / "menu-consolidations.json").read_text())["transitions"]
    match = [
        t for t in transitions
        if t["source"]["path"] == relative and t["source"]["sha256"] == row["last_sha256"]
        and t["disposition"] == "absorbed"
        and t["destination"]["path"] == into["path"] and t["destination"]["tab"] == into["tab"]
    ]
    assert len(match) == 1, f"{menu}: no matching Scriptmix consolidation transition"
    assert match[0]["acceptance"]["state"] == "implemented", f"{menu}: consolidation is not implemented"
    launcher = mix / into["path"]
    assert launcher.is_file(), f"{menu}: launcher {into['path']} is missing"
    ast.parse(launcher.read_text(), feature_version=(3, 11))
    _history(mix, row, pinned=pin is not None)
    module = app / row["tab_declared_in"]
    if not module.is_file() and os.environ.get(SKIP_APP_TAB):
        pytest.skip(f"{menu}: App tab check skipped: {os.environ[SKIP_APP_TAB]}")
    assert module.is_file() and _declares(module, into["tab"]), f"{menu}: App does not declare tab {into['tab']!r}"
    return row["last_sha256"]
