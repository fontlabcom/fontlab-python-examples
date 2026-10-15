# this_file: tests/test_catalog_reviews.py
"""Cross-check reviewed catalog decisions against receipts and pinned identities."""

import hashlib
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from catalog_reviews import apply_reviews

SOURCES = json.loads((ROOT / "catalog/sources.json").read_text())
PORTS = json.loads((ROOT / "catalog/ports.json").read_text())["ports"]
FILES = {row["id"]: row for row in SOURCES["files"]}


def pointer(document, value):
    """Read the JSON pointers used by the evidence receipts."""
    for key in value.lstrip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document


def project(value):
    return {
        key: value[key]
        for key in ("source_id", "launched", "closed", "visible", "error")
        if key in value
    }


def test_native_fields_when_passed_then_each_has_matching_launch_and_close():
    receipt = json.loads(
        (ROOT / "verification/catalog-native-evidence.json").read_text()
    )
    implemented = {
        row["source_id"] for row in PORTS if row["implementation"] == "implemented"
    }
    accepted = {
        row["source_id"]
        for row in PORTS
        if row["implementation"] == "implemented"
        and row["native_acceptance"] == "passed"
    }
    assert len(implemented) == SOURCES["counts"]["examples_ported"]
    assert accepted <= set(receipt["records"]), "Current passes need evidence"
    assert set(receipt["records"]) <= {row["source_id"] for row in PORTS}
    for row in PORTS:
        if row["source_id"] not in implemented:
            assert row["native_acceptance"] == "unexecuted"
            assert "native_evidence" not in row
            continue
        if row["native_acceptance"] != "passed":
            assert "native_evidence" not in row
            continue
        assert (ROOT / row["native_evidence"]["report"]).is_file(), (
            "Native acceptance must cite an existing receipt"
        )
        ref = row["native_evidence"]["catalog_record"]
        assert ref == "/records/" + row["source_id"]
        evidence = pointer(receipt, ref)
        assert evidence["name"] == row["name"]
        for phase in ["launch", "inspect"]:
            assert evidence[phase]["source_id"] == row["source_id"]
            assert evidence[phase]["launched"] is True
            assert evidence[phase]["closed"] is False
            assert evidence[phase]["visible"] is True
            assert not evidence[phase].get("error")
        assert evidence["close"] == {
            "source_id": row["source_id"],
            "closed": True,
            "launched": False,
        }
        assert evidence["host_alive"] is True
        assert row["native_evidence"]["source"] == evidence["source"]


def test_native_receipt_when_originals_available_then_exact_file_and_record_match():
    receipt = json.loads(
        (ROOT / "verification/catalog-native-evidence.json").read_text()
    )
    external = ROOT.parent / "verification/issue-101-ecosystem/evidence"
    if not external.is_dir():
        pytest.skip(
            "Workspace native originals unavailable; portable receipt checked separately"
        )
    cache = {}
    for row in receipt["records"].values():
        source = row["source"]
        assert source["root"] in {"repository", "ecosystem-evidence"}
        relative = Path(source["file"])
        assert not relative.is_absolute() and ".." not in relative.parts
        path = (ROOT if source["root"] == "repository" else external) / source["file"]
        assert path.is_file(), source
        if path not in cache:
            data = path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == source["sha256"], source
            cache[path] = data.decode()
        text = cache[path]
        if "line" in source:
            record = json.loads(text.splitlines()[source["line"] - 1])
            assert record["name"] == row["name"]
            assert record["host_alive_after"] is True
        else:
            record = pointer(json.loads(text), source["pointer"])
        for phase, record_pointer in source["phase_pointers"].items():
            assert project(pointer(record, record_pointer)) == row[phase], source
        assert (
            pointer(
                json.loads(text) if "line" not in source else record,
                source["host_alive_pointer"],
            )
            is True
        )


def test_candidate_reviews_when_resolved_then_keep_all_original_mappings():
    reviewed = [row for row in SOURCES["examples"] if "classification_review" in row]
    assert len(reviewed) == 17
    assert Counter(row["classification"] for row in reviewed) == {
        "auxiliary": 2,
        "plugin": 10,
        "entrypoint": 1,
        "setup-entrypoint": 1,
        "qml-resource": 2,
        "qml-entrypoint": 1,
    }
    assert SOURCES["counts"]["ambiguous_candidates"] == 0
    for row in reviewed:
        review = row["classification_review"]
        assert row["static_classification"] == "ambiguous"
        assert review["state"] == "reviewed" and review["reason"]
        assert review["evidence"] and row["ambiguity"] is None
        assert review["source_sha256"] == FILES[row["id"]]["sha256"]
        assert FILES[row["id"]]["classification_review"] == review
        assert row["id"] in row["original_file_ids"]
        for owner in review["owner_example_ids"]:
            assert owner in {e["id"] for e in SOURCES["examples"]}
    # The previously missed mathtext launcher stays required, with its blocker explicit.
    mathtext = next(e for e in reviewed if e["id"] == "3425e97bf3542f90")
    assert (
        "backend_qt5agg"
        in mathtext["classification_review"]["implementation_constraint"]
    )


def test_shared_reviews_when_resolved_then_scope_and_reverse_membership_agree():
    reviewed = [row for row in FILES.values() if "ownership_review" in row]
    assert len(reviewed) == 69
    examples = {row["id"]: row for row in SOURCES["examples"]}
    for row in reviewed:
        review = row["ownership_review"]
        assert review["state"] == "reviewed" and review["reason"]
        assert review["source_sha256"] == row["sha256"]
        assert review["scope"] in {
            "example",
            "collection",
            "repository",
            "documentation",
        }
        assert "unresolved" not in row["association_state"]
        for owner in row["example_ids"]:
            assert row["id"] in examples[owner]["original_file_ids"]
    icon = FILES["35b8f74bbe2972a7"]
    assert icon["example_ids"] == ["d69bb62e126a51e9"]


def test_licenses_when_nonofficial_then_every_port_and_resource_has_file_review():
    licenses = json.loads((ROOT / "catalog/licenses.json").read_text())
    reviews = licenses["files"]
    for port in PORTS:
        if port["source"]["path"].startswith("src/pyqt-official/"):
            if port["implementation"] == "clean_room_pending":
                assert "license" not in port
            else:
                assert port["license"]["selected"] == "Apache-2.0"
            continue
        for row in [port, *port["resources"]]:
            review = reviews[row["target_path"]]
            assert row["license"][
                "file_review"
            ] == "catalog/licenses.json#/files/" + row["target_path"].replace("/", "~1")
            assert review["source_id"] == row["source_id"]
            assert review["source_sha256"] == FILES[row["source_id"]]["sha256"]
            assert review["attribution"] and review["reason"] and review["evidence"]
            for evidence in review["evidence"]:
                original = FILES[evidence["source_id"]]
                assert evidence["sha256"] == original["sha256"]
                assert evidence["upstream_url"] == original["upstream_url"]
            if review["state"] == "unresolved":
                assert row["license"]["review_state"] == "unresolved"
    insights = json.loads((ROOT / "catalog/insights.json").read_text())["insights"]
    for row in insights:
        assert reviews[row["target_path"]]["selected"] == "Apache-2.0"
    for path, review in reviews.items():
        assert review["target_path"] == path
        planned = {p["target_path"] for p in PORTS if p["implementation"] == "blocked"}
        if path not in planned:
            assert (ROOT / path).is_file()


@pytest.mark.parametrize("section", ["classifications", "ownership"])
def test_reviews_when_source_hash_changes_then_reject_stale_decision(section):
    catalog = deepcopy(SOURCES)
    reviews = json.loads((ROOT / "catalog/reviews.json").read_text())
    first = next(iter(reviews[section]))
    reviews[section][first]["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="review hash mismatch"):
        apply_reviews(catalog, reviews)


def test_reviews_when_applied_twice_then_static_evidence_and_output_are_identical():
    catalog = deepcopy(SOURCES)
    reviews = json.loads((ROOT / "catalog/reviews.json").read_text())
    apply_reviews(catalog, reviews)
    first = deepcopy(catalog)
    apply_reviews(catalog, reviews)
    assert catalog == first == SOURCES, (
        "Reapplying reviews must preserve raw observations"
    )


def test_reviews_when_no_decisions_then_ambiguity_is_preserved():
    catalog = deepcopy(SOURCES)
    for row in catalog["examples"]:
        if "static_classification" in row:
            row["classification"] = row["static_classification"]
    apply_reviews(catalog, {"classifications": {}, "ownership": {}})
    assert catalog["counts"]["ambiguous_candidates"] == 17, (
        "An empty review must not resolve a candidate without evidence"
    )


@pytest.mark.parametrize("field", ["state", "reason", "evidence"])
def test_reviews_when_evidence_or_reasoning_missing_then_no_state_is_changed(field):
    catalog = deepcopy(SOURCES)
    reviews = json.loads((ROOT / "catalog/reviews.json").read_text())
    next(iter(reviews["classifications"].values())).pop(field)
    with pytest.raises(ValueError, match="Review needs reasoning and evidence"):
        apply_reviews(catalog, reviews)
    assert catalog == SOURCES, (
        "Reject unsupported review claims before changing records"
    )


def test_review_citations_when_originals_available_then_source_records_match():
    external = ROOT.parent / "verification/issue-101-ecosystem/evidence"
    if not external.is_dir():
        pytest.skip("Workspace source observations unavailable")
    reviews = json.loads((ROOT / "catalog/reviews.json").read_text())
    for section in ["classifications", "ownership"]:
        for source_id, review in reviews[section].items():
            for evidence in review["evidence"]:
                if "source_id" in evidence:
                    original = FILES[evidence["source_id"]]
                    assert evidence["sha256"] == original["sha256"]
                    continue
                path = external / evidence["file"]
                assert (
                    hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
                )
                record = pointer(json.loads(path.read_text()), evidence["pointer"])
                if isinstance(record, list):
                    assert any(row["id"] == source_id for row in record)
                else:
                    assert (
                        record.get("source_id", record.get("id", record.get("qml_id")))
                        == source_id
                    )
