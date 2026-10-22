# this_file: tests/historical_sources.py
"""Historical identifiers from local records; optional external byte audits."""

import hashlib
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def recorded_sources() -> dict[str, str]:
    """Cross-check repeated identifiers without requiring archived source bytes."""
    index = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    records = json.loads((ROOT / "menu-adaptations.json").read_text())
    sources = {row["target"]: row["target_sha256"] for row in index}
    notice = (ROOT / "NOTICE").read_text()
    for row in records["adaptations"] + records["retirements"]:
        source, digest = row["source"], row["source_sha256"]
        assert re.fullmatch(r"[a-f0-9]{64}", digest), source
        if source in sources:
            assert sources[source] == digest, f"Conflicting historical hash: {source}"
        else:
            assert source in notice and digest in notice, source
        sources[source] = digest
    return sources


def recorded_sha256(source: str) -> str:
    """Return a recorded digest, never a claim about available original bytes."""
    return recorded_sources()[source]


def archived_root() -> Path:
    """Skip disabled audits or an absent archive, never an incomplete archive."""
    if os.environ.get("FONTLAB_AUDIT_ARCHIVED_SOURCES") != "1":
        pytest.skip("External source-byte audit: set FONTLAB_AUDIT_ARCHIVED_SOURCES=1")
    root = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
    if not (root / "rescued").is_dir():
        pytest.skip("External historical source absent: rescued/; set FONTLAB_PRESERVED_ROOT to an extracted archive")
    return root


def archived_source(source: str) -> Path:
    """Require a present, hash-matching file once the archive exists."""
    path = archived_root() / source
    assert path.is_file(), f"Missing historical source: {source}"
    if source in recorded_sources():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == recorded_sha256(source)
    return path


def archive_failures(sources: dict[str, str]) -> list[str]:
    """Inspect every recorded file so a missing source cannot hide corruption."""
    root = archived_root()
    failures = []
    for source, digest in sources.items():
        path = root / source
        try:
            if not path.is_file():
                failures.append(f"Missing historical source: {source}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                failures.append(f"Historical source hash mismatch: {source}")
        except OSError as error:
            failures.append(f"Unreadable historical source: {source}: {error}")
    return failures
