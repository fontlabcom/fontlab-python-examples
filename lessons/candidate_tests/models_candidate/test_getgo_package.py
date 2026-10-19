# this_file: lessons/candidate_tests/models_candidate/test_getgo_package.py
# SPDX-License-Identifier: Apache-2.0
"""Complete packaged GetGo routing, pending acceptance and immutable resources."""

import hashlib
import importlib
import inspect
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[2]
GETGO = ROOT / "src/fontlab_python_lessons/getgo"
MANIFEST = json.loads((GETGO / "native_manifest.json").read_text())
ROWS = MANIFEST["examples"]
MENUS = {
    "font_info_ui": "Scripts/GetGo Fonts/GetGo - Font Info Mini Tool.py",
    "export_ttf": "Scripts/GetGo Fonts/GetGo - Export a TTF Geometry Subset.py",
    "compare_fonts": "Scripts/GetGo Fonts/GetGo - Compare Two Real Fonts.py",
    "designspace": "Scripts/GetGo Fonts/GetGo - Masters Axes and Instances.py",
    "naming": "Scripts/GetGo Fonts/GetGo - Name a Disposable Derivative.py",
    "outline_pens": "Scripts/GetGo Fonts/GetGo - Outline Pens and Intersections.py",
    "kerning_classes": "Scripts/GetGo Fonts/GetGo - Kerning and Classes Report.py",
    "master_compatibility": "Scripts/GetGo Fonts/GetGo - Compare Master Topology.py",
    "batch_transform": "Scripts/GetGo Fonts/GetGo - Widen Two Glyphs.py",
    "spacing": "Scripts/GetGo Fonts/GetGo - Sidebearings from H.py",
    "export_otf": "Scripts/GetGo Fonts/GetGo - Export an OTF Geometry Subset.py",
    "unicode_coverage": "Scripts/GetGo Fonts/GetGo - Arabic Text Coverage.py",
    "font_audit": "Scripts/GetGo Fonts/GetGo - Audit a Real Font.py",
}


def test_complete_fixture_payload_and_pending_runtime_provenance():
    data = GETGO / "data"
    fonts = json.loads((data / "manifest.json").read_text())["fonts"]
    assert len(fonts) == 99
    assert MANIFEST["native_status"] == "pending"
    assert all(
        row["native_status"] == "pending" and "native_verification" not in row for row in ROWS
    )
    for row in fonts:
        assert hashlib.sha256((data / row["path"]).read_bytes()).hexdigest() == row["sha256"]
        assert (data / row["license_path"]).read_text().strip()
    provenance = json.loads((ROOT / "provenance/getgo.json").read_text())
    assert len(provenance["inputs"]) == 19 and provenance["native_status"] == "pending"
    assert len(provenance["resources"]) == len([p for p in data.rglob("*") if p.is_file()])
    for resource in provenance["resources"]:
        assert (
            hashlib.sha256((data / resource["path"]).read_bytes()).hexdigest() == resource["sha256"]
        )
    for row in provenance["inputs"]:
        assert len(row["source_sha256"]) == 64 and (ROOT / row["destination"]).is_file()
        assert (
            hashlib.sha256((ROOT / row["destination"]).read_bytes()).hexdigest()
            == row["destination_sha256"]
        )
    for path in GETGO.glob("*.py"):
        assert "examples.getgo" not in path.read_text()
        assert (
            "# this_file:" in path.read_text()
            and "SPDX-License-Identifier: Apache-2.0" in path.read_text()
        )


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["id"])
@pytest.mark.parametrize("custom", [False, True])
def test_launch_calls_original_run_once_with_defaults_or_original_kwargs(row, custom, monkeypatch):
    package = importlib.import_module("fontlab_python_lessons.getgo")
    calls = []
    shows = []
    module = importlib.import_module(row["module"])
    defaults = {name: p.default for name, p in inspect.signature(module.run).parameters.items()}
    # Explicit original defaults exercise every supported keyword without inventing a new API.
    kwargs = defaults if custom else {}
    result = {"text": "مرحبا", "nested": [1]}

    def run(**kw):
        calls.append(kw)
        return result

    monkeypatch.setattr(module, "run", run)
    monkeypatch.setattr(module, "show", lambda: run(), raising=False)
    monkeypatch.setitem(
        sys.modules,
        "fly.ap.reports",
        SimpleNamespace(show_report=lambda data, **kw: shows.append((data, kw)) or "window"),
    )
    actual = package.launch(row["id"], **kwargs)
    assert calls == [kwargs]
    if row["id"] == "font_info_ui":
        assert actual is result and not shows
    else:
        assert actual == "window" and shows[0][0] is result
        assert shows[0][1]["key"] == "getgo-" + row["id"]


def test_unknown_entry_fails_before_module_or_ui_import(monkeypatch):
    from fontlab_python_lessons import getgo

    monkeypatch.setattr(
        getgo, "import_module", lambda name: pytest.fail("Must reject unknown name first")
    )
    with pytest.raises(KeyError):
        getgo.launch("../font_audit")


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["id"])
def test_all_thirteen_real_menu_routes_match_packaged_entry(row, monkeypatch):
    assert len(MENUS) == len(ROWS) == 13
    menu = MENUS[row["id"]]
    calls = []
    monkeypatch.setitem(
        sys.modules,
        "fontlab_python_lessons.getgo",
        SimpleNamespace(launch=lambda name: calls.append(name)),
    )
    paths = [ROOT.parent / menu, ROOT / menu]
    for path in paths:
        calls.clear()
        ns = runpy.run_path(str(path), run_name="packaged_menu_import")
        assert calls == []
        ns["main"]()
        assert calls == [row["id"]]
        calls.clear()
        runpy.run_path(str(path), run_name="__main__")
        assert calls == [row["id"]]

    def normalized(path):
        return "\n".join(
            line for line in path.read_text().splitlines() if not line.startswith("# this_file:")
        )

    assert normalized(paths[0]) == normalized(paths[1])


def test_info_handle_after_owned_parent_destruction_is_idempotent():
    from fontlab_python_lessons.getgo.font_info_ui import InfoTool

    tool = InfoTool(SimpleNamespace(_released=True), {"family": "Snapshot"})
    tool.close()
    assert tool.widget is None


def test_designspace_run_refuses_changed_master_during_inspection(monkeypatch):
    from test_getgo import FakePackage
    from contextlib import contextmanager

    module = importlib.import_module("fontlab_python_lessons.getgo.designspace")
    package = FakePackage()

    @contextmanager
    def owned(*args):
        yield package, {"page_url": "https://example.org"}

    monkeypatch.setattr(module, "owned_font", owned)

    def changed(package):
        package.master = "Changed"
        return []

    monkeypatch.setattr(module, "instance_rows", changed)
    with pytest.raises(AssertionError, match="selected master"):
        module.run()


def test_binary_rejects_wrong_suffix_and_missing_notdef(tmp_path):
    from fontlab_python_lessons.getgo._binary import compile_subset

    with pytest.raises(ValueError, match="suffix"):
        compile_subset({}, tmp_path / "wrong.otf", True)
    with pytest.raises(ValueError, match="notdef"):
        compile_subset({"glyphs": {}}, tmp_path / "bad.ttf", True)


@pytest.mark.parametrize(
    "damage,match",
    [
        ("format", "format"),
        ("upm", "UPM"),
        ("license", "licence"),
        ("width", "Advance"),
        ("empty", "winding"),
        ("bounds", "bounds"),
    ],
)
def test_binary_verification_detects_independent_readback_damage(tmp_path, damage, match):
    from test_getgo import binary_data
    from fontlab_python_lessons.getgo._binary import compile_subset, verify_subset

    data = binary_data()
    path = compile_subset(data, tmp_path / "control.ttf", True)
    # Change the expected source independently of the already built binary.
    if damage == "format":
        with pytest.raises(AssertionError, match=match):
            verify_subset(path, data, False)
        return
    if damage == "upm":
        data["upm"] = 2048
    if damage == "license":
        data["license"] = "Wrong licence"
    if damage == "width":
        data["glyphs"]["A"]["width"] += 100
    if damage == "empty":
        data["glyphs"]["A"]["recording"] = []
    if damage == "bounds":
        data["glyphs"]["A"]["recording"] = [
            (op, tuple((p[0] + 100, p[1]) for p in args)) if args else (op, args)
            for op, args in data["glyphs"]["A"]["recording"]
        ]
    with pytest.raises(AssertionError, match=match):
        verify_subset(path, data, True)


@pytest.mark.parametrize("failure", [False, "exception", None])
def test_info_tool_delegates_owned_close_once_and_retains_failed_owner(failure):
    from fontlab_python_lessons.getgo.font_info_ui import InfoTool

    calls = []

    def close():
        calls.append("close")
        if failure == "exception":
            raise RuntimeError("close failed")
        return failure

    widget = SimpleNamespace(
        _released=False,
        _release=lambda: None,
        close=close,
        deleteLater=lambda: pytest.fail("App close owns deletion"),
    )
    tool = InfoTool(widget, {})
    if failure is not None:
        with pytest.raises(RuntimeError):
            tool.close()
        assert tool.widget is widget
    else:
        tool.close()
        tool.close()
        assert tool.widget is None
    assert calls == ["close"]


def test_all_getgo_functions_have_explicit_boundary_annotations():
    import ast

    for path in GETGO.glob("*.py"):
        tree = ast.parse(path.read_text(), feature_version=(3, 11))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                assert node.returns is not None, (path, node.name)
                args = [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]
                args += [a for a in (node.args.vararg, node.args.kwarg) if a is not None]
                assert all(arg.annotation is not None for arg in args), (path, node.name)
