# this_file: src_docs/current_menus.py
"""Document all current menu source; never import or execute a menu."""

import ast
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def catalogue(root: Path, *, revision: str | None = None) -> None:
    """Retain every menu description, exact source hash and immutable source link."""
    if revision is None:
        revision = subprocess.check_output(
            ["git", "log", "-1", "--format=%H", "--", "Scripts"], cwd=root, text=True
        ).strip()
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("A complete source commit is required")
    output = root / "src_docs/md/current"
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    snapshots = root / ".build/menu-sources"
    if snapshots.exists():
        shutil.rmtree(snapshots)
    snapshots.mkdir(parents=True)
    index = [
        "# Current menu sources",
        "",
        "Choose a category, then a script. Each page retains its usage and exact source identity.",
        "",
    ]
    for folder in sorted((root / "Scripts").iterdir()):
        if not folder.is_dir():
            continue
        sources = sorted(folder.glob("*.py"))
        if not sources:
            continue
        category = output / slug(folder.name)
        category.mkdir()
        lines = [f"# {folder.name}", ""]
        index.append(f"## {folder.name}")
        index.append("")
        for source in sources:
            target = category / (slug(source.stem) + ".md")
            if target.exists():
                raise ValueError(f"Duplicate documentation slug: {source.name}")
            data = source.read_bytes()
            snapshot = snapshots / (hashlib.sha256(data).hexdigest() + ".py")
            snapshot.write_bytes(data)
            description = (
                ast.get_docstring(ast.parse(data))
                or "Read the source before running this script."
            )
            header = (
                f"this_file: {target.relative_to(root).as_posix()}\n"
                f"tags: {json.dumps([folder.name])}\n"
                f"categories: {json.dumps([folder.name])}\n"
            )
            text = f"---\n{header}---\n\n# {source.stem}\n\n{description}\n\n"
            text += f"Run **{folder.name} > {source.stem}** from FontLab's Scripts menu.\n\n"
            text += "Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.\n\n"
            text += (
                "## Source identity\n\n"
                + f"SHA256: `{hashlib.sha256(data).hexdigest()}`\n\n"
                + f"[Python source at `{revision[:12]}`](https://github.com/fontlabcom/fontlab-python-examples/blob/"
                + revision + "/" + quote(source.relative_to(root).as_posix(), safe="/") + ")\n"
            )
            target.write_text(text)
            lines.append(f"- [{source.stem}]({target.name})")
            index.append(f"- [{source.stem}]({slug(folder.name)}/{target.name})")
        (category / "index.md").write_text("\n".join(lines) + "\n")
        index.append("")
    (output / "index.md").write_text("\n".join(index).rstrip() + "\n")
