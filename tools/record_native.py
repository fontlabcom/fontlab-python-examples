# SPDX-License-Identifier: Apache-2.0
# this_file: tools/record_native.py
"""Record native acceptance from native_cleanroom.py receipts, after validating them.

Two steps, from the repository root::

    python tools/record_native.py propose --evidence-root E --output P.json E/run/final*.jsonl
    python tools/record_native.py apply P.json --commit <examples commit of the run>

``propose`` derives the proposal from the receipts (passed ones only); nothing is
written by hand. ``apply`` refuses the whole proposal, writing nothing, unless:

* the run's summary names a clean, unchanged checkout at ``--commit``, which is in
  this checkout's history, and the driver at that commit hashes to the summary's
  driver digest;
* each port has exactly one receipt with all six phases (prepare, launch, inspect,
  close, verify, finish), every envelope ok with sys.path restored and within the
  host budget, no reset or cleanup error, and complete clean teardown (no surviving
  objects, windows, threads, temporary directories or handles; host alive);
  implemented ports show a visible launched window and a clean close, blocked ports
  their capability failure without host access and no new descriptors;
* the receipt's files are exactly the port's current dependency closure
  (native_cleanroom.dependencies), with hashes equal to the files at the run commit
  and to the current files.

Implemented ports then become ``passed`` with exact-projection records in
verification/catalog-native-evidence.json; blocked ports are verified but stay
``unexecuted``. ``apply_port_states`` regenerates the catalogue. Run after
tools/integrate_cleanroom.py, which resets native acceptance.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from catalog_output import write_catalog
from catalog_ports import apply_port_states
from native_cleanroom import HOST_BUDGET, dependencies

RECEIPT = "verification/catalog-native-evidence.json"
DRIVER = "tools/native_cleanroom.py"
FORMAT = "native-cleanroom.v1"
PHASES = ("prepare", "launch", "inspect", "close", "verify", "finish")
POINTERS = {
    # The launch state is the inspect snapshot taken right after launch.
    "launch": "/phases/inspect/data/snapshot",
    "inspect": "/phases/inspect/data/snapshot",
    "close": "/phases/close/data/snapshot",
}
ID_POINTER = "/port_id"  # snapshots may carry a port's own "name" field
HOST_ALIVE_POINTER = "/phases/finish/data/host_alive"
CLEAN = {
    "clean": True,
    "surviving_objects": 0,
    "new_windows": 0,
    "new_threads": [],
    "temporary_directories_remaining": 0,
    "registry_empty": True,
    "host_alive": True,
}


class StaleProposal(ValueError):
    """The proposal does not match its evidence, the run commit or the current files."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pointer(document, value: str):
    for key in value.lstrip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document


def project(value: dict) -> dict:
    keys = ("source_id", "launched", "closed", "visible", "error")
    return {key: value[key] for key in keys if key in value}


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, check=True
    ).stdout


class _Commit:
    """File bytes at the run commit, which must be in this checkout's history."""

    def __init__(self, root: Path, commit: str) -> None:
        self.root, self.commit, self.cache = root, commit, {}
        try:
            _git(root, "cat-file", "-e", commit + "^{commit}")
            _git(root, "merge-base", "--is-ancestor", commit, "HEAD")
        except (OSError, subprocess.CalledProcessError) as error:
            raise StaleProposal(
                f"run commit {commit} is not in this checkout's history"
            ) from error

    def sha(self, name: str) -> str | None:
        if name not in self.cache:
            try:
                self.cache[name] = sha256_bytes(
                    _git(self.root, "show", f"{self.commit}:{name}")
                )
            except subprocess.CalledProcessError:
                self.cache[name] = None
        return self.cache[name]


def _evidence_path(evidence_root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise StaleProposal(f"Nonportable evidence path: {name}")
    return evidence_root / relative


def _receipt_line(path: Path, pid: str) -> tuple[int, dict]:
    rows = [
        (number, json.loads(line))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if line.strip()
    ]
    matches = [(n, r) for n, r in rows if r.get("port_id") == pid]
    if len(matches) != 1:
        raise StaleProposal(
            f"{pid}: {len(matches)} receipts in {path.name}, need exactly 1"
        )
    return matches[0]


def check_receipt(pid: str, record: dict, implemented: bool) -> None:
    """Raise StaleProposal unless the receipt proves a complete, clean native run."""
    if record.get("status") != "passed" or record.get("continue_safe") is not True:
        raise StaleProposal(f"{pid}: receipt is not a clean pass")
    for key in ("error", "cleanup_error", "reset", "reset_error"):
        if record.get(key):
            raise StaleProposal(f"{pid}: receipt has {key}")
    phases = record.get("phases", {})
    if set(phases) != set(PHASES):
        raise StaleProposal(
            f"{pid}: phases {sorted(phases)} are not exactly {list(PHASES)}"
        )
    for name in PHASES:
        phase = phases[name]
        seconds = phase.get("host_seconds")
        if (
            phase.get("ok") is not True
            or phase.get("path_restored") is not True
            or not isinstance(seconds, (int, float))
            or not 0 <= seconds < HOST_BUDGET
            or not isinstance(phase.get("data"), dict)
        ):
            raise StaleProposal(f"{pid}: phase {name} is not a successful envelope")
    for name in ("verify", "finish"):
        data = phases[name]["data"]
        if any(data.get(key) != value for key, value in CLEAN.items()):
            raise StaleProposal(f"{pid}: {name} does not show clean teardown")
        if not implemented and data.get("new_file_descriptors") != 0:
            raise StaleProposal(
                f"{pid}: {name} does not show clean teardown (descriptors)"
            )
    if implemented:
        launch, inspect = phases["launch"]["data"], phases["inspect"]["data"]
        if (
            launch.get("launched") is not True
            or inspect.get("visible") is not True
            or inspect.get("top_level") is not True
        ):
            raise StaleProposal(f"{pid}: receipt shows no visible launched window")
        opened = {"source_id": pid, "launched": True, "closed": False, "visible": True}
        for name in ("launch", "inspect"):
            state = project(pointer(record, POINTERS[name]))
            if state.pop("error", "") or state != opened:
                raise StaleProposal(f"{pid}: receipt shows no visible launched window")
        closed = {"source_id": pid, "launched": False, "closed": True}
        if (
            phases["close"]["data"].get("closed") is not True
            or project(pointer(record, POINTERS["close"])) != closed
        ):
            raise StaleProposal(f"{pid}: receipt shows no clean close")
    else:
        launch = phases["launch"]["data"]
        if (
            not launch.get("capability_failure")
            or launch.get("host_accessed") is not False
        ):
            raise StaleProposal(
                f"{pid}: blocked receipt lacks a host-free capability failure"
            )
        if phases["inspect"]["data"].get("blocked") is not True:
            raise StaleProposal(f"{pid}: blocked receipt not inspected as blocked")


def _check_summary(
    path: Path, proposal: dict, commit: str, driver_sha: str | None
) -> None:
    summary_path = path.with_suffix(".summary.json")
    if not summary_path.is_file():
        raise StaleProposal(f"{path.name}: run summary missing")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("examples_commit") != commit:
        raise StaleProposal(
            f"{path.name}: run commit {summary.get('examples_commit')} is not {commit}"
        )
    if (
        summary.get("examples_dirty") is not False
        or summary.get("revision_unchanged") is not True
    ):
        raise StaleProposal(
            f"{path.name}: the run's checkout was dirty or changed during the run"
        )
    if (
        not driver_sha
        or summary.get("driver_sha256") != driver_sha
        or proposal.get("driver_sha256") != driver_sha
    ):
        raise StaleProposal(
            f"{path.name}: driver digest does not match {DRIVER} at the run commit"
        )


def validate(
    proposal: dict, ports: dict, root: Path, evidence_root: Path, commit: str
) -> list[dict]:
    """Checked entries (with their receipt line and record); raises on any problem."""
    if proposal.get("examples_commit") != commit:
        raise StaleProposal(
            f"proposal commit {proposal.get('examples_commit')} is not --commit {commit}"
        )
    at_commit = _Commit(root, commit)
    driver_sha = at_commit.sha(DRIVER)
    checked, problems, summaries = [], [], {}
    for pid, entry in sorted(proposal["ports"].items()):
        try:
            row = ports.get(pid)
            if row is None or not row.get("clean_room_receipt"):
                raise StaleProposal(f"{pid}: not a clean-room catalogue record")
            if (
                entry["implementation"] != row["implementation"]
                or entry["native_acceptance"] != "passed"
            ):
                raise StaleProposal(
                    f"{pid}: implementation or acceptance differs from the catalogue"
                )
            path = _evidence_path(evidence_root, entry["evidence"])
            if not path.is_file():
                raise StaleProposal(
                    f"{pid}: evidence file missing: {entry['evidence']}"
                )
            if path not in summaries:
                _check_summary(path, proposal, commit, driver_sha)
                summaries[path] = True
            line, record = _receipt_line(path, pid)
            if record.get("implementation") != row["implementation"]:
                raise StaleProposal(
                    f"{pid}: receipt implementation differs from the catalogue"
                )
            check_receipt(pid, record, row["implementation"] == "implemented")
            closure = dependencies(root, row)
            if (
                record.get("files") != entry["files"]
                or sorted(entry["files"]) != closure
            ):
                raise StaleProposal(
                    f"{pid}: receipt files are not the port's dependency closure"
                )
            for name, digest in entry["files"].items():
                if at_commit.sha(name) != digest:
                    raise StaleProposal(f"{pid}: {name} differs from the run commit")
                if sha256_bytes((root / name).read_bytes()) != digest:
                    raise StaleProposal(f"{pid}: {name} changed since the native run")
            checked.append(
                {
                    "pid": pid,
                    "entry": entry,
                    "row": row,
                    "line": line,
                    "record": record,
                    "path": path,
                }
            )
        except (StaleProposal, KeyError, ValueError, OSError) as error:
            problems.append(
                str(error) if isinstance(error, StaleProposal) else f"{pid}: {error!r}"
            )
    if problems:
        raise StaleProposal("Refusing the proposal:\n  " + "\n  ".join(problems))
    return checked


def record_native(
    manifest: dict,
    receipt: dict,
    proposal: dict,
    root: Path,
    evidence_root: Path,
    commit: str,
) -> dict:
    """Apply a validated proposal to the manifest and evidence receipt in place."""
    ports = {row["source_id"]: row for row in manifest["ports"]}
    checked = validate(proposal, ports, root, evidence_root, commit)
    counts = {"passed": 0, "blocked_verified": 0}
    for item in checked:
        row, record = item["row"], item["record"]
        if row["implementation"] != "implemented":
            counts["blocked_verified"] += 1
            continue
        pid = item["pid"]
        source = {
            "root": "ecosystem-evidence",
            "file": item["entry"]["evidence"],
            "sha256": sha256_bytes(item["path"].read_bytes()),
            "line": item["line"],
            "format": FORMAT,
            "id_pointer": ID_POINTER,
            "phase_pointers": dict(POINTERS),
            "host_alive_pointer": HOST_ALIVE_POINTER,
        }
        receipt["records"][pid] = {
            "name": row["name"],
            **{phase: project(pointer(record, ptr)) for phase, ptr in POINTERS.items()},
            "host_alive": True,
            "source": source,
        }
        row["native_acceptance"] = "passed"
        row["native_evidence"] = {
            "implementation_commit": commit,
            "report": RECEIPT,
            "verification": "clean-room native acceptance: launch, inspect, close, "
            "owned teardown verified clean, host alive (tools/native_cleanroom.py); "
            "receipt bound to the port's dependency closure at the run commit",
            "catalog_record": "/records/" + pid,
            "source": source,
        }
        counts["passed"] += 1
    return counts


def propose(runs: list[Path], evidence_root: Path) -> dict:
    """A proposal from receipts: passed receipts only, one run commit and driver."""
    ports, identities = {}, set()
    for run in runs:
        summary = json.loads(
            Path(run).with_suffix(".summary.json").read_text(encoding="utf-8")
        )
        identities.add((summary.get("examples_commit"), summary.get("driver_sha256")))
        relative = (
            Path(run).resolve().relative_to(Path(evidence_root).resolve()).as_posix()
        )
        for line in Path(run).read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record.get("status") == "passed":
                ports[record["port_id"]] = {
                    "native_acceptance": "passed",
                    "implementation": record["implementation"],
                    "evidence": relative,
                    "files": record["files"],
                }
    if len(identities) != 1:
        raise StaleProposal(
            f"runs come from different commits or drivers: {sorted(identities, key=str)}"
        )
    commit, driver = identities.pop()
    return {"examples_commit": commit, "driver_sha256": driver, "ports": ports}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        help="default: ../verification/issue-101-ecosystem/evidence",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("propose", help="write a proposal from run receipts")
    make.add_argument("runs", type=Path, nargs="+")
    make.add_argument("--output", type=Path, required=True)
    apply = sub.add_parser("apply", help="validate a proposal and record it")
    apply.add_argument("proposal", type=Path)
    apply.add_argument("--commit", required=True, help="examples commit of the run")
    args = parser.parse_args()
    root = args.root.resolve()
    evidence_root = (
        args.evidence_root or root.parent / "verification/issue-101-ecosystem/evidence"
    ).resolve()
    if args.command == "propose":
        try:
            proposal = propose(args.runs, evidence_root)
        except StaleProposal as error:
            parser.exit(1, f"{error}\n")
        args.output.write_text(
            json.dumps(proposal, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {"ports": len(proposal["ports"]), "commit": proposal["examples_commit"]}
            )
        )
        return
    manifest = json.loads((root / "catalog/ports.json").read_text(encoding="utf-8"))
    receipt = json.loads((root / RECEIPT).read_text(encoding="utf-8"))
    proposal = json.loads(args.proposal.read_text(encoding="utf-8"))
    try:
        counts = record_native(
            manifest, receipt, proposal, root, evidence_root, args.commit
        )
    except StaleProposal as error:
        parser.exit(1, f"{error}\n")
    catalog = json.loads((root / "catalog/sources.json").read_text(encoding="utf-8"))
    apply_port_states(catalog, manifest)
    write_catalog(catalog, root / "catalog")
    manifest["source_catalog_sha256"] = sha256_bytes(
        (root / "catalog/sources.json").read_bytes()
    )
    (root / "catalog/ports.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (root / RECEIPT).write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
