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
    if "review_decisions" in catalog:
        lines[6] = (
            f"{catalog['counts']['source_files']:,} original files; "
            f"{catalog['counts']['python_files']} Python source files. "
            "This source inventory records static/reviewed roles; see ports.json for implementation and native status."
        )
        lines[8] = (
            "Static candidates retain their identities. Reviewed classifications and shared ownership "
            "are recorded per file in [sources.json](sources.json) and [reviews.json](reviews.json). "
            "Runtime acceptance is recorded separately in [ports.json](ports.json). Targets remain planned paths."
        )
    if "port_manifest" in catalog:
        states = catalog["counts"]["port_states"]
        lines[6] = (
            f"{catalog['counts']['source_files']:,} original files; "
            f"{catalog['counts']['python_files']} Python source files. Port records: "
            + ", ".join(f"{count} {state}" for state, count in states.items())
            + "."
        )
        lines[8] += (
            " Official originals remain archived. Independent replacements and capability blockers "
            "are bound to [specifications](../clean-room-specs/INDEX.json) by "
            "[receipts](../clean-room/receipts/). Archived resources are not re-licensed as replacements."
        )
        executed = catalog["counts"]["examples_native_executed"]
        ported = catalog["counts"].get("examples_ported", executed)
        lines[8] += f" Native launch/inspect/close passes: {executed}" + (
            "; independent replacements await new native acceptance."
            if executed < ported
            else " (every implemented port; recorded by tools/record_native.py)."
        )
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
            "| Original candidate | Planned port | State | Source evidence | Needs |",
            "| --- | --- | --- | --- | --- |",
        ]
        for example in catalog["examples"]:
            if example["category"] == category_name:
                file = by_id[example["id"]]
                target = example.get("port_target_path", example["target_path"])
                lines.append(
                    f"| [{example['repository']} / {example['source_entrypoint']}]({file['upstream_url']}) | `{target}` | {example['port_state']} | {example['classification']} | {', '.join(example['capability_needs']) or 'review source'} |"
                )
    (output / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
