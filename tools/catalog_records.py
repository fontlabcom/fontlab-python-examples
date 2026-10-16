# this_file: tools/catalog_records.py
"""Preserve one portable record per exact upstream file."""

import hashlib
import posixpath
import re
from pathlib import PurePosixPath
from urllib.parse import quote

from provenance import license_document, license_evidence
from resource_analysis import capabilities, resource_analysis
from source_analysis import python_analysis, source_text


def identity(repository: str, path: str) -> str:
    return hashlib.sha256((repository + ":" + path).encode()).hexdigest()[:16]


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "root"


def category(path: str, needs: list[str]) -> str:
    for name in [
        "gstreamer",
        "matplotlib",
        "video-overlay",
        "webengine",
        "qml",
        "multimedia",
        "database",
        "network",
        "platform",
        "graphics-painting",
        "designer-ui",
        "threads-processes",
    ]:
        if name in needs:
            return name
    parts = PurePosixPath(path).parts
    if "pyqt-official" in parts:
        index = parts.index("pyqt-official") + 1
        return slug(parts[index]) if index < len(parts) else "metadata"
    if parts[0] == "official" and len(parts) > 1:
        return slug(parts[1])
    return "widgets" if path.endswith(".py") else "resources-metadata"


def source_records(source: dict) -> list[dict]:
    repository, revision = source["repository"], source["commit"]
    texts = {p: source_text(p, b) for p, b in source["data"].items()}
    records = []
    for path in sorted(texts):
        text = texts[path]
        python = python_analysis(text, path) if path.endswith(".py") else None
        needs = capabilities(path, text, python or {})
        record = {
            "id": identity(repository, path),
            "repository": repository,
            "commit": revision,
            "path": path,
            "bytes": source["files"][path]["bytes"],
            "sha256": source["files"][path]["sha256"],
            "git_blob_sha": source["files"][path]["git_blob_sha"],
            "git_mode": source["blobs"][path]["mode"],
            "upstream_url": f"https://github.com/{repository}/blob/{revision}/{quote(path, safe='/')}",
            "category": category(path, needs),
            "capability_needs": needs,
            "license": license_evidence(repository, path, texts),
            "port_state": "pending",
            "runtime_state": "unexecuted",
        }
        if python:
            record["python"] = python
        record.update(resource_analysis(path, text))
        suffix = PurePosixPath(path).suffix
        record["kind"] = (
            "python"
            if python
            else "license"
            if license_document(path)
            else "qml"
            if suffix == ".qml"
            else "ui"
            if suffix == ".ui"
            else "qrc"
            if suffix == ".qrc"
            else "dependency"
            if PurePosixPath(path).name
            in {"requirements.txt", "pyproject.toml", "setup.py", "Pipfile"}
            else "documentation"
            if suffix in {".md", ".rst"}
            else "asset-or-configuration"
        )
        if PurePosixPath(path).name == "requirements.txt":
            record["dependency_declarations"] = sorted(
                set(
                    re.findall(
                        r"(?m)^\s*([A-Za-z0-9][A-Za-z0-9_.-]*(?:\[[^\]\n]+\])?[^#\n]*)",
                        text,
                    )
                )
            )
        target_name = (
            slug(PurePosixPath(path).stem) + "-" + record["id"] + suffix.lower()
        )
        record["target_path"] = (
            f"ports/{record['category']}/{slug(repository)}/{target_name}"
        )
        records.append(record)
    # Resolve local imports by logical spelling, never filesystem case folding.
    by_path = {r["path"]: r for r in records}
    for record in records:
        references = record.get("xml", record.get("qml", {})).get("references", [])
        record["resource_reference_resolutions"] = []
        for reference in references:
            relative = posixpath.normpath(
                str(PurePosixPath(record["path"]).parent / reference)
            )
            target = by_path.get(relative)
            record["resource_reference_resolutions"].append(
                {
                    "reference": reference,
                    "logical_path": relative,
                    "original_file_id": target["id"] if target else None,
                    "state": "resolved"
                    if target
                    else "unresolved; inspect runtime/resource URL semantics",
                }
            )
        if "python" not in record:
            continue
        associations = set()
        for module in (
            record["python"]["imports"] + record["python"]["local_import_names"]
        ):
            module_path = module.lstrip(".").replace(".", "/")
            for prefix in [str(PurePosixPath(record["path"]).parent), "."]:
                for tail in [module_path + ".py", module_path + "/__init__.py"]:
                    candidate = str(PurePosixPath(prefix) / tail)
                    if candidate in by_path and candidate != record["path"]:
                        associations.add(by_path[candidate]["id"])
                        helper = by_path[candidate].get("python")
                        if (
                            helper
                            and helper["role"] == "ambiguous"
                            and helper["parse"]["state"] == "parsed"
                        ):
                            helper["role"] = "auxiliary"
        record["python"]["local_module_ids"] = sorted(associations)
    return records
