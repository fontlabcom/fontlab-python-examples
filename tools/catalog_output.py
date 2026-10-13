# this_file: tools/catalog_output.py
"""Deterministic JSON and categorized Markdown output."""

import json
from pathlib import Path


def write_catalog(catalog: dict, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "sources.json").write_text(
        json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "---",
        "this_file: catalog/INDEX.md",
        "---",
        "",
        "# Complete upstream source index",
        "",
        f"{catalog['counts']['source_files']:,} original files; {catalog['counts']['python_files']} Python source files. All ports **pending**; all native execution **unexecuted**.",
        "",
        "Entrypoints are static candidates, not a verified executable-example denominator. Ambiguous candidates stay in scope. Helpers and every resource retain their own mapping in [sources.json](sources.json). Targets are planned paths, not files that exist.",
        "",
        "| Collection | Revision | Files | Python |",
        "| --- | --- | ---: | ---: |",
    ]
    for source in catalog["sources"]:
        lines.append(
            f"| {source['repository']} | `{source['commit']}` | {source['source_files']} | {source['python_files']} |"
        )
    lines += [
        "",
        "Directory resource associations are conservative; local imports and XML/QML references are recorded separately. Licenses are declarations/evidence with review pending. Apache repository licensing does not relicense upstream files.",
        "",
        "Categories: "
        + " · ".join(
            f"[{c}](#{c})" for c in sorted({e["category"] for e in catalog["examples"]})
        ),
    ]
    by_id = {f["id"]: f for f in catalog["files"]}
    for category_name in sorted({e["category"] for e in catalog["examples"]}):
        lines += [
            "",
            f"## {category_name}",
            "",
            "| Original candidate | Planned port | Source evidence | Needs |",
            "| --- | --- | --- | --- |",
        ]
        for example in catalog["examples"]:
            if example["category"] == category_name:
                file = by_id[example["id"]]
                lines.append(
                    f"| [{example['repository']} / {example['source_entrypoint']}]({file['upstream_url']}) | `{example['target_path']}` | {example['classification']} | {', '.join(example['capability_needs']) or 'review source'} |"
                )
    (output / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
