#!/usr/bin/env python3
# this_file: tools/collect_pythonqt_reference.py
"""Copy third-party Python files that use PythonQt into _reference/ with provenance.

Each source checkout keeps its relative folder structure under
_reference/<source-name>/. The manifest records repository URL, commit, file
hashes and detected licence files so the copies stay traceable; it does not
grant redistribution rights.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

PATTERN = re.compile(rb"\bPythonQt\b")
# Slicer/CTK/MeVisLab expose PythonQt as a top-level ``qt`` module.
QT_MODULE = re.compile(rb"^\s*(?:import qt\b|from qt import\b)", re.MULTILINE)
LICENSE_NAMES = re.compile(r"^(licen[cs]e|copying|notice)(\.|$)", re.IGNORECASE)
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def _git(root: Path, *args: str) -> str | None:
    """Return trimmed git output, or None when the folder is not a checkout."""
    result = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def _python_files(root: Path) -> list[Path]:
    """List regular .py files, skipping VCS/cache folders and symlinks."""
    found = []
    for path in root.rglob("*.py"):
        if path.is_symlink() or not path.is_file():
            continue
        if SKIP_DIRS.intersection(path.relative_to(root).parts):
            continue
        found.append(path)
    return sorted(found)


def collect(name: str, root: Path, output: Path) -> dict:
    """Copy matching files for one source and return its manifest record."""
    scanned = _python_files(root)
    files = []
    for path in scanned:
        data = path.read_bytes()
        rules = [n for n, rx in (("PythonQt", PATTERN), ("qt-module", QT_MODULE)) if rx.search(data)]
        if not rules:
            continue
        relative = path.relative_to(root)
        target = output / name / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        files.append(
            {
                "path": relative.as_posix(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "pythonqt_mentions": len(PATTERN.findall(data)),
                "rules": rules,
            }
        )
    licenses = sorted(
        p.name for p in root.iterdir() if p.is_file() and LICENSE_NAMES.match(p.name)
    )
    return {
        "name": name,
        "url": _git(root, "remote", "get-url", "origin"),
        "commit": _git(root, "rev-parse", "HEAD"),
        "license_files": licenses,
        "python_files_scanned": len(scanned),
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append", default=[], metavar="NAME=DIR")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    records = []
    for spec in args.source:
        name, _, directory = spec.partition("=")
        root = Path(directory)
        if not root.is_dir():
            records.append({"name": name, "error": "source folder missing"})
            continue
        records.append(collect(name, root, args.output))
    summary = {
        "schema_version": 1,
        "patterns": [PATTERN.pattern.decode(), QT_MODULE.pattern.decode()],
        "sources": records,
        "total_files": sum(len(r.get("files", [])) for r in records),
    }
    args.manifest.write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n")
    print(f"{summary['total_files']} files from {len(records)} sources")


if __name__ == "__main__":
    main()
