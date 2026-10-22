# this_file: src_docs/build.py
"""Build the examples site and a verified export of the retained catalogue."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from src_docs.current_menus import catalogue

ROOT = Path(__file__).resolve().parents[1]
NOTICE = (
    '!!! note "Retained catalogue"\n\n'
    "    This page comes from the retained catalogue. Its launch instructions and native\n"
    "    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current\n"
    "    launcher. The documentation build does not rerun these examples.\n\n"
)


def export(root: Path) -> None:
    """Read a verified retained manifest; never execute retained source code.

    FONTLAB_RETAINED_EXPORT selects an explicitly reviewed checkpoint. Otherwise
    use the retained static export. Refuse stale/unsafe inputs before replacing
    any accepted output. A build does not refresh or bless mismatched hashes.
    """
    source = Path(
        os.environ.get("FONTLAB_RETAINED_EXPORT") or root / "src_docs/retained-export"
    )
    manifest = json.loads((source / "manifest.json").read_text())
    if manifest.get("format") != "fontlab-python-examples.docs-export.v1":
        raise ValueError("Unsupported retained export format")
    pages, seen = [], set()
    for row in manifest["pages"]:
        relative = Path(row["path"])
        target = source / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or relative.suffix != ".md"
            or "\\" in row["path"]
            or not target.resolve().is_relative_to(source.resolve())
        ):
            raise ValueError("Unsafe retained export path")
        if row["path"] in seen:
            raise ValueError("Duplicate retained export page")
        seen.add(row["path"])
        data = target.read_bytes()
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError(
                "Retained catalogue differs from its manifest: " + row["path"]
            )
        title, _, body = data.decode().partition("\n")
        if NOTICE not in body:
            data = (title + "\n\n" + NOTICE + body.lstrip("\n")).encode()
        pages.append((relative, data))
        row["sha256"] = hashlib.sha256(data).hexdigest()
    output = root / ".build/export"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for relative, data in pages:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest["generator"] = "src_docs/build.py (verified retained checkpoint)"
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--offline", action="store_true", help="use cached dependencies"
    )
    parser.add_argument(
        "--serve", action="store_true", help="preview locally with Markdown editing"
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="prepare API-site inputs without rendering",
    )
    args = parser.parse_args()
    export(ROOT)
    catalogue(ROOT)
    if not args.export_only:
        command = [
            "properdocs",
            "serve" if args.serve else "build",
            "--strict",
            "-f",
            "src_docs/mkdocs.yml",
        ]
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
