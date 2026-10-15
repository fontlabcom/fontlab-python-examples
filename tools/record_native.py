# SPDX-License-Identifier: Apache-2.0
# this_file: tools/record_native.py
"""Record native acceptance from a proposal, validated against evidence and current files.

A proposal (written next to the native evidence) maps port ids to the receipt
that proves them::

    {"driver_sha256": "...", "ports": {"<id>": {"native_acceptance": "passed",
     "implementation": "implemented", "evidence": "examples-cleanroom/final01.jsonl",
     "files": {"ports/...py": "<sha256>"}}}}

Every entry must match exactly one passing, continue-safe receipt line in its
evidence file; the receipt's file hashes must equal the proposal's and the
current port files (a changed port makes the entry stale), and the batch summary
must name the proposal's driver. Any problem refuses the whole proposal and
writes nothing. Implemented ports become ``passed`` with an exact-projection
record in verification/catalog-native-evidence.json; blocked ports are verified
but stay ``unexecuted`` (the catalogue records native runs of implementations
only). Then ``apply_port_states`` projects the manifest into the catalogue.

Run after tools/integrate_cleanroom.py, which resets native acceptance:

    python tools/record_native.py ../verification/issue-101-ecosystem/evidence/examples-cleanroom/native-acceptance-proposal.json
"""

import argparse
import hashlib
import json
from pathlib import Path

from catalog_output import write_catalog
from catalog_ports import apply_port_states

RECEIPT = "verification/catalog-native-evidence.json"
FORMAT = "native-cleanroom.v1"
POINTERS = {
    # The launch state is the inspect snapshot taken right after launch.
    "launch": "/phases/inspect/data/snapshot",
    "inspect": "/phases/inspect/data/snapshot",
    "close": "/phases/close/data/snapshot",
}
ID_POINTER = "/port_id"  # snapshots may carry a port's own "name" field
HOST_ALIVE_POINTER = "/phases/finish/data/host_alive"


class StaleProposal(ValueError):
    """The proposal does not match its evidence or the current files."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pointer(document, value: str):
    for key in value.lstrip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document


def project(value: dict) -> dict:
    keys = ("source_id", "launched", "closed", "visible", "error")
    return {key: value[key] for key in keys if key in value}


def _evidence_path(evidence_root: Path, name: str) -> Path:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise StaleProposal(f"Nonportable evidence path: {name}")
    return evidence_root / relative


def _receipt_line(path: Path, pid: str) -> tuple[int, dict]:
    matches = [
        (number, json.loads(line))
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if line.strip() and json.loads(line).get("port_id") == pid
    ]
    if len(matches) != 1:
        raise StaleProposal(
            f"{pid}: {len(matches)} receipts in {path.name}, need exactly 1"
        )
    return matches[0]


def validate(
    proposal: dict, ports: dict, root: Path, evidence_root: Path
) -> list[dict]:
    """Checked entries (with their receipt line and record); raises on any problem."""
    checked, problems = [], []
    for pid, entry in sorted(proposal["ports"].items()):
        try:
            row = ports.get(pid)
            if row is None or not row.get("clean_room_receipt"):
                raise StaleProposal(f"{pid}: not a clean-room catalogue record")
            if entry["implementation"] != row["implementation"]:
                raise StaleProposal(f"{pid}: implementation differs from the catalogue")
            if entry["native_acceptance"] != "passed":
                raise StaleProposal(f"{pid}: only passed receipts are recorded")
            path = _evidence_path(evidence_root, entry["evidence"])
            if not path.is_file():
                raise StaleProposal(
                    f"{pid}: evidence file missing: {entry['evidence']}"
                )
            summary = path.with_suffix(".summary.json")
            if (
                not summary.is_file()
                or json.loads(summary.read_text())["driver_sha256"]
                != proposal["driver_sha256"]
            ):
                raise StaleProposal(f"{pid}: evidence summary names another driver")
            line, record = _receipt_line(path, pid)
            if (
                record["status"] != "passed"
                or not record.get("continue_safe")
                or record["implementation"] != row["implementation"]
            ):
                raise StaleProposal(f"{pid}: receipt is not a clean pass")
            if record["files"] != entry["files"] or set(entry["files"]) != set(
                row["replacement_files"]
            ):
                raise StaleProposal(
                    f"{pid}: file list or hashes differ from the receipt"
                )
            for name, digest in entry["files"].items():
                if sha256(root / name) != digest:
                    raise StaleProposal(f"{pid}: {name} changed since the native run")
            if row["implementation"] == "implemented":
                phases = {
                    phase: project(pointer(record, ptr))
                    for phase, ptr in POINTERS.items()
                }
                opened = {
                    "source_id": pid,
                    "launched": True,
                    "closed": False,
                    "visible": True,
                }
                # A port's own snapshot may carry an empty "error" field; any error fails.
                for phase in ("launch", "inspect"):
                    state = dict(phases[phase])
                    if state.pop("error", "") or state != opened:
                        raise StaleProposal(
                            f"{pid}: receipt shows no visible launched window"
                        )
                if phases["close"] != {
                    "source_id": pid,
                    "launched": False,
                    "closed": True,
                }:
                    raise StaleProposal(f"{pid}: receipt shows no clean close")
                if pointer(record, HOST_ALIVE_POINTER) is not True:
                    raise StaleProposal(f"{pid}: host not confirmed alive")
            elif not record["phases"]["launch"]["data"].get("capability_failure"):
                raise StaleProposal(
                    f"{pid}: blocked receipt lacks its capability failure"
                )
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
        except (StaleProposal, KeyError, ValueError) as error:
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
    checked = validate(proposal, ports, root, evidence_root)
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
            "sha256": sha256(item["path"]),
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
            "owned teardown verified clean, host alive (tools/native_cleanroom.py)",
            "catalog_record": "/records/" + pid,
            "source": source,
        }
        counts["passed"] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("proposal", type=Path)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        help="directory the proposal's evidence paths are relative to "
        "(default: ../verification/issue-101-ecosystem/evidence)",
    )
    parser.add_argument(
        "--commit", required=True, help="examples commit the receipts ran"
    )
    args = parser.parse_args()
    root = args.root.resolve()
    evidence_root = (
        args.evidence_root or root.parent / "verification/issue-101-ecosystem/evidence"
    ).resolve()
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
    manifest["source_catalog_sha256"] = sha256(root / "catalog/sources.json")
    (root / "catalog/ports.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (root / RECEIPT).write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
