# this_file: tests/test_historical_sources.py
"""Record integrity always runs; external original bytes are an optional audit."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest

from historical_sources import ROOT, archive_failures, archived_source, recorded_sha256, recorded_sources


def test_historical_hashes_when_loaded_then_index_and_notice_agree() -> None:
    sources = recorded_sources()
    index = json.loads((ROOT / "rescue-index.json").read_text())["menus"]
    assert len(sources) == 536, "Keep 494 menu identities and 42 source-only identities"
    assert all(sources[row["target"]] == row["target_sha256"] for row in index)


def test_unknown_historical_source_when_queried_then_refused() -> None:
    with pytest.raises(KeyError):
        recorded_sha256("rescued/not-recorded.py")


def test_external_audit_when_not_enabled_then_explicit_skip(monkeypatch) -> None:
    monkeypatch.delenv("FONTLAB_AUDIT_ARCHIVED_SOURCES", raising=False)
    with pytest.raises(pytest.skip.Exception, match="External source-byte audit"):
        archived_source("rescued/not-recorded.py")


def test_external_audit_when_bytes_corrupt_then_fails(monkeypatch, tmp_path) -> None:
    source = next(iter(recorded_sources()))
    path = tmp_path / source
    path.parent.mkdir(parents=True)
    path.write_bytes(b"incorrect original bytes")
    monkeypatch.setenv("FONTLAB_AUDIT_ARCHIVED_SOURCES", "1")
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(tmp_path))
    with pytest.raises(AssertionError):
        archived_source(source)


def test_external_original_bytes_when_available_then_all_recorded_hashes_match() -> None:
    failures = archive_failures(recorded_sources())
    assert not failures, "\n".join(failures)


def test_partial_archive_when_file_deleted_and_corrupted_then_both_failures_reported(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
) -> None:
    original = tmp_path / "original" / "rescued"
    original.mkdir(parents=True)
    sources = {}
    for name in ("deleted.py", "corrupt.py", "intact.py"):
        path = original / name
        path.write_bytes(b"original bytes\n")
        sources[f"rescued/{name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    copied = tmp_path / "copy"
    shutil.copytree(original.parent, copied)
    (copied / "rescued/deleted.py").unlink()
    (copied / "rescued/corrupt.py").write_bytes(b"corrupted bytes\n")
    monkeypatch.setenv("FONTLAB_AUDIT_ARCHIVED_SOURCES", "1")
    monkeypatch.setenv("FONTLAB_PRESERVED_ROOT", str(copied))
    monkeypatch.setitem(globals(), "recorded_sources", lambda: sources)
    with pytest.raises(AssertionError) as caught:
        test_external_original_bytes_when_available_then_all_recorded_hashes_match()
    message = str(caught.value)
    assert "Missing historical source: rescued/deleted.py" in message
    assert "Historical source hash mismatch: rescued/corrupt.py" in message
    assert "intact.py" not in message
