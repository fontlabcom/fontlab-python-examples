# SPDX-License-Identifier: Apache-2.0
# this_file: tools/sync_samples.py
"""Copy the FontLab 9 Samples GUI scripts into examples/samples/ and write its README.

The scripts are maintained in the fontlab-samples workspace repository and deployed
to FontLab's ``Scripts/Samples`` folder. This tool copies every ``*.py`` from that
folder byte for byte (``.pyc`` and other files are ignored), removes copies whose
source is gone, and regenerates ``examples/samples/README.md`` from each script's
``#FLM: Category · Title`` line and docstring summary. From the repository root::

    python3 tools/sync_samples.py                   # copy from FontLab's Scripts/Samples
    python3 tools/sync_samples.py --source DIR      # copy from another folder
    python3 tools/sync_samples.py --check           # exit 1 if README.md is stale
"""

import argparse
import ast
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "examples/samples"
SOURCE = Path.home() / "Library/Application Support/FontLab/FontLab 9/Scripts/Samples"
INTRO = """\
---
this_file: examples/samples/README.md
---

# Samples: GUI scripts for FontLab 9

{count} single-file PythonQt dialogs for everyday font work: anchors, metrics,
kerning, outlines, masters, names, guides, font info, features, hinting, cleanup,
generators, reports and proofs. Each one works on the current font and offers a master
scope where that makes sense; most list what an Apply will change before you press it,
and a few (such as mark-colour swatches) apply on click. Report, browser and proof
scripts change no font data (some select glyphs, copy to the clipboard or export files).
Many glyph-editing tools group their edits into one Undo step, but Undo coverage varies.
Seven metrics scripts warn that moved stem hints are not restored, and font-wide data
(font info, OpenType features, master settings) is written directly: Italic Angle
(Masters) states that Undo does not restore its change. Read each script's notes before
applying changes.

Copy any file into FontLab's `Scripts` folder (for example `Scripts/Samples`) and run
it from the **Scripts** menu, or open it in the Scripting panel. A script needs only
FontLab 9 and its bundled PythonQt; nothing else is installed. Dialogs are modeless,
so the Font window stays usable, and every dialog disconnects its signals when closed.

Each script was run in FontLab 9.0.9783 through its menu path on disposable copies of
GetGo fonts, with screenshots and before/after reads of the changed glyphs. Edits on
glyphs used by automatic composites warn first: FontLab may rebuild those composites'
anchors and locks, and Undo does not restore that rebuild.
"""


def describe(path: Path) -> tuple[str, str, str]:
    """(category, title, summary) from the #FLM line and the module docstring."""
    text = path.read_text(encoding="utf-8")
    first = text.splitlines()[0]
    if not first.startswith("#FLM: ") or " · " not in first:
        raise ValueError(f"{path.name}: first line must be '#FLM: Category · Title'")
    category, title = (part.strip() for part in first[6:].split(" · ", 1))
    doc = ast.get_docstring(ast.parse(text)) or ""
    summary = " ".join(doc.split("\n\n")[0].split())
    if not summary:
        raise ValueError(f"{path.name}: module docstring missing")
    return category, title, summary


def readme(folder: Path) -> str:
    scripts = sorted(folder.glob("*.py"))
    groups: dict[str, list[str]] = {}
    for path in scripts:
        category, title, summary = describe(path)
        cell = summary.replace("|", "\\|")
        groups.setdefault(category, []).append(f"| [{title}]({path.name}) | {cell} |")
    lines = [INTRO.format(count=len(scripts))]
    for category in sorted(groups):
        rows = sorted(groups[category], key=str.casefold)
        lines += [f"## {category} ({len(rows)})", "", "| Script | What it does |", "| --- | --- |", *rows, ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def copy(source: Path, target: Path) -> int:
    names = {p.name for p in source.glob("*.py")}
    if source.resolve() == target.resolve():
        return len(names)
    if not names:
        raise SystemExit(f"no *.py scripts in {source}")
    target.mkdir(parents=True, exist_ok=True)
    for stale in target.glob("*.py"):
        if stale.name not in names:
            stale.unlink()
    for name in sorted(names):
        shutil.copyfile(source / name, target / name)
    return len(names)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--check", action="store_true", help="only verify README.md")
    args = parser.parse_args()
    if not args.check:
        print(f"copied {copy(args.source, TARGET)} scripts from {args.source}")
        (TARGET / "README.md").write_text(readme(TARGET), encoding="utf-8")
        return 0
    if (TARGET / "README.md").read_text(encoding="utf-8") != readme(TARGET):
        print("examples/samples/README.md is stale: run tools/sync_samples.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
