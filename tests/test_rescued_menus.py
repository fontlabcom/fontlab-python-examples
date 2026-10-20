# this_file: tests/test_rescued_menus.py
"""Verify archived menu routing without importing Fly or running preserved code."""

import ast
import builtins
import hashlib
import json
import os
import runpy
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path(os.environ.get("FONTLAB_PRESERVED_ROOT", str(ROOT)))
INDEX = json.loads((ROOT / "rescue-index.json").read_text())
ADAPTATIONS = json.loads((ROOT / "menu-adaptations.json").read_text())["adaptations"]
ADAPTED = {row["source_menu"]: row for row in ADAPTATIONS}
ROWS = [
    dict(
        row,
        **(
            {
                "menu": ADAPTED[row["menu"]]["menu"],
                "adapted_entry": ADAPTED[row["menu"]]["entry_point"],
                "adapted_module": "fly.ap."
                + ADAPTED[row["menu"]].get("api_module", "glyph_catalog"),
            }
            if row["menu"] in ADAPTED
            else {}
        ),
    )
    for row in INDEX["menus"]
]


@pytest.fixture(params=ROWS, ids=lambda row: row["menu"])
def row(request: pytest.FixtureRequest) -> dict[str, str]:
    """Exercise every indexed menu independently."""
    return request.param


def test_index_when_loaded_then_has_complete_unique_menu_scope() -> None:
    assert len(ROWS) == INDEX["new_menu_count"] == 494, "Keep all indexed menus"
    assert len({row["menu"] for row in ROWS}) == len(ROWS), (
        "Menu identities must be unique"
    )


def test_menu_when_imported_then_does_not_import_host_or_dispatch(
    row: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    original_import = builtins.__import__

    def isolated_import(name: str, *args: Any, **kwargs: Any) -> Any:
        assert name.split(".")[0] not in {"fly", "fontlabapp"}, (
            "Menu import must stay host-free"
        )
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", isolated_import)
    namespace = runpy.run_path(str(ROOT / row["menu"]), run_name="archived_menu_import")
    assert callable(namespace.get("main")), (
        "Import must expose an explicit main function"
    )


@pytest.mark.parametrize("mode", ["explicit", "main_guard"])
def test_menu_when_launched_then_dispatches_exact_target_once(
    row: dict[str, str], mode: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    entry = row.get("adapted_entry")
    module_name = row["adapted_module"] if entry else "fly.ap.rescued_examples"
    calls: list[tuple] = []
    module = ModuleType(module_name)

    def launch(*args) -> dict[str, object]:
        calls.append(args)
        return {"fake_result": object()}

    setattr(module, entry or "launch", launch)
    # Replace every parent, so an installed Fly/App copy cannot satisfy the import.
    for name in ("fly", "fly.ap"):
        parent = ModuleType(name)
        parent.__path__ = []
        monkeypatch.setitem(sys.modules, name, parent)
    monkeypatch.setitem(sys.modules, module_name, module)
    namespace = runpy.run_path(
        str(ROOT / row["menu"]),
        run_name="__main__" if mode == "main_guard" else "archived_menu_import",
    )
    if mode == "explicit":
        assert calls == [], "Import must not dispatch, even with the helper available"
        assert namespace["main"]() is None, "main has a None return contract"
    expected = () if entry else ((ROOT / row["target"]).resolve(),)
    assert calls == [expected], (
        "Dispatch exactly the reviewed practical entry or indexed target once"
    )


def test_menu_when_inspected_then_preserves_layout_docs_typing_and_source_hash(
    row: dict[str, str],
) -> None:
    path = ROOT / row["menu"]
    source = path.read_text()
    tree = ast.parse(source, filename=row["menu"], feature_version=(3, 11))
    assert len(path.relative_to(ROOT / "Scripts").parts) == 2, "Keep one category level"
    assert f"# this_file: {row['menu']}" in source, "Keep an exact file header"
    main = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "main"
    )
    assert isinstance(main.returns, ast.Constant) and main.returns.value is None, (
        "Annotate main -> None"
    )
    assert not main.args.args and not main.args.kwonlyargs, (
        "Menu main needs no user arguments"
    )
    imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module
        == (
            row["adapted_module"]
            if row.get("adapted_entry")
            else "fly.ap.rescued_examples"
        )
    ]
    assert len(imports) == 1 and imports[0] in list(ast.walk(main)), (
        "Import the shared dispatcher lazily inside main"
    )
    doc = ast.get_docstring(tree) or ""
    for section in ("Purpose:", "Setup:", "Run:", "Result:", "Compatibility:"):
        assert section in doc, f"Document {section} for the preserved entry"
    assert "pending" in doc and "preserved" in doc, "Do not imply native acceptance"
    assert row["target"] in doc, "Identify the preserved source in user instructions"
    assert f"# preserved-source-sha256: {row['target_sha256']}" in source, (
        "Retain source provenance"
    )
    assert (
        hashlib.sha256((ARCHIVE / row["target"]).read_bytes()).hexdigest()
        == row["target_sha256"]
    ), "Never change preserved target bytes"


def test_scripts_when_scanned_then_all_menu_leaves_use_one_level_and_python311() -> (
    None
):
    paths = sorted((ROOT / "Scripts").rglob("*.py"))
    assert len(paths) == 510, (
        "Retain all494original identities (484dispatch+10adapted) and all16practical lessons"
    )
    for path in paths:
        assert len(path.relative_to(ROOT / "Scripts").parts) == 2, (
            f"Unexpected menu depth: {path}"
        )
        ast.parse(path.read_text(), filename=str(path), feature_version=(3, 11))
