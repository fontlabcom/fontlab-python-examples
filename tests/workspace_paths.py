# this_file: tests/workspace_paths.py
"""Locate the FontLab scripting workspace and the ignored ``_reference`` tree.

The checkout may be the canonical one (workspace = its parent) or a git worktree
anywhere below the workspace (for example ``<workspace>/.worktrees/<name>``).
``FONTLAB_WORKSPACE`` overrides the search; ``FONTLAB_EXAMPLES_REFERENCE`` names a
checkout that holds the untracked ``_reference`` tree.
"""

import os
from pathlib import Path

CHECKOUT = Path(__file__).resolve().parents[1]
MARKER = "verification/issue-101-ecosystem/evidence"


def find_workspace() -> Path:
    override = os.environ.get("FONTLAB_WORKSPACE")
    if override:
        return Path(override).resolve()
    for candidate in CHECKOUT.parents:
        if (candidate / MARKER).is_dir():
            return candidate
    return CHECKOUT.parent  # canonical layout; callers skip when evidence is absent


WORKSPACE = find_workspace()


def reference_file(relative: str) -> Path:
    """``_reference/...`` is untracked: take it from this checkout, else the workspace's."""
    own = CHECKOUT / relative
    if own.exists():
        return own
    override = os.environ.get("FONTLAB_EXAMPLES_REFERENCE")
    base = Path(override) if override else WORKSPACE / "fontlab-python-examples"
    return base / relative
