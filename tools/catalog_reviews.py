# this_file: tools/catalog_reviews.py
"""Apply explicit, hash-bound source reviews after static analysis."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SOURCE_FIELDS = ("path", "repository", "sha256", "upstream_url")
HEX64 = re.compile(r"[0-9a-f]{64}")


def _pointer(document, value: str):
    for key in value.lstrip("/").split("/"):
        key = key.replace("~1", "/").replace("~0", "~")
        document = document[int(key)] if isinstance(document, list) else document[key]
    return document


def check_citation(
    item: dict, files: dict, evidence_root: Path | None, cache: dict
) -> None:
    """Raise ValueError unless a review citation names a real, matching source or record.

    Source citations must equal the catalogue's own record for that id (path,
    repository, hash, URL; optional one-based line range). Evidence citations need a
    portable path, a hash and a JSON pointer; with ``evidence_root`` the file must
    exist with that hash and the pointer must resolve.
    """
    if "source_id" in item:
        record = files.get(item["source_id"])
        if record is None:
            raise ValueError(f"Review cites an unknown source: {item['source_id']}")
        if any(item.get(field) != record.get(field) for field in SOURCE_FIELDS):
            raise ValueError(
                f"Review citation does not match source {item['source_id']}"
            )
        lines = item.get("lines")
        if lines is not None and not (
            isinstance(lines, list)
            and len(lines) == 2
            and all(isinstance(n, int) for n in lines)
            and 1 <= lines[0] <= lines[1]
        ):
            raise ValueError(f"Review citation has an invalid line range: {lines}")
        return
    if item.get("root") != "ecosystem-evidence":
        raise ValueError(f"Review citation has an unknown kind: {sorted(item)}")
    relative = Path(item.get("file", ""))
    if not item.get("file") or relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Review evidence path is not portable: {item.get('file')}")
    if not HEX64.fullmatch(str(item.get("sha256", ""))) or not str(
        item.get("pointer", "")
    ).startswith("/"):
        raise ValueError(
            f"Review evidence needs a sha256 and a JSON pointer: {item['file']}"
        )
    if evidence_root is None:
        return
    path = evidence_root / relative
    if not path.is_file():
        raise ValueError(f"Review evidence file is missing: {item['file']}")
    if path not in cache:
        data = path.read_bytes()
        cache[path] = (hashlib.sha256(data).hexdigest(), json.loads(data))
    digest, document = cache[path]
    if digest != item["sha256"]:
        raise ValueError(f"Review evidence hash differs: {item['file']}")
    try:
        _pointer(document, item["pointer"])
    except (KeyError, IndexError, ValueError, TypeError) as error:
        raise ValueError(
            f"Review evidence pointer does not resolve: {item['pointer']}"
        ) from error


def apply_reviews(
    catalog: dict, reviews: dict, evidence_root: Path | None = None
) -> None:
    """Keep static observations and identities while applying reviewed decisions.

    Every citation is checked (``check_citation``) before any record changes.
    """
    files = {row["id"]: row for row in catalog["files"]}
    examples = {row["id"]: row for row in catalog["examples"]}
    cache: dict = {}
    for section in ["classifications", "ownership"]:
        for source_id, review in reviews[section].items():
            if (
                review.get("state") != "reviewed"
                or not review.get("reason")
                or not review.get("evidence")
            ):
                raise ValueError(f"Review needs reasoning and evidence: {source_id}")
            for item in review["evidence"]:
                check_citation(item, files, evidence_root, cache)
    for source_id, review in reviews["classifications"].items():
        file, example = files[source_id], examples[source_id]
        if file["sha256"] != review["source_sha256"]:
            raise ValueError(f"Classification review hash mismatch: {source_id}")
        example.setdefault("static_classification", example["classification"])
        example["classification"] = review["classification"]
        example["ambiguity"] = None
        example["classification_review"] = review
        file["classification_review"] = review
        if "python" in file:
            file["python"].setdefault("static_role", file["python"]["role"])
            file["python"]["role"] = review["classification"]
        for owner in review["owner_example_ids"]:
            _associate(file, examples[owner])
    for source_id, review in reviews["ownership"].items():
        file = files[source_id]
        if file["sha256"] != review["source_sha256"]:
            raise ValueError(f"Ownership review hash mismatch: {source_id}")
        file["ownership_review"] = review
        file["association_state"] = "reviewed " + review["scope"] + " ownership"
        for owner in review["owner_example_ids"]:
            _associate(file, examples[owner])
    catalog["counts"].setdefault(
        "static_ambiguous_candidates", catalog["counts"]["ambiguous_candidates"]
    )
    catalog["counts"]["ambiguous_candidates"] = sum(
        row["classification"] == "ambiguous" for row in catalog["examples"]
    )
    catalog["counts"].setdefault(
        "static_auxiliary_python_files", catalog["counts"]["auxiliary_python_files"]
    )
    catalog["counts"]["auxiliary_python_files"] = sum(
        row.get("python", {}).get("role") == "auxiliary" for row in catalog["files"]
    )
    catalog["counts"]["reviewed_classifications"] = dict(
        sorted(Counter(row["classification"] for row in catalog["examples"]).items())
    )
    catalog["counts"]["shared_files_reviewed"] = len(reviews["ownership"])
    catalog["review_decisions"] = "catalog/reviews.json"
    if (
        "hash-bound classification/ownership reviews applied"
        not in catalog["analysis_semantics"]
    ):
        catalog["analysis_semantics"] += (
            "; hash-bound classification/ownership reviews applied; runtime remains separate"
        )


def _associate(file: dict, example: dict) -> None:
    """Record both directions without asserting that directory assets are loaded."""
    file["example_ids"] = sorted(set(file["example_ids"]) | {example["id"]})
    example["original_file_ids"] = sorted(
        set(example["original_file_ids"]) | {file["id"]}
    )
    if file["kind"] != "python":
        example["ui_qml_qrc_asset_ids"] = sorted(
            set(example["ui_qml_qrc_asset_ids"]) | {file["id"]}
        )
