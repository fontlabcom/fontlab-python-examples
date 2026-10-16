# this_file: tests/test_record_native.py
"""record_native records only complete, clean receipts bound to a clean run commit."""

import hashlib
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from record_native import StaleProposal, propose, record_native, validate

PORT = "ports/demo/example-aaaa.py"
HELPER = "ports/demo/helper-cccc.py"
BLOCKED = "ports/demo/blocked-bbbb.py"
DRIVER = "tools/native_cleanroom.py"
PACKAGE = "fontlab_python_examples/launcher.py"


def git(root, *args):
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def envelope(data):
    return {"ok": True, "path_restored": True, "host_seconds": 0.02, "data": data}


def teardown():
    return {
        "clean": True,
        "surviving_objects": 0,
        "new_windows": 0,
        "new_threads": [],
        "temporary_directories_remaining": 0,
        "registry_empty": True,
        "host_alive": True,
        "new_file_descriptors": None,
    }


def implemented_receipt(pid, files):
    shown = {
        "name": "Demo",
        "source_id": pid,
        "launched": True,
        "closed": False,
        "visible": True,
    }
    return {
        "port_id": pid,
        "implementation": "implemented",
        "status": "passed",
        "continue_safe": True,
        "files": files,
        "phases": {
            "prepare": envelope({"import_verified": True}),
            "launch": envelope({"launched": True, "owned_objects": 3}),
            "inspect": envelope(
                {"visible": True, "top_level": True, "snapshot": shown}
            ),
            "close": envelope(
                {
                    "closed": True,
                    "snapshot": {
                        "name": "Demo",
                        "source_id": pid,
                        "launched": False,
                        "closed": True,
                    },
                }
            ),
            "verify": envelope(teardown()),
            "finish": envelope(teardown()),
        },
    }


def blocked_receipt(pid, files):
    clean = teardown() | {"new_file_descriptors": 0}
    return {
        "port_id": pid,
        "implementation": "blocked",
        "status": "passed",
        "continue_safe": True,
        "files": files,
        "phases": {
            "prepare": envelope({"import_verified": True}),
            "launch": envelope(
                {"capability_failure": "needs X", "host_accessed": False}
            ),
            "inspect": envelope({"blocked": True, "clean": True}),
            "close": envelope({"closed": True, "snapshot": {}}),
            "verify": envelope(clean),
            "finish": envelope(clean),
        },
    }


@pytest.fixture
def world(tmp_path):
    root, evidence = tmp_path / "repo", tmp_path / "evidence"
    texts = {
        PORT: 'S.port("demo/helper-cccc.py")\n',
        HELPER: "print('helper')\n",
        BLOCKED: "raise NotImplementedError\n",
        DRIVER: "# driver\n",
        PACKAGE: "# launcher\n",
    }
    for name, text in texts.items():
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
    git(root, "init", "-q")
    git(root, "add", ".")
    git(
        root,
        "-c",
        "user.name=t",
        "-c",
        "user.email=t@example.com",
        "commit",
        "-qm",
        "run",
    )
    commit = git(root, "rev-parse", "HEAD")
    deps = {
        "aaaa": {n: sha(root / n) for n in sorted([PACKAGE, PORT, HELPER])},
        "bbbb": {n: sha(root / n) for n in sorted([PACKAGE, BLOCKED])},
    }
    (evidence / "run").mkdir(parents=True)
    lines = [
        implemented_receipt("aaaa", deps["aaaa"]),
        blocked_receipt("bbbb", deps["bbbb"]),
    ]
    (evidence / "run/final01.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in lines)
    )
    summary = {
        "driver_sha256": sha(root / DRIVER),
        "examples_commit": commit,
        "examples_dirty": False,
        "revision_unchanged": True,
    }
    (evidence / "run/final01.summary.json").write_text(json.dumps(summary))
    manifest = {
        "ports": [
            {
                "source_id": "aaaa",
                "name": "Demo",
                "implementation": "implemented",
                "native_acceptance": "unexecuted",
                "clean_room_receipt": "r/aaaa.json",
                "target_path": PORT,
                "replacement_files": [PORT],
            },
            {
                "source_id": "bbbb",
                "name": "Blocked",
                "implementation": "blocked",
                "native_acceptance": "unexecuted",
                "clean_room_receipt": "r/bbbb.json",
                "target_path": BLOCKED,
                "replacement_files": [BLOCKED],
            },
        ]
    }
    proposal = propose([evidence / "run/final01.jsonl"], evidence)
    return root, evidence, manifest, {"records": {}}, proposal, commit


def ports_of(manifest):
    return {r["source_id"]: r for r in manifest["ports"]}


def rewrite(evidence, change):
    path = evidence / "run/final01.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    change(rows)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))


def test_propose_when_receipts_then_proposal_binds_commit_driver_and_closure(world):
    _root, _evidence, _manifest, _receipt, proposal, commit = world
    assert proposal["examples_commit"] == commit
    assert set(proposal["ports"]) == {"aaaa", "bbbb"}
    assert set(proposal["ports"]["aaaa"]["files"]) == {PACKAGE, PORT, HELPER}


def test_record_when_everything_matches_then_passed_and_blocked_verified(world):
    root, evidence, manifest, receipt, proposal, commit = world
    counts = record_native(manifest, receipt, proposal, root, evidence, commit)
    assert counts == {"passed": 1, "blocked_verified": 1}
    implemented, blocked = manifest["ports"]
    assert implemented["native_acceptance"] == "passed"
    assert implemented["native_evidence"]["implementation_commit"] == commit
    assert (
        blocked["native_acceptance"] == "unexecuted"
        and "native_evidence" not in blocked
    )
    assert receipt["records"]["aaaa"]["close"] == {
        "source_id": "aaaa",
        "launched": False,
        "closed": True,
    }


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda rows: rows[0]["phases"]["inspect"].update(ok=False), "phase inspect"),
        (lambda rows: rows[0]["phases"].pop("launch"), "phases"),
        (
            lambda rows: rows[0]["phases"]["finish"]["data"].update(clean=False),
            "teardown",
        ),
        (
            lambda rows: rows[0]["phases"]["finish"]["data"].update(
                surviving_objects=99
            ),
            "teardown",
        ),
        (
            lambda rows: rows[0]["phases"]["verify"]["data"].update(new_windows=1),
            "teardown",
        ),
        (
            lambda rows: rows[0]["phases"]["close"].update(path_restored=False),
            "phase close",
        ),
        (
            lambda rows: rows[0]["phases"]["launch"].update(host_seconds=9.0),
            "phase launch",
        ),
        (lambda rows: rows[0].update(reset={"sessions_reset": 1}), "reset"),
        (lambda rows: rows[0].update(status="failed"), "not a clean pass"),
        (
            lambda rows: rows[1]["phases"]["launch"]["data"].update(host_accessed=True),
            "blocked",
        ),
        (
            lambda rows: rows[1]["phases"]["finish"]["data"].update(
                new_file_descriptors=2
            ),
            "teardown",
        ),
    ],
)
def test_validate_when_receipt_tampered_then_refused(world, change, message):
    root, evidence, manifest, _receipt, proposal, commit = world
    rewrite(evidence, change)
    with pytest.raises(StaleProposal, match=message):
        validate(proposal, ports_of(manifest), root, evidence, commit)


def test_validate_when_helper_missing_from_receipt_files_then_refused(world):
    root, evidence, manifest, _receipt, proposal, commit = world
    rewrite(evidence, lambda rows: rows[0]["files"].pop(HELPER))
    proposal["ports"]["aaaa"]["files"].pop(HELPER)
    with pytest.raises(StaleProposal, match="dependency"):
        validate(proposal, ports_of(manifest), root, evidence, commit)


def test_validate_when_shared_helper_changed_after_run_then_stale(world):
    root, evidence, manifest, _receipt, proposal, commit = world
    (root / HELPER).write_text("print('changed')\n")
    with pytest.raises(StaleProposal, match="changed since the native run"):
        validate(proposal, ports_of(manifest), root, evidence, commit)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (
            lambda s, p: (
                s.update(driver_sha256="fabricated"),
                p.update(driver_sha256="fabricated"),
            ),
            "driver",
        ),
        (lambda s, p: s.update(examples_dirty=True), "dirty"),
        (lambda s, p: s.update(revision_unchanged=False), "dirty"),
        (
            lambda s, p: (
                s.update(examples_commit="0" * 40),
                p.update(examples_commit="0" * 40),
            ),
            "commit",
        ),
    ],
)
def test_validate_when_run_identity_forged_then_refused(world, change, message):
    root, evidence, manifest, _receipt, proposal, _commit = world
    path = evidence / "run/final01.summary.json"
    summary = json.loads(path.read_text())
    change(summary, proposal)
    path.write_text(json.dumps(summary))
    target = proposal["examples_commit"]
    with pytest.raises(StaleProposal, match=message):
        validate(proposal, ports_of(manifest), root, evidence, target)


def test_validate_when_commit_argument_differs_from_proposal_then_refused(world):
    root, evidence, manifest, _receipt, proposal, _commit = world
    with pytest.raises(StaleProposal, match="commit"):
        validate(proposal, ports_of(manifest), root, evidence, "f" * 40)


def test_validate_when_receipt_hash_forged_to_match_edit_then_commit_check_refuses(
    world,
):
    root, evidence, manifest, _receipt, proposal, commit = world
    (root / HELPER).write_text("print('edited after the run')\n")
    forged = sha(root / HELPER)
    rewrite(evidence, lambda rows: rows[0]["files"].update({HELPER: forged}))
    proposal["ports"]["aaaa"]["files"][HELPER] = forged
    with pytest.raises(StaleProposal, match="run commit"):
        validate(proposal, ports_of(manifest), root, evidence, commit)


def test_record_when_refused_then_nothing_written(world):
    root, evidence, manifest, receipt, proposal, commit = world
    before = deepcopy(manifest)
    rewrite(evidence, lambda rows: rows[0]["phases"]["inspect"].update(ok=False))
    with pytest.raises(StaleProposal):
        record_native(manifest, receipt, proposal, root, evidence, commit)
    assert manifest == before and receipt == {"records": {}}
