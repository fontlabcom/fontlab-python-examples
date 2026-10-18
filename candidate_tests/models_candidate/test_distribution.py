# this_file: candidate_tests/models_candidate/test_distribution.py
"""Keep the complete small lesson package separate from historical examples."""

import ast
import json
import tomllib
from importlib.resources import files
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]


def test_menu_when_packaged_then_contains_only_three_shallow_python_entries():
    paths = sorted(
        path.relative_to(ROOT / "Scripts")
        for path in (ROOT / "Scripts").rglob("*")
        if path.is_file()
    )
    assert len(paths) == 3 and all(len(path.parts) == 2 and path.suffix == ".py" for path in paths)
    for path in paths:
        body = (ROOT / "Scripts" / path).read_text()
        assert f"this_file: Scripts/{path.as_posix()}" in body
        tree = ast.parse(body)
        assert ast.get_docstring(tree) and "from fontlab_python_lessons import launch" in body


def test_resource_when_packaged_then_has_exact_known_controls_and_no_external_assets():
    from fontlab_python_lessons.forms import CONTROL_NAMES, CONTROL_TYPES

    resource = files("fontlab_python_lessons").joinpath("resources/glyph-metrics-form.ui")
    root = ElementTree.fromstring(resource.read_text())
    widgets = {node.attrib["name"]: node.attrib["class"] for node in root.iter("widget")}
    assert all(
        widgets[name] == kind for name, kind in zip(CONTROL_NAMES, CONTROL_TYPES, strict=True)
    )
    assert not list(root.iter("include")) and not list(root.iter("pixmap")), (
        "The owned form is self-contained"
    )


def test_provenance_when_built_then_all_four_original_identities_have_license_and_destinations():
    record = json.loads((ROOT / "provenance/models.json").read_text())
    assert record["license"] == "Apache-2.0" and len(record["inputs"]) == 4
    for source in record["inputs"]:
        assert len(source["sha256"]) == 64 and (ROOT / source["destination"]).is_file()
    config = tomllib.loads((ROOT / "pyproject.toml").read_text())
    assert config["tool"]["hatch"]["version"]["source"] == "vcs"
    assert config["project"]["dynamic"] == ["version"]
    assert config["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"] == [
        "src/fontlab_python_lessons"
    ]


def test_production_when_imported_then_has_no_alternate_binding_or_font_setters():
    for path in (ROOT / "src/fontlab_python_lessons").glob("*.py"):
        body = path.read_text()
        tree = ast.parse(body)
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        imports += [
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        ]
        assert not any(
            name and name.startswith(("PySide", "PyQt", "requests")) for name in imports
        ), path.name
        methods = [
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        ]
        assert not {"setAdvance", "setMaster", "setProperty", "clipboard"}.intersection(methods), (
            path.name
        )
        compile(body, str(path), "exec")
