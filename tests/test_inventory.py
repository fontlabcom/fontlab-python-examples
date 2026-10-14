# this_file: tests/test_inventory.py
"""Inventory tests use owned source bytes; they never import upstream examples."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from inventory import build_catalog, main, write_catalog
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
    assert json.loads((tmp_path / "catalog/sources.json").read_text()) == build_catalog(
        *sources
    ), "Successful CLI writes the complete catalog"
    assert (tmp_path / "catalog/INDEX.md").is_file(), "Successful CLI writes navigation"
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


@pytest.mark.parametrize(
    "text",
    [
        "if enabled:\n    def unused():\n        widget.show()\n",
        "if enabled:\n    async def unused():\n        widget.show()\n",
        "if enabled:\n    class Helper:\n        def unused(self):\n            widget.show()\n",
        "class Helper:\n    async def unused(self):\n        widget.show()\n",
        "if enabled:\n    launch = lambda: widget.show()\n",
        "class Helper:\n    launch = lambda: widget.show()\n",
        "def unused():\n    if __name__ == '__main__':\n        widget.show()\n",
        "if enabled:\n    async def unused():\n        if __name__ == '__main__':\n            widget.show()\n",
        "class Helper:\n    def unused(self):\n        if __name__ == '__main__':\n            widget.show()\n",
        "def unused():\n    class Nested:\n        widget.show()\n",
    ],
)
def test_deferred_bodies_when_nested_then_no_entrypoint_evidence(text):
    analysis = python_analysis(text, "helper.py")
    assert analysis["role"] == "ambiguous", "Deferred bodies prove no module launch"
    assert analysis["entrypoint_evidence"] == [], "Deferred guards also stay excluded"
    assert "widget.show" in analysis["api_calls"], "Broad API extraction is preserved"


@pytest.mark.parametrize(
    "text, kinds",
    [
        ("if enabled:\n    widget.show()\n", ["module-launch-call"]),
        ("class Launcher:\n    widget.show()\n", ["module-launch-call"]),
        (
            "if enabled:\n    class Launcher:\n        widget.show()\n",
            ["module-launch-call"],
        ),
        ("class Launcher(widget.show()):\n    pass\n", ["module-launch-call"]),
        ("@widget.show()\nclass Launcher:\n    pass\n", ["module-launch-call"]),
        ("def unused(value=widget.show()):\n    pass\n", ["module-launch-call"]),
        ("async def unused(value=widget.show()):\n    pass\n", ["module-launch-call"]),
        ("launch = lambda value=widget.show(): None\n", ["module-launch-call"]),
        (
            "if __name__ == '__main__':\n    widget.show()\n",
            ["main-guard", "module-launch-call"],
        ),
        (
            "class Launcher:\n    if __name__ == '__main__':\n        widget.show()\n",
            ["main-guard", "module-launch-call"],
        ),
    ],
)
def test_definition_time_and_module_calls_when_present_then_candidate(text, kinds):
    analysis = python_analysis(text, "helper.py")
    assert analysis["role"] == "entrypoint", (
        "Definition-time expressions remain evidence"
    )
    assert [e["kind"] for e in analysis["entrypoint_evidence"]] == kinds


def test_deferred_imports_when_present_then_broad_capabilities_preserved():
    text = "if enabled:\n    def unused():\n        from PyQt5 import QtNetwork\n        QtNetwork.QNetworkAccessManager()\n"
    analysis = python_analysis(text, "helper.py")
    assert analysis["role"] == "ambiguous"
    assert analysis["imports"] == ["PyQt5"]
    assert analysis["qt_symbols"] == ["PyQt5.QtNetwork"]
    assert analysis["qt_bindings"] == ["PyQt5"]
    assert analysis["api_calls"] == ["PyQt5.QtNetwork.QNetworkAccessManager"]
    assert "network" in capabilities("helper.py", text, analysis)


@pytest.mark.parametrize("operation", ["mkdir", "sources.json", "INDEX.md"])
def test_cli_output_permission_failure_when_injected_then_portable_error(
    sources, tmp_path, monkeypatch, capsys, operation
):
    trees, recovery, roots = sources
    tree_path, recovery_path = tmp_path / "trees.json", tmp_path / "recovery.json"
    tree_path.write_text(json.dumps(trees))
    recovery_path.write_text(json.dumps(recovery))
    output = tmp_path / "private-output"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory.py",
            "--tree-receipt",
            str(tree_path),
            "--recovery-receipt",
            str(recovery_path),
            "--source-root",
            f"owned/examples={roots['owned/examples']}",
            "--output",
            str(output),
        ],
    )
    method = "mkdir" if operation == "mkdir" else "write_text"
    original = getattr(Path, method)

    def fail_output(path, *args, **kwargs):
        if path == output or path == output / operation:
            raise PermissionError(13, "Permission denied", str(path))
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, method, fail_output)
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1, "Output failure must return the CLI failure code"
    captured = capsys.readouterr()
    assert captured.err == "Inventory failed: PermissionError\n"
    assert captured.out == "", "Failure must not print success counts"
    assert str(tmp_path) not in captured.err and "Traceback" not in captured.err
