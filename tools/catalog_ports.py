# this_file: tools/catalog_ports.py
"""Project hash-bound port states into the upstream inventory, without source I/O."""

from collections import Counter


def apply_port_states(catalog: dict, manifest: dict) -> None:
    """Keep original identities while regenerating runtime and relocation metadata."""
    files = {row["id"]: row for row in catalog["files"]}
    examples = {row["id"]: row for row in catalog["examples"]}
    for port in manifest["ports"]:
        for item in [port, *port["resources"]]:
            source = files[item["source_id"]]
            if source["sha256"] != item["source"]["sha256"]:
                raise ValueError(f"Port source hash mismatch: {item['source_id']}")
            _project(source, item, port)
        if port["source_id"] in examples:
            _project(examples[port["source_id"]], port, port)
    states = Counter(row["implementation"] for row in manifest["ports"])
    catalog["counts"].update(
        port_states=dict(sorted(states.items())),
        examples_clean_room_pending=states["clean_room_pending"],
        examples_ported=states["implemented"],
        examples_native_executed=sum(
            row["implementation"] == "implemented"
            and row["native_acceptance"] == "passed"
            for row in manifest["ports"]
        ),
    )
    catalog["port_manifest"] = "catalog/ports.json"
    if "analysis_semantics" in catalog:
        catalog["analysis_semantics"] = catalog["analysis_semantics"].replace(
            "all ports pending/native unexecuted",
            "port states projected from hash-bound manifest",
        )


def _project(target: dict, item: dict, port: dict) -> None:
    """Pending distribution makes no licence or acceptance claim for removed files."""
    target.update(
        port_state=port["implementation"],
        runtime_state=port["native_acceptance"],
        port_target_path=item["target_path"],
    )
    for field in ("archive", "spec"):
        target.pop(field, None)
    if port["implementation"] == "clean_room_pending":
        target.pop("license", None)
        target["archive"] = item["archive"]
        target["spec"] = port["spec"]
