# this_file: tests/test_inventory.py
"""Inventory tests use owned source bytes; they never import upstream examples."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inventory import build_catalog, write_catalog
from provenance import declared_terms, relative_path
from resource_analysis import capabilities, resource_analysis
from source_analysis import python_analysis


def test_complete_accounting_and_entrypoint_distinction(sources):
    catalog = build_catalog(*sources)
    assert catalog["counts"]["source_files"] == 9, "Every original file needs a record"
    files = {f["path"]: f for f in catalog["files"]}
    assert files["widgets/helper.py"]["python"]["role"] == "auxiliary"
    assert files["widgets/main.py"]["python"]["role"] == "entrypoint"
    assert files["widgets/broken.py"]["python"]["parse"]["state"] == "syntax-error"
    assert files["widgets/broken.py"]["python"]["role"] == "ambiguous"
    assert files["widgets/main.py"]["python"]["qt_bindings"] == ["PyQt5"]
    assert (
        "PyQt5.QtWidgets.QApplication"
        in files["widgets/main.py"]["python"]["api_calls"]
    )
    assert files["widgets/view.ui"]["xml"]["classes"] == ["QWidget"]
    assert files["widgets/resources.qrc"]["xml"]["references"] == ["icon.png"]
    assert (
        files["widgets/resources.qrc"]["resource_reference_resolutions"][0][
            "original_file_id"
        ]
        == files["widgets/icon.png"]["id"]
    )
    assert all(
        f["port_state"] == "pending" and f["runtime_state"] == "unexecuted"
        for f in catalog["files"]
    )


def test_deterministic_output_and_portability(sources, tmp_path):
    catalog = build_catalog(*sources)
    first, second = tmp_path / "first", tmp_path / "second"
    write_catalog(catalog, first)
    write_catalog(build_catalog(*sources), second)
    assert {p.name: p.read_bytes() for p in first.iterdir()} == {
        p.name: p.read_bytes() for p in second.iterdir()
    }
    output = json.dumps(catalog)
    assert str(tmp_path) not in output and "storage_path" not in output
    assert all(not f["target_path"].startswith("/") for f in catalog["files"])


def test_case_collisions_keep_distinct_source_and_target_paths(sources):
    catalog = build_catalog(*sources)
    collisions = [
        f for f in catalog["files"] if f["path"].endswith(("Subplot.py", "subplot.py"))
    ]
    assert len(collisions) == 2
    assert len({f["target_path"].casefold() for f in collisions}) == 2
    assert len({f["id"] for f in collisions}) == 2
    assert all(f["category"] == "matplotlib" for f in collisions)


@pytest.mark.parametrize(
    "change", ["bytes", "tree", "missing", "extra", "revision", "traversal"]
)
def test_source_or_receipt_mismatch_fails(sources, change):
    trees, recovery, roots = sources
    root = next(iter(roots.values()))
    record = recovery["repositories"][0]["files"]["widgets/main.py"]
    if change == "bytes":
        (root / record["storage_path"]).write_bytes(b"changed")
    elif change == "tree":
        trees["repositories"][0]["tree"]["tree"].pop()
    elif change == "missing":
        (root / record["storage_path"]).unlink()
    elif change == "extra":
        (root / "unreceipted.py").write_bytes(b"unexpected")
    elif change == "revision":
        recovery["repositories"][0]["commit"] = "b" * 40
    else:
        record["storage_path"] = "../escape"
    with pytest.raises(ValueError):
        build_catalog(trees, recovery, roots)


def test_license_claims_remain_evidence_and_review_pending(sources):
    catalog = build_catalog(*sources)
    assert all(f["license"]["review_state"] == "pending" for f in catalog["files"])
    assert all(f["license"]["declared_terms"] == ["unknown"] for f in catalog["files"])


def test_source_analysis_checks_launch_semantics_and_resource_errors():
    assert (
        python_analysis("if __name__ != '__main__':\n    value = 1\n", "helper.py")[
            "role"
        ]
        == "ambiguous"
    )
    assert (
        python_analysis("def create():\n    app = QApplication([])\n", "helper.py")[
            "role"
        ]
        == "ambiguous"
    )
    assert resource_analysis("bad.qrc", "<RCC>")["xml"]["state"] == "parse-error"
    assert resource_analysis(
        "main.qml", 'import QtQuick 2.0\nImage { source: "icon.png" }'
    )["qml"]["references"] == ["icon.png"]
    assert "network" not in capabilities(
        "helper.py", "# https://license.example\nvalue = 1", {}
    )


def test_license_declaration_detection_keeps_unrecognized_terms_visible():
    assert declared_terms("SPDX-License-Identifier: MIT OR GPL-3.0-only") == [
        "MIT OR GPL-3.0-only"
    ]
    assert declared_terms("Unspecified permissions") == []
    for path in ["/absolute", "../escape", "a/../escape", "windows\\path"]:
        with pytest.raises(ValueError):
            relative_path(path)


def test_cli_writes_catalog_and_reports_portable_errors(sources, tmp_path):
    trees, recovery, roots = sources
    tree_path, recovery_path = tmp_path / "trees.json", tmp_path / "recovery.json"
    tree_path.write_text(json.dumps(trees))
    recovery_path.write_text(json.dumps(recovery))
    script = Path(__file__).resolve().parents[1] / "tools" / "inventory.py"
    command = [
        sys.executable,
        str(script),
        "--tree-receipt",
        str(tree_path),
        "--recovery-receipt",
        str(recovery_path),
        "--source-root",
        f"owned/examples={roots['owned/examples']}",
        "--output",
        str(tmp_path / "catalog"),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["source_files"] == 9
    recovery_path.unlink()
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert str(tmp_path) not in result.stderr
    assert "FileNotFoundError" in result.stderr


def test_qml_launcher_keeps_source_identity_without_runtime_claim():
    from catalog_examples import example_records

    file = {
        "id": "owned-qml",
        "kind": "qml",
        "path": "qml/app.qml",
        "repository": "owned/examples",
        "commit": "a" * 40,
        "category": "qml",
        "target_path": "ports/qml/app.qml",
        "capability_needs": ["qml"],
        "license": {"readme_paths": ["README.md"]},
    }
    candidates = example_records([file])
    assert candidates[0]["source_entrypoint"] == "qml/app.qml"
    assert candidates[0]["classification"] == "ambiguous"
    assert candidates[0]["original_file_ids"] == ["owned-qml"]


def test_existing_ds_store_is_preserved_without_changing_original_denominator(sources):
    ds_store = next(iter(sources[2].values())) / ".DS_Store"
    ds_store.write_bytes(b"owned metadata fixture")
    assert build_catalog(*sources)["counts"]["source_files"] == 9
    assert ds_store.read_bytes() == b"owned metadata fixture"
