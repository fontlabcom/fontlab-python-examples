# SPDX-License-Identifier: Apache-2.0
# this_file: tests/test_cleanroom_integration.py
"""Receipt integration preserves immutable provenance and requires real replacements."""

import hashlib
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from integrate_cleanroom import checked_path, integrate, merge_receipts, read_receipts


def test_receipts_when_merged_then_complete_reviewed_unexecuted_and_idempotent():
    receipts = read_receipts(ROOT)
    original = json.loads((ROOT / "catalog/ports.json").read_text())
    merged = merge_receipts(original, receipts)
    clean = [r for r in merged["ports"] if r["source_id"] in receipts]
    assert len(clean) == 187
    assert Counter(r["implementation"] for r in clean) == {
        "implemented": 127,
        "blocked": 60,
    }
    assert not any(r["implementation"] == "clean_room_pending" for r in merged["ports"])
    before = {r["source_id"]: r for r in original["ports"]}
    for row in merged["ports"]:
        old = before[row["source_id"]]
        if row["source_id"] not in receipts:
            assert row == old
            continue
        assert row["source"] == old["source"] and row["resources"] == old["resources"]
        assert row["archive"] == old["archive"] and row["spec"] == old["spec"]
        assert row["native_acceptance"] == "unexecuted" and "native_evidence" not in row
        assert row["license"]["selected"] == "Apache-2.0"
        assert row["license"]["review_state"] == "reviewed"
        assert (
            row["license"]["spec_sha256"] == receipts[row["source_id"]]["spec_sha256"]
        )
    assert merge_receipts(merged, receipts) == merged


@pytest.mark.parametrize(
    "failure", ["hash", "target", "reason", "missing", "traversal", "unknown"]
)
def test_receipt_when_invalid_then_rejected_without_catalog_write(tmp_path, failure):
    spec = {
        "port_id": "one",
        "target_path": "ports/one.py",
        "spec_file": "clean-room-specs/one.md",
    }
    for directory in ["catalog", "clean-room-specs", "clean-room/receipts", "ports"]:
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    (tmp_path / spec["spec_file"]).write_text("A fresh specification")
    (tmp_path / "clean-room-specs/INDEX.json").write_text(json.dumps({"ports": [spec]}))
    (tmp_path / spec["target_path"]).write_text(
        "# SPDX-License-Identifier: Apache-2.0\n# Clean-room implementation from "
        + spec["spec_file"]
        + "\n"
    )
    receipt = {
        "port_id": "one",
        "target_path": spec["target_path"],
        "files": [spec["target_path"]],
        "implementation": "implemented",
        "blocked_reason": None,
        "spec_sha256": hashlib.sha256(
            (tmp_path / spec["spec_file"]).read_bytes()
        ).hexdigest(),
    }
    if failure == "hash":
        receipt["spec_sha256"] = "0" * 64
    if failure == "target":
        receipt["target_path"] = "ports/wrong.py"
    if failure == "reason":
        receipt.update(implementation="blocked", blocked_reason="")
    if failure == "missing":
        receipt["files"].append("ports/absent.py")
    if failure == "traversal":
        receipt["files"].append("ports/../../escape.py")
    if failure == "unknown":
        receipt["port_id"] = "unknown"
    (tmp_path / "clean-room/receipts/one.json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError):
        read_receipts(tmp_path)
    assert not list((tmp_path / "catalog").iterdir())


def test_integrate_when_metadata_only_then_reproducible_and_source_identities_preserved(
    tmp_path,
):
    for directory in ["catalog", "clean-room", "clean-room-specs", "ports"]:
        shutil.copytree(ROOT / directory, tmp_path / directory)
    before = json.loads((tmp_path / "catalog/sources.json").read_text())
    integrate(tmp_path)
    first = {
        name: (tmp_path / "catalog" / name).read_bytes()
        for name in ["ports.json", "sources.json", "INDEX.md"]
    }
    integrate(tmp_path)
    assert first == {name: (tmp_path / "catalog" / name).read_bytes() for name in first}
    after = json.loads(first["sources.json"])
    assert [
        (r["id"], r["sha256"], r["git_blob_sha"], r["path"]) for r in before["files"]
    ] == [(r["id"], r["sha256"], r["git_blob_sha"], r["path"]) for r in after["files"]]
    manifest = json.loads(first["ports.json"])
    assert (
        manifest["source_catalog_sha256"]
        == hashlib.sha256(first["sources.json"]).hexdigest()
    )
    assert after["counts"]["port_states"] == {"implemented": 148, "blocked": 151}
    assert after["counts"]["examples_native_executed"] == 21
    for row in after["files"]:
        if row.get("clean_room_receipt"):
            assert "license" not in row, (
                "Replacement grant must not relicense original bytes"
            )


def test_checked_path_when_symlink_leaves_root_then_rejected(tmp_path):
    (tmp_path / "outside").symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError):
        checked_path(tmp_path, "outside/anything")


def test_committed_catalog_when_integrated_then_exact_receipts_and_counts():
    manifest = json.loads((ROOT / "catalog/ports.json").read_text())
    sources = json.loads((ROOT / "catalog/sources.json").read_text())
    receipts = read_receipts(ROOT)
    assert Counter(r["implementation"] for r in manifest["ports"]) == {
        "implemented": 148,
        "blocked": 151,
    }
    assert len([r for r in manifest["ports"] if r.get("clean_room_receipt")]) == 187
    for row in manifest["ports"]:
        if row["source_id"] in receipts:
            assert row["implementation"] == receipts[row["source_id"]]["implementation"]
    assert sources["counts"]["examples_clean_room_pending"] == 0
