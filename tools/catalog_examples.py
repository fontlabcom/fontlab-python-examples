# this_file: tools/catalog_examples.py
"""Infer candidate launchers, retaining uncertainty and all resource mappings."""

from pathlib import PurePosixPath


def example_records(files: list[dict]) -> list[dict]:
    examples = []
    for file in files:
        python = file.get("python")
        qml_launcher = (
            file["kind"] == "qml"
            and PurePosixPath(file["path"]).name in {"main.qml", "app.qml"}
            and not any(
                f.get("python", {}).get("role") in {"entrypoint", "ambiguous"}
                and f["repository"] == file["repository"]
                and PurePosixPath(f["path"]).parent
                == PurePosixPath(file["path"]).parent
                for f in files
            )
        )
        if (not python or python["role"] == "auxiliary") and not qml_launcher:
            continue
        if qml_launcher:
            python = {
                "role": "ambiguous",
                "entrypoint_evidence": [
                    {"kind": "qml-launcher-filename; host loader required"}
                ],
            }
        prefix = str(PurePosixPath(file["path"]).parent)
        members = [
            f
            for f in files
            if f["repository"] == file["repository"]
            and (f["path"].startswith(prefix + "/") or prefix == ".")
        ]
        # Directory membership is conservative: shared and sibling files remain explicit.
        examples.append(
            {
                "id": file["id"],
                "repository": file["repository"],
                "commit": file["commit"],
                "source_entrypoint": file["path"],
                "source_root": prefix,
                "category": file["category"],
                "target_path": file["target_path"],
                "classification": python["role"],
                "ambiguity": None
                if python["role"] == "entrypoint"
                else "No proven module-launch evidence; inspect original/README before excluding or selecting a launcher",
                "entrypoint_evidence": python["entrypoint_evidence"],
                "original_file_ids": sorted(f["id"] for f in members),
                "association_basis": "same source directory subtree; membership does not prove runtime use",
                "ui_qml_qrc_asset_ids": sorted(
                    f["id"] for f in members if f["kind"] != "python"
                ),
                "readme_paths": file["license"]["readme_paths"],
                "capability_needs": sorted(
                    {n for f in members for n in f["capability_needs"]}
                ),
                "dependency_imports": sorted(
                    {i for f in members for i in f.get("python", {}).get("imports", [])}
                ),
                "port_state": "pending",
                "runtime_state": "unexecuted",
            }
        )
    return examples
