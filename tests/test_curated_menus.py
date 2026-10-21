# this_file: tests/test_curated_menus.py
"""The active tree contains reviewed practical facades, with no archive dispatcher."""

import ast
import runpy
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_active_scripts_when_scanned_then_only_curated_practical_one_level_menus():
    paths = sorted((ROOT / "Scripts").rglob("*.py"))
    assert len(paths) == 49, "Ship the 49 practical facades with native acceptance pending"
    assert {p.parent.name for p in paths} == {
        "Dialogs",
        "Forms",
        "GetGo Fonts",
        "Models",
        "Tools",
        "Widgets",
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
    monkeypatch.setitem(sys.modules, module.__name__, module)
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


@pytest.mark.parametrize("title,entry", GETGO.items())
def test_getgo_when_run_then_lazy_exact_packaged_dispatch(monkeypatch, title, entry):
    calls = []
    parent = ModuleType("fontlab_python_lessons")
    parent.__path__ = []
    module = ModuleType("fontlab_python_lessons.getgo")
    result = object()
    module.launch = lambda key: calls.append(key) or result
    monkeypatch.setitem(sys.modules, parent.__name__, parent)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    path = ROOT / "Scripts/GetGo Fonts" / f"GetGo - {title}.py"
    namespace = runpy.run_path(str(path), run_name="inspection")
    assert calls == [], "Inspection must not open fonts or windows"
    assert namespace["main"]() is result, (
        "Keep the owned report handle returned by the package"
    )
    runpy.run_path(str(path), run_name="__main__")
    assert calls == [entry, entry], (
        "Dispatch the specified installed lesson once per launch"
    )
