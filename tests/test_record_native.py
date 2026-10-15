# this_file: tests/test_record_native.py
"""record_native applies only proposals that match their evidence and current files."""

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from record_native import StaleProposal, record_native, validate

PORT = "ports/demo/example-aaaa.py"
BLOCKED = "ports/demo/blocked-bbbb.py"


def receipt_line(pid, path, digest, *, status="passed", blocked=False):
    snapshot = {
        "name": "Demo",
        "source_id": pid,
        "launched": True,
        "closed": False,
        "visible": True,
    }
    phases = {
        "launch": {
            "data": {"capability_failure": "needs X"} if blocked else {"launched": True}
        },
        "inspect": {"data": {"snapshot": snapshot}},
        "close": {
            "data": {
                "snapshot": {
                    "name": "Demo",
                    "source_id": pid,
                    "launched": False,
                    "closed": True,
                }
            }
        },
        "finish": {"data": {"host_alive": True, "clean": True}},
    }
    return {
        "port_id": pid,
        "implementation": "blocked" if blocked else "implemented",
        "status": status,
        "phases": phases,
        "continue_safe": True,
        "files": {path: digest},
    }


@pytest.fixture
def world(tmp_path):
    root, evidence = tmp_path / "repo", tmp_path / "evidence"
    for name, text in ((PORT, "print('ok')\n"), (BLOCKED, "raise\n")):
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    digests = {
        n: hashlib.sha256((root / n).read_bytes()).hexdigest() for n in (PORT, BLOCKED)
    }
    (evidence / "run").mkdir(parents=True)
    lines = [
        receipt_line("aaaa", PORT, digests[PORT]),
        receipt_line("bbbb", BLOCKED, digests[BLOCKED], blocked=True),
    ]
    (evidence / "run/final01.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in lines)
    )
    (evidence / "run/final01.summary.json").write_text(
        json.dumps({"driver_sha256": "d1"})
    )
    manifest = {
        "ports": [
            {
                "source_id": "aaaa",
                "name": "Demo",
                "implementation": "implemented",
                "native_acceptance": "unexecuted",
                "clean_room_receipt": "r/aaaa.json",
                "replacement_files": [PORT],
            },
            {
                "source_id": "bbbb",
                "name": "Blocked",
                "implementation": "blocked",
                "native_acceptance": "unexecuted",
                "clean_room_receipt": "r/bbbb.json",
                "replacement_files": [BLOCKED],
            },
        ]
    }
    proposal = {
        "driver_sha256": "d1",
        "ports": {
            pid: {
                "native_acceptance": "passed",
                "implementation": impl,
                "evidence": "run/final01.jsonl",
                "files": {path: digests[path]},
            }
            for pid, impl, path in (
                ("aaaa", "implemented", PORT),
                ("bbbb", "blocked", BLOCKED),
            )
        },
    }
    return root, evidence, manifest, {"records": {}}, proposal


def test_record_when_proposal_matches_then_passed_with_exact_projection(world):
    root, evidence, manifest, receipt, proposal = world
    counts = record_native(manifest, receipt, proposal, root, evidence, "abc1234")
    assert counts == {"passed": 1, "blocked_verified": 1}
    implemented, blocked = manifest["ports"]
    assert implemented["native_acceptance"] == "passed"
    assert implemented["native_evidence"]["catalog_record"] == "/records/aaaa"
    assert implemented["native_evidence"]["source"]["line"] == 1
    assert (
        blocked["native_acceptance"] == "unexecuted"
        and "native_evidence" not in blocked
    )
    record = receipt["records"]["aaaa"]
    assert record["launch"] == {
        "source_id": "aaaa",
        "launched": True,
        "closed": False,
        "visible": True,
    }
    assert record["close"] == {"source_id": "aaaa", "launched": False, "closed": True}
    assert set(receipt["records"]) == {"aaaa"}


def test_record_when_port_file_changed_then_refused_and_nothing_written(world):
    root, evidence, manifest, receipt, proposal = world
    before = deepcopy(manifest)
    (root / PORT).write_text("print('changed')\n")
    with pytest.raises(StaleProposal, match="changed since the native run"):
        record_native(manifest, receipt, proposal, root, evidence, "abc1234")
    assert manifest == before and receipt == {"records": {}}


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda p, e: p.update(driver_sha256="other"), "another driver"),
        (
            lambda p, e: p["ports"]["aaaa"].update(evidence="run/missing.jsonl"),
            "evidence file missing",
        ),
        (
            lambda p, e: p["ports"]["aaaa"].update(evidence="../outside.jsonl"),
            "Nonportable",
        ),
        (
            lambda p, e: p["ports"]["aaaa"].update(implementation="blocked"),
            "implementation differs",
        ),
        (
            lambda p, e: p["ports"]["aaaa"]["files"].update({PORT: "0" * 64}),
            "hashes differ",
        ),
        (
            lambda p, e: p["ports"].update(zzzz=dict(p["ports"]["aaaa"])),
            "not a clean-room",
        ),
    ],
)
def test_validate_when_proposal_inconsistent_then_refused(world, change, message):
    root, evidence, manifest, _, proposal = world
    change(proposal, evidence)
    ports = {r["source_id"]: r for r in manifest["ports"]}
    with pytest.raises(StaleProposal, match=message):
        validate(proposal, ports, root, evidence)


def test_validate_when_receipt_failed_or_duplicated_then_refused(world):
    root, evidence, manifest, _, proposal = world
    path = evidence / "run/final01.jsonl"
    lines = path.read_text().splitlines()
    failed = json.loads(lines[0]) | {"status": "failed"}
    path.write_text(json.dumps(failed) + "\n" + lines[1] + "\n")
    ports = {r["source_id"]: r for r in manifest["ports"]}
    with pytest.raises(StaleProposal, match="not a clean pass"):
        validate(proposal, ports, root, evidence)
    path.write_text(lines[0] + "\n" + lines[0] + "\n" + lines[1] + "\n")
    with pytest.raises(StaleProposal, match="2 receipts"):
        validate(proposal, ports, root, evidence)


def test_record_when_applied_twice_then_same_result(world):
    root, evidence, manifest, receipt, proposal = world
    record_native(manifest, receipt, proposal, root, evidence, "abc1234")
    once = deepcopy((manifest, receipt))
    record_native(manifest, receipt, proposal, root, evidence, "abc1234")
    assert (manifest, receipt) == once


def test_record_when_snapshot_has_empty_error_field_then_accepted_but_error_refused(
    world,
):
    root, evidence, manifest, receipt, proposal = world
    path = evidence / "run/final01.jsonl"
    lines = [json.loads(line) for line in path.read_text().splitlines()]
    lines[0]["phases"]["inspect"]["data"]["snapshot"]["error"] = ""
    path.write_text("".join(json.dumps(r) + "\n" for r in lines))
    record_native(manifest, receipt, proposal, root, evidence, "abc1234")
    assert receipt["records"]["aaaa"]["inspect"]["error"] == ""
    lines[0]["phases"]["inspect"]["data"]["snapshot"]["error"] = "boom"
    path.write_text("".join(json.dumps(r) + "\n" for r in lines))
    ports = {r["source_id"]: r for r in manifest["ports"]}
    with pytest.raises(StaleProposal, match="no visible launched window"):
        validate(proposal, ports, root, evidence)
