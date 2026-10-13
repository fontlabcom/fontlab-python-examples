#!/usr/bin/env python3
# this_file: tools/inventory.py
"""Generate a portable complete source catalog; no upstream code is executed."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from catalog_examples import example_records
from catalog_output import write_catalog
from catalog_records import source_records
from provenance import verified_sources


def build_catalog(trees: dict, recovery: dict, roots: dict[str, Path]) -> dict:
    sources = verified_sources(trees, recovery, roots)
    files = [record for source in sources for record in source_records(source)]
    examples = example_records(files)
    for file in files:
        file["example_ids"] = sorted(
            e["id"] for e in examples if file["id"] in e["original_file_ids"]
        )
        file["association_state"] = (
            "directory-associated; review runtime references"
            if file["example_ids"]
            else "shared-or-repository-file; ownership unresolved"
        )
    duplicates = defaultdict(list)
    for file in files:
        duplicates[file["sha256"]].append(file["id"])
    return {
        "this_file": "catalog/sources.json",
        "schema_version": "fontlab.examples-catalog.v1",
        "analysis_semantics": "static source evidence only; candidates and directory associations require review; all ports pending/native unexecuted",
        "sources": [
            {
                "repository": s["repository"],
                "commit": s["commit"],
                "archive_sha256": s["archive_sha256"],
                "source_files": len(s["files"]),
                "python_files": sum(p.endswith(".py") for p in s["files"]),
            }
            for s in sources
        ],
        "counts": {
            "source_files": len(files),
            "python_files": sum("python" in f for f in files),
            "entrypoint_candidates": sum(
                e["classification"] == "entrypoint" for e in examples
            ),
            "ambiguous_candidates": sum(
                e["classification"] == "ambiguous" for e in examples
            ),
            "auxiliary_python_files": sum(
                f.get("python", {}).get("role") == "auxiliary" for f in files
            ),
            "examples_ported": 0,
            "examples_native_executed": 0,
            "python_parse_states": dict(
                sorted(
                    Counter(
                        f["python"]["parse"]["state"] for f in files if "python" in f
                    ).items()
                )
            ),
            "file_categories": dict(
                sorted(Counter(f["category"] for f in files).items())
            ),
        },
        "files": files,
        "examples": examples,
        "byte_duplicate_groups": [
            {"sha256": sha, "original_file_ids": sorted(ids)}
            for sha, ids in sorted(duplicates.items())
            if len(ids) > 1
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree-receipt", required=True, type=Path)
    parser.add_argument("--recovery-receipt", required=True, type=Path)
    parser.add_argument(
        "--source-root", action="append", required=True, metavar="REPOSITORY=PATH"
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    roots = {}
    for value in args.source_root:
        repository, separator, path = value.partition("=")
        if not separator or not repository or not path or repository in roots:
            parser.error("Source roots must be unique REPOSITORY=PATH values")
        roots[repository] = Path(path)
    try:
        catalog = build_catalog(
            json.loads(args.tree_receipt.read_text()),
            json.loads(args.recovery_receipt.read_text()),
            roots,
        )
    except (ValueError, KeyError, OSError) as error:
        # OSError text may expose private absolute paths; keep CLI diagnostics portable.
        parser.exit(
            1,
            f"Inventory failed: {str(error) if isinstance(error, ValueError) else type(error).__name__}\n",
        )
    write_catalog(catalog, args.output)
    print(json.dumps(catalog["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
