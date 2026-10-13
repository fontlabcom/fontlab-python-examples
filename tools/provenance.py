# this_file: tools/provenance.py
"""Receipt validation and conservative per-file license evidence."""

import hashlib
import re
from pathlib import Path, PurePosixPath


def relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or str(path) != value:
        raise ValueError("Receipt contains a nonportable relative path")
    return path


def verified_sources(trees: dict, recovery: dict, roots: dict[str, Path]) -> list[dict]:
    """Validate both receipts and every original byte before emitting output."""
    upstream = {r["repository"]: r for r in trees["repositories"]}
    recovered = {r["repository"]: r for r in recovery["repositories"]}
    if len(upstream) != len(trees["repositories"]) or len(recovered) != len(
        recovery["repositories"]
    ):
        raise ValueError("Duplicate repository receipt")
    if set(upstream) != set(recovered) or set(roots) != set(recovered):
        raise ValueError("Source roots and receipt repositories differ")
    output = []
    for repository in sorted(upstream):
        tree, receipt = upstream[repository], recovered[repository]
        if tree["commit"] != receipt["commit"] or tree["tree"].get("truncated", False):
            raise ValueError(f"Revision mismatch or truncated tree: {repository}")
        blobs = {f["path"]: f for f in tree["tree"]["tree"] if f["type"] == "blob"}
        files = receipt["files"]
        if (
            set(blobs) != set(files)
            or len(files) != tree["file_count"]
            or len(files) != receipt["files_verified"]
        ):
            raise ValueError(f"File accounting mismatch: {repository}")
        if sum(p.endswith(".py") for p in files) != tree["python_file_count"]:
            raise ValueError(f"Python accounting mismatch: {repository}")
        root = roots[repository].resolve()
        storage_paths = {str(relative_path(f["storage_path"])) for f in files.values()}
        if len(storage_paths) != len(files):
            raise ValueError(f"Duplicate storage mapping: {repository}")
        actual = {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and p.name != ".DS_Store"
        }
        if actual != storage_paths:
            raise ValueError(f"Source directory accounting mismatch: {repository}")
        data = {}
        for logical in sorted(files):
            relative_path(logical)
            record, blob = files[logical], blobs[logical]
            stored = root / record["storage_path"]
            if not stored.resolve().is_relative_to(root) or stored.is_symlink():
                raise ValueError(f"Source storage escapes root: {repository}:{logical}")
            content = stored.read_bytes()
            git_hash = hashlib.sha1(
                b"blob " + str(len(content)).encode() + b"\0" + content
            ).hexdigest()
            if (
                len(content) != record["bytes"]
                or len(content) != blob["size"]
                or hashlib.sha256(content).hexdigest() != record["sha256"]
                or git_hash != record["git_blob_sha"]
                or git_hash != blob["sha"]
            ):
                raise ValueError(f"Source/hash mismatch: {repository}:{logical}")
            data[logical] = content
        output.append(
            {
                "repository": repository,
                "commit": tree["commit"],
                "files": files,
                "blobs": blobs,
                "data": data,
                "archive_sha256": receipt.get("archive_sha256"),
            }
        )
    denominator = recovery["denominator"]
    if (
        len(output) != denominator["repositories"]
        or sum(len(r["files"]) for r in output) != denominator["source_files"]
    ):
        raise ValueError("Recovery denominator mismatch")
    return output


def license_document(path: str) -> bool:
    name = PurePosixPath(path).name.lower()
    return (
        name == "copying"
        or name == "notice"
        or name == "license"
        or name.startswith(("license.", "copying.", "notice."))
        or "-license." in name
    )


def declared_terms(text: str) -> list[str]:
    """Report recognizable declarations without assigning a legal conclusion."""
    terms = set(re.findall(r"SPDX-License-Identifier:\s*([^\n]+)", text))
    low = text.lower()
    for name, phrase in {
        "GPL-3.0 (version declaration; or-later scope requires review)": "version 3, 29 june 2007",
        "GPL (file header; version/options require review)": "gnu general public license",
        "MIT": "permission is hereby granted, free of charge",
        "Apache-2.0": "apache license, version 2.0",
        "OFL-1.1": "sil open font license version 1.1",
        "OFL (version requires review)": "license:   sil",
        "BSD-3-Clause": "neither the name of the copyright holder",
        "public-domain declaration": "released into the public domain",
    }.items():
        if phrase in low:
            terms.add(name)
    return sorted(terms)


def license_evidence(repository: str, path: str, texts: dict[str, str]) -> dict:
    p = PurePosixPath(path)
    relevant = sorted(
        n for n in texts if license_document(n) and PurePosixPath(n).parent in p.parents
    )
    readmes = sorted(
        n
        for n in texts
        if PurePosixPath(n).name.lower().startswith("readme")
        and PurePosixPath(n).parent in p.parents
    )
    own = texts[path]
    terms = declared_terms(own[:20000]) if own else []
    evidence = [{"path": path, "scope": "file-header", "terms": terms}] if terms else []
    for n in relevant:
        evidence.append(
            {
                "path": n,
                "scope": "nearby notice; applicability requires review",
                "terms": declared_terms(texts[n]),
            }
        )
    # These scoped declarations were read in the pinned upstream README.
    readme = texts.get("README.md", "")
    if repository == "pyqt/examples" and "MIT or GPLv3" in readme:
        if re.match(r"src/(?:0[1-9]|1[0-5]) ", path) and p.suffix == ".py":
            evidence.append(
                {
                    "path": "README.md",
                    "scope": "numbered example source, except where indicated",
                    "terms": ["MIT OR GPL-3.0"],
                }
            )
        elif path.startswith("src/screenshots/"):
            evidence.append(
                {
                    "path": "README.md",
                    "scope": "screenshots; book attribution condition",
                    "terms": ["CC-BY-NC-SA-4.0"],
                }
            )
    attribution = [
        {"path": path, "line": i, "notice": line.strip()}
        for i, line in enumerate(own.splitlines(), 1)
        if re.search(r"\bcopyright\b", line, re.IGNORECASE) and len(line) < 500
    ]
    return {
        "review_state": "pending",
        "declared_terms": sorted({t for e in evidence for t in e["terms"]})
        or ["unknown"],
        "evidence": evidence,
        "readme_paths": readmes,
        "attribution_notices": attribution,
        "redistribution_state": "originals-local-only; per-file review pending",
    }
