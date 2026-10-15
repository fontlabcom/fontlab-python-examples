# SPDX-License-Identifier: Apache-2.0
# this_file: tools/docs_export.py
"""Export the examples catalogue as Markdown pages for the documentation site.

Reads catalog/ports.json, catalog/sources.json, catalog/insights.json and
examples/recipes/*/README.md, examples/getgo/README.md, and writes docs-export/ deterministically (no dates,
sorted output, LF line endings):

    docs-export/index.md                  overview and per-category counts
    docs-export/categories/<category>.md  every record: status, native, licence, launch
    docs-export/insights.md               original insight examples
    docs-export/recipes/index.md          recipe overview
    docs-export/recipes/<name>.md         each recipe README, links resolved
    docs-export/getgo.md                  real GetGo font examples (examples/getgo/README.md)
    docs-export/manifest.json             format, inputs, pages, counts

Links to repository files use ``--source-base-url`` (default: the repository's
main branch on GitHub); links between exported pages stay relative. From the
repository root::

    python3 tools/docs_export.py            # write docs-export/
    python3 tools/docs_export.py --check    # exit 1 if docs-export/ is stale
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

FORMAT = "fontlab-python-examples.docs-export.v1"
OUTPUT = "docs-export"
SOURCE_BASE_URL = "https://github.com/fontlabcom/fontlab-python-examples/blob/main/"
INPUTS = ("catalog/ports.json", "catalog/sources.json", "catalog/insights.json")
LINK = re.compile(r"(\]\()([^)#\s]+)([^)]*\))")


def cell(text) -> str:
    """One Markdown table cell: single line, pipes escaped."""
    return " ".join(str(text).split()).replace("|", "\\|")


def native_status(port: dict) -> str:
    if port["implementation"] == "blocked":
        return "not run (blocked)"
    if port.get("native_acceptance") != "passed":
        return str(port.get("native_acceptance"))
    evidence = port.get("native_evidence", {})
    commit = evidence.get("implementation_commit")
    source = evidence.get("source", {}).get("file", "")
    detail = f"commit `{commit[:7]}`" if commit else "historical record"
    return (
        f"passed ({detail}; workspace evidence `{source}`)"
        if source
        else f"passed ({detail})"
    )


def record_section(port: dict, base: str) -> list[str]:
    source = port["source"]
    lines = [
        f"### {port['name']}",
        "",
        f"- Source: [{source['repository']} / {source['path']}]({source['upstream_url']})",
        f"- Port: [`{port['target_path']}`]({base}{port['target_path']})",
        f"- Implementation: **{port['implementation']}**",
        f"- Native acceptance: {native_status(port)}",
        f"- Licence: {port['license']['selected']}",
    ]
    if port["implementation"] == "blocked":
        lines += [
            f"- Blocked: {cell(port.get('blocked_reason') or 'no reason recorded')}",
            "",
        ]
        return lines
    lines += [
        "",
        "```python",
        "import fontlab_python_examples as examples",
        "",
        f'handle = examples.launch("{port["source_id"]}")  # inside FontLab',
        f'examples.close("{port["source_id"]}")',
        "```",
        "",
    ]
    return lines


def category_pages(ports: list[dict], categories: dict, base: str) -> dict[str, str]:
    grouped: dict[str, list[dict]] = {}
    for port in ports:
        grouped.setdefault(categories[port["source_id"]], []).append(port)
    pages = {}
    for name, rows in sorted(grouped.items()):
        rows = sorted(rows, key=lambda r: (r["name"].casefold(), r["source_id"]))
        implemented = sum(r["implementation"] == "implemented" for r in rows)
        lines = [
            f"# Examples: {name}",
            "",
            f"{len(rows)} records: {implemented} implemented, {len(rows) - implemented} blocked.",
            "",
            "| Example | Implementation | Native | Licence |",
            "| --- | --- | --- | --- |",
        ]
        ids = anchors([r["name"] for r in rows])
        lines += [
            f"| [{cell(r['name'])}](#{ident}) | {r['implementation']} | "
            f"{'passed' if r.get('native_acceptance') == 'passed' else 'not run'} | "
            f"{cell(r['license']['selected'])} |"
            for r, ident in zip(rows, ids)
        ]
        lines.append("")
        for row in rows:
            lines += record_section(row, base)
        pages[f"categories/{name}.md"] = "\n".join(lines)
    return pages


def anchors(titles: list[str]) -> list[str]:
    """Heading ids as MkDocs (Python-Markdown toc) assigns them on one page:
    lowercase, punctuation dropped, spaces to hyphens, repeats suffixed _1, _2."""
    seen: set[str] = set()
    result = []
    for title in titles:
        base = re.sub(r"[-\s]+", "-", re.sub(r"[^\w\s-]", "", title.lower()).strip())
        ident, n = base, 0
        while ident in seen:
            n += 1
            ident = f"{base}_{n}"
        seen.add(ident)
        result.append(ident)
    return result


def index_page(
    ports: list[dict], categories: dict, insights: list, recipes: list, getgo: int
) -> str:
    counts: dict[str, list[int]] = {}
    for port in ports:
        row = counts.setdefault(categories[port["source_id"]], [0, 0, 0])
        row[0] += 1
        row[1] += port["implementation"] == "implemented"
        row[2] += port.get("native_acceptance") == "passed"
    implemented = sum(r[1] for r in counts.values())
    native = sum(r[2] for r in counts.values())
    lines = [
        "# Python examples for FontLab",
        "",
        (
            f"{len(ports)} catalogued examples: {implemented} implemented for FontLab's PythonQt "
            f"({native} natively accepted: launch, inspect, close), {len(ports) - implemented} "
            "blocked by a recorded host capability. Also: "
            f"[{len(insights)} insight examples](insights.md) and "
            f"[{len(recipes)} recipes](recipes/index.md), plus "
            f"[{getgo} examples on real GetGo fonts](getgo.md)."
        ),
        "",
        "| Category | Records | Implemented | Native passed |",
        "| --- | ---: | ---: | ---: |",
    ]
    lines += [
        f"| [{name}](categories/{name}.md) | {total} | {done} | {native} |"
        for name, (total, done, native) in sorted(counts.items())
    ]
    return "\n".join(lines + [""])


def insights_page(insights: list, base: str) -> str:
    lines = [
        "# Insight examples",
        "",
        "Original examples written for FontLab's PythonQt, each showing one idiom.",
        "",
        "| Example | Idiom | Native | Licence |",
        "| --- | --- | --- | --- |",
    ]
    for item in sorted(insights, key=lambda i: i["rank"]):
        lines.append(
            f"| [{cell(item['title'])}]({base}{item['target_path']}) | {cell(item['idiom'])} | "
            f"{item['native_acceptance']} | {item['license']} |"
        )
    lines += [
        "",
        "```python",
        "import fontlab_python_examples as examples",
        "",
        'examples.launch("signal-lifetime")  # by slug, inside FontLab',
        "```",
        "",
    ]
    return "\n".join(lines)


def recipe_pages(root: Path, base: str) -> dict[str, str]:
    folder = root / "examples/recipes"
    names = sorted(p.name for p in folder.iterdir() if (p / "README.md").is_file())
    pages = {
        "recipes/index.md": resolve(
            read_md(folder / "README.md"), "examples/recipes/", base, names
        )
    }
    for name in names:
        text = read_md(folder / name / "README.md")
        pages[f"recipes/{name}.md"] = resolve(
            text, f"examples/recipes/{name}/", base, names
        )
    return pages


def getgo_page(root: Path, base: str) -> str:
    """The GetGo examples README; its links to fixtures and scripts point at the repository."""
    return resolve(read_md(root / "examples/getgo/README.md"), "examples/getgo/", base, [])


def read_md(path: Path) -> str:
    """README text without its this_file front matter."""
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        text = text.split("\n---\n", 1)[1].lstrip("\n")
    return text


def resolve(text: str, folder: str, base: str, recipes: list[str]) -> str:
    """Recipe folder links become page links; other relative links point at the repository."""

    def replace(match: re.Match) -> str:
        target = match.group(2)
        if re.match(r"[a-z]+:", target) or target.startswith("/"):
            return match.group(0)
        name = target.rstrip("/").split("/")[-1]
        if (
            target.endswith("/") and name in recipes
        ):  # a recipe folder: its exported page
            return match.group(1) + f"{name}.md" + match.group(3)
        path = (Path(folder) / target).as_posix()
        parts = []
        for part in path.split("/"):
            if part == "..":
                parts.pop()
            elif part not in ("", "."):
                parts.append(part)
        return match.group(1) + base + "/".join(parts) + match.group(3)

    return LINK.sub(replace, text)


def inputs(root: Path) -> list[str]:
    """Every file the export reads: the catalogue files and each recipe README."""
    readmes = sorted(
        p.relative_to(root).as_posix()
        for p in (root / "examples/recipes").rglob("README.md")
    )
    return [*INPUTS, *readmes, "examples/getgo/README.md", "examples/getgo/native_manifest.json"]


def build(root: Path, base: str = SOURCE_BASE_URL) -> dict[str, str]:
    """Relative page path -> text, plus manifest.json."""
    ports = json.loads((root / "catalog/ports.json").read_text(encoding="utf-8"))[
        "ports"
    ]
    sources = json.loads((root / "catalog/sources.json").read_text(encoding="utf-8"))
    insights = json.loads((root / "catalog/insights.json").read_text(encoding="utf-8"))[
        "insights"
    ]
    categories = {e["id"]: e["category"] for e in sources["examples"]}
    pages = category_pages(ports, categories, base)
    pages["insights.md"] = insights_page(insights, base)
    recipes = recipe_pages(root, base)
    pages.update(recipes)
    pages["getgo.md"] = getgo_page(root, base)
    getgo = json.loads((root / "examples/getgo/native_manifest.json").read_text(encoding="utf-8"))
    pages["index.md"] = index_page(
        ports, categories, insights, sorted(recipes)[1:], len(getgo["examples"])
    )
    pages = {path: text.rstrip("\n") + "\n" for path, text in sorted(pages.items())}
    implemented = sum(p["implementation"] == "implemented" for p in ports)
    manifest = {
        "format": FORMAT,
        "generator": "tools/docs_export.py",
        "source_base_url": base,
        "inputs": {
            name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in inputs(root)
        },
        "counts": {
            "records": len(ports),
            "implemented": implemented,
            "blocked": len(ports) - implemented,
            "native_passed": sum(p.get("native_acceptance") == "passed" for p in ports),
            "categories": len({categories[p["source_id"]] for p in ports}),
            "insights": len(insights),
            "recipes": len(recipes) - 1,
            "getgo_examples": len(getgo["examples"]),
        },
        "entry": "index.md",
        "pages": [
            {
                "path": path,
                "title": text.splitlines()[0].lstrip("# ").strip(),
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
            for path, text in pages.items()
        ],
    }
    pages["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return pages


def is_finder_metadata(path: Path) -> bool:
    """macOS Finder files (.DS_Store, AppleDouble ._*) are not part of the export."""
    return path.name == ".DS_Store" or path.name.startswith("._")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--output", type=Path, help=f"default: <root>/{OUTPUT}")
    parser.add_argument("--source-base-url", default=SOURCE_BASE_URL)
    parser.add_argument(
        "--check", action="store_true", help="compare instead of writing"
    )
    args = parser.parse_args()
    output = args.output or args.root / OUTPUT
    pages = build(args.root, args.source_base_url)
    existing = (
        {
            p.relative_to(output).as_posix()
            for p in output.rglob("*")
            if p.is_file() and not is_finder_metadata(p)
        }
        if output.is_dir()
        else set()
    )
    if args.check:
        stale = sorted(
            {
                p
                for p, text in pages.items()
                if not (output / p).is_file()
                or (output / p).read_text(encoding="utf-8") != text
            }
            | (existing - set(pages))
        )
        print("stale: " + ", ".join(stale) if stale else f"{len(pages)} files current")
        return 1 if stale else 0
    for extra in existing - set(pages):
        (output / extra).unlink()
    for path, text in pages.items():
        target = output / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="\n")
    print(json.dumps({"pages": len(pages) - 1, "output": str(output)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
