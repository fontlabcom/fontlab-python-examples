# this_file: tests/test_wp09_labs.py
"""Core labs remain lazy menu entrypoints with exact profile-group identities."""

import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

from module_doubles import install_module

ROOT = Path(__file__).resolve().parents[1]
LABS = {
    "E01": "Model Filtering Lab",
    "E02": "Tree Models Lab",
    "E03": "Metrics Controls Lab",
    "E04": "Calendar Lab",
    "E05": "Completion Lab",
    "E06": "Drag Drop Lab",
    "E07": "Proof Composition Lab",
    "E08": "Unicode Lab",
    "E09": "Review Model Lab",
}


@pytest.mark.parametrize("identifier,title", LABS.items())
def test_lab_when_inspected_then_lazy_and_when_run_then_exact_app_dispatch(
    monkeypatch, identifier, title
):
    calls = []
    result = object()
    for name in ("fly", "fly.ap", "fly.ap.studios", "fly.ap.studios.core_pythonqt_labs"):
        install_module(monkeypatch, name, ModuleType(name))
    sys.modules["fly.ap.studios.core_pythonqt_labs"].show = (
        lambda key: calls.append(key) or result
    )
    path = ROOT / "Scripts/Labs" / f"{title}.py"
    source = path.read_text()
    namespace = runpy.run_path(str(path), run_name="inspection")
    assert not calls, "Inspecting a menu must not create a window or read a font"
    assert namespace["main"]() is result, "Return the shell owner for lifecycle control"
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [identifier, identifier]
    assert "# SPDX-License-Identifier: Apache-2.0" in source
    assert f"# this_file: Scripts/Labs/{title}.py" in source
    doc = ast.get_docstring(ast.parse(source, feature_version=(3, 11)))
    assert all(label in doc for label in ("Setup:", "Usage:", "Credits:"))


RETAINED_LESSONS = {
    "Scripts/Models/Glyph Name Filter.py",
    "Scripts/Models/Glyph Metrics Model.py",
    "Scripts/Forms/Glyph Metrics Form.py",
}
ROWS = json.loads((ROOT / "menu-consolidations.json").read_text())["transitions"]
COMPATIBILITY = [
    row for row in ROWS
    if Path(row["destination"]["path"]).stem in LABS.values()
    and row["source"]["path"] not in RETAINED_LESSONS
]


@pytest.mark.parametrize("row", COMPATIBILITY, ids=lambda row: row["source"]["path"])
def test_compatibility_route_when_run_then_selects_its_exact_profile(monkeypatch, row):
    calls = []
    result = object()
    for name in ("fly", "fly.ap", "fly.ap.studios", "fly.ap.studios.core_pythonqt_labs"):
        install_module(monkeypatch, name, ModuleType(name))
    sys.modules["fly.ap.studios.core_pythonqt_labs"].show = (
        lambda key, *, profile: calls.append((key, profile)) or result
    )
    path = ROOT / row["source"]["path"]
    assert row["compatibility_launcher"] == {
        "path": row["source"]["path"],
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    identifier = next(key for key, title in LABS.items()
                      if title == Path(row["destination"]["path"]).stem)
    namespace = runpy.run_path(str(path), run_name="inspection")
    assert not calls
    assert namespace["main"]() is result
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [(identifier, path.stem)] * 2
    assert "# SPDX-License-Identifier: Apache-2.0" in path.read_text()
    tree = ast.parse(path.read_text())
    assert len([node for node in tree.body if isinstance(node, ast.FunctionDef)]) == 1
    assert not any(isinstance(node, ast.ClassDef) for node in tree.body)



def test_wp09_inventory_when_counted_then_only_the_nine_owned_labs_are_implemented():
    implemented = [row for row in ROWS if row["acceptance"]["state"] == "implemented"]
    assert len(implemented) == 51
    assert len(COMPATIBILITY) == 48
    assert {Path(row["destination"]["path"]).stem for row in implemented} == set(LABS.values())
    assert all(not row["acceptance"]["behavior_parity"] and not row["acceptance"]["native"]
               for row in implemented)
