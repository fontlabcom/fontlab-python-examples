# this_file: tests/test_curated_menus.py
"""The active tree contains reviewed practical facades, with no archive dispatcher."""

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


def test_active_scripts_when_scanned_then_only_curated_practical_one_level_menus():
    paths = sorted((ROOT / "Scripts").rglob("*.py"))
    assert len(paths) == 100, "Ship the 100 practical facades with native acceptance pending"
    assert {p.parent.name for p in paths} == {
        "Contours",
        "Designer",
        "Dialogs",
        "Drag And Drop",
        "Drawing",
        "Forms",
        "GetGo Fonts",
        "Graphics",
        "Models",
        "Text",
        "Tools",
        "Widgets",
        "Windows",
    }
    for path in paths:
        source = path.read_text()
        assert len(path.relative_to(ROOT / "Scripts").parts) == 2
        assert f"# this_file: {path.relative_to(ROOT).as_posix()}" in source
        assert "rescued_examples" not in source, (
            "An archived dispatcher is not a practical tool"
        )
        ast.parse(source, feature_version=(3, 11))


LESSONS = {
    "Forms/Glyph Metrics Form.py": "glyph-metrics-form",
    "Models/Glyph Metrics Model.py": "glyph-metrics-model",
    "Models/Glyph Name Filter.py": "glyph-name-filter",
}


@pytest.mark.parametrize("relative,entry", LESSONS.items())
def test_existing_lesson_when_run_then_dispatches_exact_packaged_entry(
    monkeypatch, relative, entry
):
    calls = []
    module = ModuleType("fontlab_python_lessons")
    module.launch = lambda key: calls.append(key)
    install_module(monkeypatch, module.__name__, module)
    path = ROOT / "Scripts" / relative
    runpy.run_path(str(path), run_name="inspection")
    assert calls == [], "Inspection must not launch a lesson"
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry], "Run exactly the packaged lesson named by the facade"


GETGO = {
    "Arabic Text Coverage": "unicode_coverage",
    "Audit a Real Font": "font_audit",
    "Compare Master Topology": "master_compatibility",
    "Compare Two Real Fonts": "compare_fonts",
    "Export a TTF Geometry Subset": "export_ttf",
    "Export an OTF Geometry Subset": "export_otf",
    "Font Info Mini Tool": "font_info_ui",
    "Kerning and Classes Report": "kerning_classes",
    "Masters Axes and Instances": "designspace",
    "Name a Disposable Derivative": "naming",
    "Outline Pens and Intersections": "outline_pens",
    "Sidebearings from H": "spacing",
    "Widen Two Glyphs": "batch_transform",
}
GETGO_REFERENCE = json.loads((ROOT / "lessons/provenance/getgo-menus.json").read_text())
SOURCE_COMPATIBILITY = "Compatibility: Uses FontLab's supplied PythonQt."
PACKAGE_COMPATIBILITY = "Compatibility: Native acceptance of this packaged adaptation is pending."


def normalized_getgo_menu(source, relative, compatibility):
    header = f"# this_file: {relative}"
    lines = source.splitlines()
    assert lines.count(header) == 1, "Require the exact layout header once"
    assert sum(line.startswith("# this_file:") for line in lines) == 1
    assert lines.count(compatibility) == 1, "Require the exact compatibility statement once"
    assert sum(line.startswith("Compatibility:") for line in lines) == 1
    return source.replace(header, "# this_file: <menu>").replace(
        compatibility, "Compatibility: <layout>"
    )


def checked_getgo_body(source, relative, compatibility, expected_hash):
    body = normalized_getgo_menu(source, relative, compatibility)
    assert hashlib.sha256(body.encode()).hexdigest() == expected_hash, "Menu body changed"
    return body


def checked_getgo_pair(root, menu, reference):
    bodies = []
    for layout, relative, compatibility in (
        ("source", menu, SOURCE_COMPATIBILITY),
        ("package", f"lessons/{menu}", PACKAGE_COMPATIBILITY),
    ):
        path = root / relative
        assert path.is_file(), f"Required {layout} checkout menu is missing"
        assert reference[layout]["path"] == relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == reference[layout]["sha256"]
        body = checked_getgo_body(
            path.read_text(), relative, compatibility, reference["common_body_sha256"]
        )
        bodies.append(body)
    assert bodies[0] == bodies[1], "Only the declared layout metadata may differ"
    return [root / menu, root / "lessons" / menu]


@pytest.mark.parametrize("title,entry", GETGO.items())
def test_getgo_when_run_then_lazy_exact_packaged_dispatch(monkeypatch, title, entry):
    assert GETGO_REFERENCE["schema"] == "getgo-menu-reference-v1"
    assert GETGO_REFERENCE["native_status"] == "pending"
    references = {item["id"]: item for item in GETGO_REFERENCE["menus"]}
    assert len(GETGO_REFERENCE["menus"]) == len(references) == len(GETGO) == 13
    assert set(references) == set(GETGO.values())
    calls = []
    parent = ModuleType("fontlab_python_lessons")
    parent.__path__ = []
    module = ModuleType("fontlab_python_lessons.getgo")
    result = object()
    module.launch = lambda key: calls.append(key) or result
    install_module(monkeypatch, parent.__name__, parent)
    install_module(monkeypatch, module.__name__, module)
    menu = f"Scripts/GetGo Fonts/GetGo - {title}.py"
    for path in checked_getgo_pair(ROOT, menu, references[entry]):
        calls.clear()
        namespace = runpy.run_path(str(path), run_name="inspection")
        assert calls == [], "Inspection must not open fonts or windows"
        assert namespace["main"]() is result, (
            "Keep the owned report handle returned by the package"
        )
        runpy.run_path(str(path), run_name="__main__")
        assert calls == [entry, entry], (
            "Dispatch the specified installed lesson once per launch"
        )


@pytest.mark.parametrize("layout", ["source", "package"])
@pytest.mark.parametrize("damage", ["compatibility", "executable-text"])
def test_pair_oracle_rejects_unapproved_text_without_changing_real_menus(layout, damage):
    reference = GETGO_REFERENCE["menus"][0]
    relative = reference[layout]["path"]
    source = (ROOT / relative).read_text()
    compatibility = SOURCE_COMPATIBILITY if layout == "source" else PACKAGE_COMPATIBILITY
    if damage == "compatibility":
        source = source.replace(compatibility, "Compatibility: Native acceptance is complete.")
        with pytest.raises(AssertionError, match="exact compatibility"):
            normalized_getgo_menu(source, relative, compatibility)
    else:
        source += "\nraise RuntimeError('unapproved executable text')\n"
        with pytest.raises(AssertionError, match="Menu body changed"):
            checked_getgo_body(source, relative, compatibility, reference["common_body_sha256"])


@pytest.mark.parametrize("layout", ["source", "package"])
def test_pair_oracle_requires_both_real_checkout_peers(monkeypatch, layout):
    reference = GETGO_REFERENCE["menus"][0]
    absent = ROOT / reference[layout]["path"]
    is_file = Path.is_file
    monkeypatch.setattr(Path, "is_file", lambda path: False if path == absent else is_file(path))
    with pytest.raises(AssertionError, match=f"Required {layout} checkout menu is missing"):
        checked_getgo_pair(ROOT, reference["source"]["path"], reference)
