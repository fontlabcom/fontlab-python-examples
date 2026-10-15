# this_file: tests/test_clean_room_relocation.py
"""Relocated metadata and host-free launch contracts; no originals are read."""

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_pending_launch_when_no_host_then_reports_spec_before_host_or_builder(
    monkeypatch,
):
    from fontlab_python_examples import launcher

    row = {
        "implementation": "clean_room_pending",
        "source_id": "owned-id",
        "spec": "clean-room-specs/owned-id.md",
    }
    monkeypatch.setattr(launcher, "describe", lambda name: row)

    def forbidden(*args):
        pytest.fail("Relocated launch must not access the host or removed code")

    monkeypatch.setattr(launcher, "_host", forbidden)
    monkeypatch.setattr(launcher, "_builder", forbidden)
    with pytest.raises(NotImplementedError, match="clean-room.*owned-id.md"):
        launcher.launch("owned")


def test_test_guard_when_state_changes_then_only_pending_skips():
    from tests.port_state import require_current

    with pytest.raises(pytest.skip.Exception, match="clean_room_pending"):
        require_current({"implementation": "clean_room_pending", "source_id": "owned"})
    for state in ("implemented", "blocked"):
        require_current({"implementation": state, "source_id": "owned"})


def test_all_pending_launches_when_catalogued_then_refuse_without_host(monkeypatch):
    from fontlab_python_examples import launcher

    def forbidden(*args):
        pytest.fail("A pending record must not touch Qt or its removed target")

    monkeypatch.setattr(launcher, "_host", forbidden)
    monkeypatch.setattr(launcher, "_builder", forbidden)
    pending = [
        row
        for row in launcher.available()
        if row["implementation"] == "clean_room_pending"
    ]
    for row in pending:
        with pytest.raises(NotImplementedError, match="clean-room"):
            launcher.launch(row["source_id"])
        assert launcher.inspect(row["source_id"])["launched"] is False


def test_overlay_when_pending_then_provenance_preserved_and_states_regenerate():
    from catalog_ports import apply_port_states

    source = {"id": "owned", "sha256": "a" * 64, "port_state": "pending"}
    resource = {"id": "asset", "sha256": "b" * 64, "license": {"selected": "old"}}
    catalog = {"files": [source, resource], "examples": [{"id": "owned"}], "counts": {}}
    row = {
        "source_id": "owned",
        "source": {"sha256": source["sha256"]},
        "implementation": "clean_room_pending",
        "native_acceptance": "unexecuted",
        "target_path": "ports/owned.py",
        "archive": "owner/private@revision:ports/owned.py",
        "spec": "clean-room-specs/owned.md",
        "resources": [
            {
                "source_id": "asset",
                "source": {"sha256": resource["sha256"]},
                "target_path": "ports/owned.png",
                "archive": "private:ports/owned.png",
            }
        ],
    }
    apply_port_states(catalog, {"ports": [row]})
    assert source["port_state"] == "clean_room_pending"
    assert source["archive"] == row["archive"] and source["sha256"] == "a" * 64
    assert resource["port_state"] == "clean_room_pending" and "license" not in resource
    assert catalog["examples"][0]["spec"] == row["spec"]
    assert catalog["counts"]["examples_clean_room_pending"] == 1
    once = deepcopy(catalog)
    apply_port_states(catalog, {"ports": [row]})
    assert catalog == once, "Applying the overlay twice must be deterministic"
    row.update(implementation="implemented", native_acceptance="passed")
    apply_port_states(catalog, {"ports": [row]})
    assert source["port_state"] == "implemented" and source["runtime_state"] == "passed"
    assert catalog["counts"]["examples_clean_room_pending"] == 0
    assert catalog["counts"]["examples_ported"] == 1


def test_overlay_when_source_hash_differs_then_rejects_stale_metadata():
    from catalog_ports import apply_port_states

    catalog = {
        "files": [{"id": "owned", "sha256": "a" * 64}],
        "examples": [],
        "counts": {},
    }
    row = {"source_id": "owned", "source": {"sha256": "b" * 64}, "resources": []}
    with pytest.raises(ValueError, match="hash mismatch"):
        apply_port_states(catalog, {"ports": [row]})


def test_relocated_records_when_catalogued_then_metadata_specs_and_removed_files_match():
    ports = json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
    index = json.loads((ROOT / "clean-room-specs/INDEX.json").read_text())["ports"]
    official = [
        r for r in ports if r["source"]["path"].startswith("src/pyqt-official/")
    ]
    assert len(official) == 187, (
        "Every original official record must remain accounted for"
    )
    assert {r["port_id"] for r in index} == {r["source_id"] for r in official}
    for row in official:
        if row["implementation"] != "clean_room_pending":
            continue
        assert row["native_acceptance"] == "unexecuted" and "native_evidence" not in row
        assert row["spec"] == f"clean-room-specs/{row['source_id']}.md"
        assert (ROOT / row["spec"]).is_file()
        for item in (row, *row["resources"]):
            assert "license" not in item, (
                "Removed files must make no public licence grant"
            )
            assert not (ROOT / item["target_path"]).exists(), item["target_path"]
            assert item["archive"] == (
                "fontlabcom/fontlab-python-examples-reference@040b2e8:pyqt-official-ports/"
                + item["target_path"]
            )
    assert not (ROOT / "ports/pyqt-official-LICENSE.md").exists()
    assert {p.suffix for p in (ROOT / "clean-room-specs").iterdir()} <= {".md", ".json"}
    assert not (ROOT / "pyqt-official-ports").exists()
