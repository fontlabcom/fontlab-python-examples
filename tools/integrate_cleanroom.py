# SPDX-License-Identifier: Apache-2.0
# this_file: tools/integrate_cleanroom.py
"""Merge independent receipts using only public metadata and replacement files."""

import argparse
import hashlib
import json
from copy import deepcopy
from pathlib import Path

from catalog_output import write_catalog
from catalog_ports import apply_port_states


def checked_path(root: Path, name: str) -> Path:
    """Reject absolute paths, traversal and symlinks leaving the checkout."""
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Nonportable receipt path: {name}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Receipt path escapes checkout: {name}")
    return path


def read_receipts(root: Path) -> dict[str, dict]:
    """Require exact spec coverage and bind every decision to its specification."""
    index = json.loads((root / "clean-room-specs/INDEX.json").read_text())["ports"]
    specs = {row["port_id"]: row for row in index}
    if len(specs) != len(index):
        raise ValueError("Duplicate specification identity")
    receipts = {}
    for path in sorted((root / "clean-room/receipts").glob("*.json")):
        receipt = json.loads(path.read_text())
        pid = receipt["port_id"]
        if pid not in specs or pid in receipts or path.stem != pid:
            raise ValueError(f"Unknown, duplicate or misnamed receipt: {path.name}")
        spec = specs[pid]
        digest = hashlib.sha256(
            checked_path(root, spec["spec_file"]).read_bytes()
        ).hexdigest()
        if receipt["spec_sha256"] != digest:
            raise ValueError(f"Specification hash mismatch: {pid}")
        if receipt["target_path"] != spec["target_path"]:
            raise ValueError(f"Receipt target mismatch: {pid}")
        state = receipt["implementation"]
        if state not in {"implemented", "blocked"}:
            raise ValueError(f"Invalid implementation state: {pid}")
        reason = receipt["blocked_reason"]
        if (
            state == "blocked" and (not isinstance(reason, str) or not reason.strip())
        ) or (state == "implemented" and reason is not None):
            raise ValueError(f"Invalid blocked reason: {pid}")
        files = receipt["files"]
        if (
            not files
            or len(set(files)) != len(files)
            or spec["target_path"] not in files
        ):
            raise ValueError(f"Incomplete file list: {pid}")
        for name in files:
            if not name.startswith("ports/") or not checked_path(root, name).is_file():
                raise ValueError(f"Missing replacement file: {name}")
            if name.endswith(".py") and not checked_path(
                root, name
            ).read_text().startswith(
                "# SPDX-License-Identifier: Apache-2.0\n# Clean-room implementation from "
                + spec["spec_file"]
            ):
                raise ValueError(f"Replacement header mismatch: {name}")
        receipts[pid] = receipt
    if set(receipts) != set(specs):
        raise ValueError("Receipt coverage differs from the specification index")
    return receipts


def merge_receipts(manifest: dict, receipts: dict[str, dict]) -> dict:
    """Keep original source/resource provenance separate from replacement grants."""
    result = deepcopy(manifest)
    ports = {row["source_id"]: row for row in result["ports"]}
    pending = {
        pid
        for pid, row in ports.items()
        if row["implementation"] == "clean_room_pending"
    }
    if pending - receipts.keys() or receipts.keys() - ports.keys():
        raise ValueError("Receipts do not cover the pending catalogue records")
    for pid, receipt in receipts.items():
        row = ports[pid]
        if (
            row["target_path"] != receipt["target_path"]
            or row.get("spec") != f"clean-room-specs/{pid}.md"
        ):
            raise ValueError(f"Catalogue/spec target mismatch: {pid}")
        if row["implementation"] != "clean_room_pending" and not row.get(
            "clean_room_receipt"
        ):
            raise ValueError(f"Refusing to replace a non-clean-room record: {pid}")
        row.update(
            implementation=receipt["implementation"],
            native_acceptance="unexecuted",
            clean_room_receipt=f"clean-room/receipts/{pid}.json",
            replacement_files=list(receipt["files"]),
            license={
                "selected": "Apache-2.0",
                "review_state": "reviewed",
                "basis": f"clean-room implementation from clean-room-specs/{pid}.md; no upstream code",
                "spec_sha256": receipt["spec_sha256"],
            },
        )
        row.pop("native_evidence", None)
        row.pop("blocked_reason", None)
        if receipt["implementation"] == "blocked":
            row["blocked_reason"] = receipt["blocked_reason"]
    return result


def integrate(root: Path) -> dict:
    """Project into the existing inventory without opening any original source."""
    receipts = read_receipts(root)
    manifest = merge_receipts(
        json.loads((root / "catalog/ports.json").read_text()), receipts
    )
    catalog = json.loads((root / "catalog/sources.json").read_text())
    apply_port_states(catalog, manifest)
    write_catalog(catalog, root / "catalog")
    manifest["source_catalog_sha256"] = hashlib.sha256(
        (root / "catalog/sources.json").read_bytes()
    ).hexdigest()
    (root / "catalog/ports.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    return catalog["counts"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args()
    print(json.dumps(integrate(args.root.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
