# this_file: tools/catalog_reviews.py
"""Apply explicit, hash-bound source reviews after static analysis."""

from collections import Counter


def apply_reviews(catalog: dict, reviews: dict) -> None:
    """Keep static observations and identities while applying reviewed decisions."""
    files = {row["id"]: row for row in catalog["files"]}
    examples = {row["id"]: row for row in catalog["examples"]}
    for section in ["classifications", "ownership"]:
        for source_id, review in reviews[section].items():
            if (
                review.get("state") != "reviewed"
                or not review.get("reason")
                or not review.get("evidence")
            ):
                raise ValueError(f"Review needs reasoning and evidence: {source_id}")
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
