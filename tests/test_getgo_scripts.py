# this_file: tests/test_getgo_scripts.py
"""Real GetGo examples: pure helpers, owned-document doubles and optional binaries."""

import ast
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
GETGO = ROOT / "examples/getgo"


def test_native_manifest_covers_thirteen_original_host_free_examples():
    import importlib

    manifest = json.loads((GETGO / "native_manifest.json").read_text())
    fonts = {
        r["id"]: r
        for r in json.loads((ROOT / "testdata/getgo/manifest.json").read_text())[
            "fonts"
        ]
    }
    rows = manifest["examples"]
    assert len(rows) == 13, "The native contract lists exactly thirteen examples"
    assert len({r["module"] for r in rows}) == len(rows)
    for row in rows:
        path = ROOT / (row["module"].replace(".", "/") + ".py")
        source = path.read_text()
        compile(source, str(path), "exec")
        assert f"# this_file: {path.relative_to(ROOT)}" in source
        assert "SPDX-License-Identifier: Apache-2.0" in source
        header = source[: source.index("\nfrom ")]
        for font_id in row["fonts"]:
            record = fonts[font_id]
            assert record["name"] in header and record["license"] in header
            assert record["page_url"] in header
            assert (ROOT / "testdata/getgo" / record["path"]).is_file()
        tree = ast.parse(source)
        assert not any(
            isinstance(n, (ast.Import, ast.ImportFrom))
            and (getattr(n, "module", "") or "").split(".")[0]
            in {"fontlab", "fontgate", "PythonQt"}
            for n in tree.body
        ), "Native imports belong inside entry functions"
        module = importlib.import_module(row["module"])
        assert callable(getattr(module, row["entry_function"]))
        assert row["native_status"] == "unexecuted"
        assert row["expected"]
        for check in row["expected"]:
            assert isinstance(check, dict) and len(check) == 2
            assert isinstance(check["path"], list) and check["path"]
            assert all(type(key) in (str, int) for key in check["path"])
            assert set(check) - {"path"} <= {"equals", "len", "contains", "gt"}
            if "len" in check:
                assert type(check["len"]) is int and check["len"] >= 0
        assert row["cleanup_function"] == (
            "handle.close" if row["id"] == "font_info_ui" else None
        )
        assert path.stem in (GETGO / "README.md").read_text()
    assert manifest["execution"]["run_python"] == "setup_and_poll_only"


def test_pure_audit_reports_duplicates_unencoded_and_missing_anchors():
    from examples.getgo.font_audit import summarize

    rows = [
        {"name": "A", "unicodes": [65], "anchors": []},
        {"name": "A.alt", "unicodes": [65], "anchors": ["top"]},
        {"name": "unencoded", "unicodes": [], "anchors": []},
    ]
    result = summarize(rows, {"A": ["top"]})
    assert result == {
        "glyph_count": 3,
        "encoded_count": 1,
        "unencoded": ["unencoded"],
        "duplicate_unicodes": {"U+0041": ["A", "A.alt"]},
        "missing_anchors": {"A": ["top"]},
        "anchor_count": 1,
        "glyphs_with_anchors": 1,
    }
    assert summarize([], {})["glyph_count"] == 0


def test_unicode_coverage_checks_scalars_without_claiming_shaping():
    from examples.getgo.unicode_coverage import coverage

    assert coverage("A\U0001f600AA", [65]) == {
        "covered": ["U+0041"],
        "missing": ["U+1F600"],
    }
    assert coverage("", []) == {"covered": [], "missing": []}


def test_naming_plan_is_deliberate_and_preserves_unrelated_metadata():
    from examples.getgo.naming import family_names

    assert (
        family_names("Scripting Sample", "Regular")["postscriptFontName"]
        == "ScriptingSample-Regular"
    )
    for bad in ("", "  ", None, "A/B"):
        with pytest.raises((TypeError, ValueError)):
            family_names(bad, "Regular")


def test_spacing_plan_accounts_for_both_sidebearings_and_negative_overhang():
    from examples.getgo.spacing import spacing_plan

    assert spacing_plan(-10, 490, 30, 40) == {"shift": 40, "width": 570}
    with pytest.raises(ValueError):
        spacing_plan(10, -10, 0, 0)


def test_transform_plan_rejects_nonfinite_and_negative_scaling():
    from examples.getgo.batch_transform import transformed

    assert transformed([(10, -20)], 1.2, 5) == [(17, -20)]
    assert transformed([], 1, 0) == []
    for scale in (0, -1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            transformed([], scale, 0)


def test_compare_fonts_normalizes_units_and_reports_asymmetric_glyphs():
    from examples.getgo.compare_fonts import compare

    result = compare({"A": 500, "B": 600}, 1000, {"A": 1100, "C": 600}, 2000)
    assert result == {
        "only_left": ["B"],
        "only_right": ["C"],
        "width_delta_em": {"A": 0.05},
    }
    with pytest.raises(ValueError):
        compare({}, 0, {}, 1000)


def test_kerning_classes_reports_dangling_members_and_typed_pairs():
    from examples.getgo.kerning_classes import summarize_kerning

    result = summarize_kerning(
        [
            {
                "left": "A",
                "right": "V",
                "value": 0,
                "left_mode": "glyphMode",
                "right_mode": "glyphMode",
            }
        ],
        [("LeftA", (["A", "absent"], 1))],
        ["A", "V"],
    )
    assert result["pair_count"] == 1 and result["pairs"][0]["value"] == 0
    assert result["missing_members"] == {"LeftA": ["absent"]}


def test_compatibility_reports_missing_layers_and_different_node_topology():
    from examples.getgo.master_compatibility import compatibility

    assert compatibility({"Light": [[True, True]], "Bold": [[True, True]]})[
        "compatible"
    ]
    assert not compatibility({"Light": [[True]], "Bold": [[False]]})["compatible"]
    assert compatibility({"Light": [], "Bold": None})["missing_layers"] == ["Bold"]


def test_designspace_reports_instances_in_axis_order_without_changing_master():
    from examples.getgo.designspace import instance_rows

    axis = SimpleNamespace(tag="wght", valueWeight=lambda loc, default: loc["wt"])
    package = SimpleNamespace(
        axes=[axis],
        instances=[
            SimpleNamespace(name="Medium", exportable=True, location={"wt": 50})
        ],
    )
    assert instance_rows(package) == [
        {"name": "Medium", "exportable": True, "coordinates": [50.0]}
    ]


def test_ui_text_is_plain_and_includes_font_metrics():
    from examples.getgo.font_info_ui import info_text

    assert (
        info_text(
            {"family": "GG Test", "glyphs": 12, "upm": 1000, "masters": ["Regular"]}
        )
        == "GG Test\n12 glyphs | 1000 units/em\nMasters: Regular"
    )


def test_all_getgo_sources_compile_and_import_with_native_imports_blocked():
    import subprocess

    for path in sorted(GETGO.glob("*.py")):
        compile(path.read_text(), str(path), "exec")
    code = """
import importlib, importlib.abc, json, sys
from pathlib import Path
class NoHost(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'fontlab', 'fontgate', 'fontpr', 'PythonQt'}:
            raise AssertionError('Eager native import: ' + fullname)
sys.meta_path.insert(0, NoHost())
for path in Path('examples/getgo').glob('*.py'):
    importlib.import_module('examples.getgo.' + path.stem)
"""
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True)


@pytest.mark.parametrize(
    "area,closed,expected",
    [
        (10, True, "counter-clockwise"),
        (-10, True, "clockwise"),
        (0, True, "degenerate"),
        (10, False, "open"),
    ],
)
def test_direction_uses_signed_area_and_open_contour_status(area, closed, expected):
    from examples.getgo.outline_pens import direction

    assert direction(area, closed) == expected


def test_ui_handle_closes_and_deletes_its_window_only_once():
    from examples.getgo.font_info_ui import InfoTool

    calls = []
    widget = SimpleNamespace(
        close=lambda: calls.append("close"), deleteLater=lambda: calls.append("delete")
    )
    handle = InfoTool(widget, {"family": "Example"})
    handle.close()
    handle.close()
    assert calls == ["close", "delete"] and handle.widget is None


@pytest.mark.parametrize(
    "failure", [None, "body", "open", "reply", "no_document", "close"]
)
@pytest.mark.parametrize("symlinked", [False, True])
def test_owned_document_lifecycle_with_real_fixture_and_host_doubles(
    tmp_path, monkeypatch, failure, symlinked
):
    from examples.getgo import _shared

    record, source = _shared.fixture("baar")
    original = source.read_bytes()
    owned_dir = tmp_path / "working"
    owned_dir.mkdir()
    temp_dir = tmp_path / "var-link" if symlinked else owned_dir
    if symlinked:
        temp_dir.symlink_to(owned_dir, target_is_directory=True)
    monkeypatch.setattr(_shared.tempfile, "mkdtemp", lambda **kw: str(temp_dir))
    prior = SimpleNamespace(
        path=str(tmp_path / "user.vfj"),
        close=lambda save: pytest.fail("Closed user font"),
    )
    packages, closed = [prior], []

    def open_copy(name, path):
        assert name == "open_font" and Path(path).is_absolute()
        assert Path(path).read_bytes() == original

        def close(save):
            assert save is False, "Never save discarded working copies"
            if failure == "close":
                raise RuntimeError("close failure")
            closed.append(path)
            packages.remove(package)

        assert Path(path) == Path(path).resolve(), (
            "Always pass canonical /private/var paths"
        )
        package = SimpleNamespace(path=str(Path(path).resolve()), close=close)
        if failure != "no_document":
            packages.append(package)
        if failure == "open":
            raise RuntimeError("open failed after registration")
        return {"status": "error" if failure == "reply" else "ok"}

    monkeypatch.setitem(
        sys.modules,
        "fontlab",
        SimpleNamespace(
            flPackage=lambda obj: obj.package,
            flWorkspace=SimpleNamespace(
                instance=lambda: SimpleNamespace(
                    packages=lambda: [SimpleNamespace(package=p) for p in packages]
                )
            ),
        ),
    )
    monkeypatch.setitem(sys.modules, "fontpr", SimpleNamespace(call=open_copy))

    def exercise():
        with _shared.owned_font("baar") as (package, found):
            assert found == record and Path(package.path).parent == owned_dir.resolve()
            if failure == "body":
                raise RuntimeError("body failed")

    if failure:
        with pytest.raises(RuntimeError):
            exercise()
    else:
        exercise()
    assert prior in packages and source.read_bytes() == original, (
        "Keep user's font and fixture untouched"
    )
    if failure == "close":
        assert (owned_dir / source.name).is_file(), (
            "Failed close must retain the open document's bytes"
        )
    else:
        assert packages == [prior] and not owned_dir.exists()
        assert len(closed) == (0 if failure == "no_document" else 1)


def test_fixture_resolution_rejects_unknown_id_and_changed_hash(tmp_path, monkeypatch):
    from examples.getgo import _shared

    with pytest.raises(KeyError):
        _shared.fixture("not-a-getgo-font")
    (tmp_path / "manifest.json").write_text(
        json.dumps({"fonts": [{"id": "bad", "path": "bad.vfj", "sha256": "0" * 64}]})
    )
    (tmp_path / "bad.vfj").write_bytes(b"changed")
    monkeypatch.setattr(_shared, "FIXTURES", tmp_path)
    with pytest.raises(ValueError, match="hash"):
        _shared.fixture("bad")


def test_required_layer_distinguishes_missing_glyph_and_null_layer():
    from examples.getgo._shared import required_layer

    for glyph in (
        None,
        SimpleNamespace(findLayer=lambda name: None),
        SimpleNamespace(findLayer=lambda name: SimpleNamespace(isNull=True)),
    ):
        with pytest.raises(KeyError):
            required_layer(
                SimpleNamespace(
                    findName=lambda name, glyph=glyph: glyph, defaultMaster="Regular"
                ),
                "absent",
            )
    layer = SimpleNamespace(isNull=False)
    glyph = SimpleNamespace(
        findLayer=lambda master: layer if master == "Bold" else None
    )
    assert required_layer(
        SimpleNamespace(findName=lambda name: glyph), "A", "Bold"
    ) == (glyph, layer)


def test_native_rows_and_notifications_use_explicit_registered_objects(monkeypatch):
    from examples.getgo._shared import glyph_rows, notify

    layers = {
        "A": SimpleNamespace(isNull=False, anchors=[SimpleNamespace(name="top")]),
        "empty": SimpleNamespace(isNull=True),
    }
    package = SimpleNamespace(
        defaultMaster="Regular",
        fgPackage=[
            SimpleNamespace(name=n, unicodes=u) for n, u in [("A", [65]), ("empty", [])]
        ],
        findName=lambda name: SimpleNamespace(findLayer=lambda master: layers[name]),
    )
    assert glyph_rows(package) == [
        {"name": "A", "unicodes": [65], "anchors": ["top"]},
        {"name": "empty", "unicodes": [], "anchors": []},
    ]
    calls = []
    monkeypatch.setitem(
        sys.modules,
        "fontlab",
        SimpleNamespace(
            flItems=lambda: SimpleNamespace(
                notifyChangesApplied=lambda *args: calls.append(args)
            )
        ),
    )
    glyph, layer = object(), object()
    notify("Example", [(glyph, layer)])
    notify("No change", [])
    assert calls == [("Example", [layer, glyph])], (
        "Undo notifications need both layer and glyph"
    )


def test_helper_edge_cases_keep_empty_results_and_reject_invalid_inputs():
    from examples.getgo.batch_transform import transformed
    from examples.getgo.kerning_classes import summarize_kerning
    from examples.getgo.master_compatibility import compatibility
    from examples.getgo.naming import family_names
    from examples.getgo.spacing import spacing_plan

    assert not compatibility({})["compatible"]
    assert summarize_kerning([], [], [])["classes"] == []
    with pytest.raises(ValueError, match="63"):
        family_names("A" * 64, "Regular")
    with pytest.raises(ValueError):
        spacing_plan(0, float("inf"), 0, 0)
    with pytest.raises(ValueError):
        transformed([(float("nan"), 0)], 1, 0)


def binary_data():
    """A curved real pen input, not a mocked compiler or binary reader."""
    triangle = [
        ("moveTo", ((10, 0),)),
        ("lineTo", ((300, 700),)),
        ("curveTo", ((450, 700), (500, 200), (590, 0))),
        ("closePath", ()),
    ]
    return {
        "upm": 1000,
        "ascender": 800,
        "descender": -200,
        "copyright": "Example author",
        "license": "Example CC0 notice",
        "source": "https://code.fontlab.com/getgo-fonts/baar/",
        "glyphs": {
            ".notdef": {"width": 600, "unicodes": [], "recording": triangle},
            "space": {"width": 250, "unicodes": [32], "recording": []},
            "A": {"width": 600, "unicodes": [65], "recording": triangle},
        },
    }


@pytest.mark.parametrize("is_ttf", [True, False])
def test_binary_compilation_and_independent_reopen_with_real_fonttools(
    tmp_path, is_ttf
):
    pytest.importorskip("fontTools")
    from fontTools.ttLib import TTFont

    from examples.getgo._binary import compile_subset, verify_subset

    data = binary_data()
    path = tmp_path / ("sample.ttf" if is_ttf else "sample.otf")
    assert compile_subset(data, path, is_ttf) == path
    report = verify_subset(path, data, is_ttf)
    assert report["verified"] and report["bounds"]["space"] is None
    with TTFont(path) as font:
        assert font["OS/2"].fsType == 0, (
            "CC0 subset must not acquire restrictive embedding flags"
        )
        assert font["name"].getDebugName(0) == data["copyright"]
        assert data["source"] in font["name"].getDebugName(10)
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        compile_subset(data, path, is_ttf)
    assert path.read_bytes() == original
    data["glyphs"]["A"]["width"] += 1
    with pytest.raises(AssertionError, match="Advance"):
        verify_subset(path, data, is_ttf)


def test_curve_pens_measure_bezier_extrema_instead_of_control_bounds():
    pytest.importorskip("fontTools")
    from examples.getgo.outline_pens import contour_report

    def draw(pen):
        pen.moveTo((0, 0))
        pen.curveTo((0, 100), (100, 100), (100, 0))
        pen.closePath() if contour.closed else pen.endPath()

    contour = SimpleNamespace(draw=draw, closed=True, nodes=lambda: [None] * 4)
    report = contour_report(contour)
    assert report["bounds"] == [0, 0, 100, 75], "Bounds must be on the curve"
    assert report["direction"] == "clockwise" and report["points"] == 4
    contour.closed = False
    assert contour_report(contour)["signed_area"] is None


@pytest.mark.parametrize(
    "module_name,suffix", [("export_ttf", ".ttf"), ("export_otf", ".otf")]
)
def test_export_entries_close_native_input_before_real_compilation(
    tmp_path, monkeypatch, module_name, suffix
):
    pytest.importorskip("fontTools")
    import importlib
    from contextlib import contextmanager

    from examples.getgo import _binary

    events = []
    data = binary_data()

    @contextmanager
    def owned(font_id):
        assert font_id == "baar"
        events.append("open")
        try:
            yield None, None
        finally:
            events.append("close")

    compile_subset = _binary.compile_subset

    def compile_after_close(data, target, is_ttf):
        assert events == ["open", "close"], (
            "Never compile while retaining native wrappers"
        )
        return compile_subset(data, target, is_ttf)

    monkeypatch.setattr(_binary, "owned_font", owned)
    monkeypatch.setattr(_binary, "snapshot", lambda package, record: data)
    monkeypatch.setattr(_binary, "compile_subset", compile_after_close)
    result = importlib.import_module("examples.getgo." + module_name).run(
        tmp_path / ("export" + suffix)
    )
    assert result["verified"] and Path(result["path"]).is_file()
    from examples.getgo._checks import result_value

    row = next(
        row
        for row in json.loads((GETGO / "native_manifest.json").read_text())["examples"]
        if row["id"] == module_name
    )
    for check in row["expected"]:
        result_value(result, check["path"])


def test_binary_snapshot_detaches_native_outlines_and_preserves_notices(
    tmp_path, monkeypatch
):
    pytest.importorskip("fontTools")
    from fontTools.pens.recordingPen import replayRecording

    from examples.getgo import _binary

    source = binary_data()
    (tmp_path / "LICENSE.txt").write_text("Original full licence")
    monkeypatch.setattr(_binary, "FIXTURES", tmp_path)
    layers = {}
    for name, data in source["glyphs"].items():
        contours = (
            [
                SimpleNamespace(
                    closed=True,
                    draw=lambda pen, data=data: replayRecording(data["recording"], pen),
                )
            ]
            if data["recording"]
            else []
        )
        layers[name] = SimpleNamespace(
            isNull=False,
            components=[],
            advanceWidth=data["width"],
            getContours=lambda contours=contours: contours,
        )
    layers["V"] = layers["A"]
    package = SimpleNamespace(
        defaultMaster="Regular",
        info=SimpleNamespace(
            unitsPerEm=1000, ascender=800, descender=-200, copyright="Original author"
        ),
        fgPackage=[
            SimpleNamespace(name=name, unicodes=data["unicodes"])
            for name, data in source["glyphs"].items()
        ]
        + [SimpleNamespace(name="V", unicodes=[86])],
        findName=lambda name: SimpleNamespace(findLayer=lambda master: layers[name]),
    )
    result = _binary.snapshot(
        package, {"page_url": source["source"], "license_path": "LICENSE.txt"}
    )
    assert list(result["glyphs"]) == [".notdef", "space", "A", "V"]
    assert (
        result["license"] == "Original full licence"
        and result["copyright"] == "Original author"
    )
    assert result["glyphs"]["A"]["recording"] == source["glyphs"]["A"]["recording"]
    layers["A"].components = [object()]
    with pytest.raises(ValueError, match="components"):
        _binary.snapshot(
            package, {"page_url": source["source"], "license_path": "LICENSE.txt"}
        )


def test_master_report_has_design_ranges_and_locations_without_setting_master():
    from examples.getgo.designspace import masters

    axis = SimpleNamespace(
        name="Weight",
        tag="wght",
        shortName="wt",
        minimal=100,
        default=400,
        maximum=900,
        designMin=0,
        designDef=40,
        designMax=100,
        valueWeight=lambda location, fallback: location["wt"],
    )
    package = SimpleNamespace(
        masters=["Light", "Bold"],
        defaultMaster="Light",
        master="Bold",
        axes=[axis],
        location=lambda master: {"wt": {"Light": 0, "Bold": 100}[master]},
    )
    report = masters(package)
    assert report["masters"] == ["Light", "Bold"] and package.master == "Bold"
    assert report["locations"] == [
        {"master": "Light", "coordinates": [0.0]},
        {"master": "Bold", "coordinates": [100.0]},
    ]
    assert (
        report["axes"][0]["default"] == 400
        and report["axes"][0]["design_default"] == 40
    )
    assert json.loads(json.dumps(report)) == report, "Reports must be JSON serializable"
    static = SimpleNamespace(masters=["Regular"], defaultMaster="Regular", axes=[])
    assert masters(static)["locations"] == [{"master": "Regular", "coordinates": []}]


@pytest.mark.parametrize("other_path", ["/fonts/User Font.vfj", ""])
def test_mutation_guard_refuses_other_documents_before_fixture_or_temp_creation(
    monkeypatch, other_path
):
    from examples.getgo import _shared

    other = SimpleNamespace(path=other_path, name="Unsaved Font")
    workspace = SimpleNamespace(packages=lambda: [other])
    monkeypatch.setitem(
        sys.modules,
        "fontlab",
        SimpleNamespace(
            flPackage=lambda p: p,
            flWorkspace=SimpleNamespace(instance=lambda: workspace),
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "fontpr",
        SimpleNamespace(call=lambda *a, **k: pytest.fail("Must not open a copy")),
    )
    monkeypatch.setattr(
        _shared, "fixture", lambda *a: pytest.fail("Must guard before reading fixtures")
    )
    monkeypatch.setattr(
        _shared.tempfile,
        "mkdtemp",
        lambda **k: pytest.fail("Must guard before making a directory"),
    )
    with (
        pytest.raises(
            RuntimeError,
            match="no-document.*" + ("User Font" if other_path else "Unsaved Font"),
        ),
        _shared.owned_font("baar", mutates=True),
    ):
        pytest.fail("Must not yield a document")


class FakePoint:
    def __init__(self, x, y):
        self.xy = (x, y)

    def x(self):
        return self.xy[0]

    def y(self):
        return self.xy[1]


class FakeBox:
    def __init__(self, points):
        self.points = points

    def x(self):
        return min(p[0] for p in self.points)

    def width(self):
        return max(p[0] for p in self.points) - self.x()


class FakeNode:
    def __init__(self, store, index, discard=False):
        self.store, self.index, self.discard = store, index, discard
        self.xy = list(store[index])
        self.type = "on"

    @property
    def x(self):
        return self.xy[0]

    @x.setter
    def x(self, value):
        self.xy[0] = value
        if not self.discard:
            self.store[self.index][0] = value

    @property
    def y(self):
        return self.xy[1]

    @y.setter
    def y(self, value):
        self.xy[1] = value
        if not self.discard:
            self.store[self.index][1] = value


class FakeContour:
    closed = True

    def __init__(self, layer):
        self.layer = layer

    def nodes(self):
        self.layer.node_reads += 1
        return [
            FakeNode(self.layer.points, i, self.layer.discard)
            for i in range(len(self.layer.points))
        ]

    def hasIntersPoints(self, other):
        return False

    def draw(self, pen):
        pen.moveTo(tuple(self.layer.points[0]))
        for point in self.layer.points[1:]:
            pen.lineTo(tuple(point))
        pen.closePath()


class FakeLayer:
    isNull = False

    def __init__(self, left=10, right=110, width=150):
        self.components = []
        self.points = [[left, 0], [right, 0], [right, 100], [left, 100]]
        self.advanceWidth = width
        self.anchors = [
            SimpleNamespace(name="top", point=FakePoint((left + right) / 2, 100))
        ]
        self.discard, self.node_reads, self.empty = False, 0, False

    @property
    def boundingBox(self):
        assert not self.empty, (
            "Preflight must reject empty outlines before reading bounds"
        )
        return FakeBox(self.points)

    def getContours(self):
        return [] if self.empty else [FakeContour(self)]


class FakePackage:
    def __init__(self):
        self.defaultMaster, self.master = "Regular", "Bold"
        self.masters = ["Light", "Regular", "Bold"]
        self.layers = {
            name: FakeLayer()
            for name in ("A", "V", "a", "H", "I", "B", "O", "space", ".notdef")
        }
        self.layers["H"] = FakeLayer(30, 130, 180)
        self._info = SimpleNamespace(
            familyName="Original",
            styleName="Regular",
            postscriptFontName="Original-Regular",
            openTypeNamePreferredFamilyName="Original",
            openTypeNamePreferredSubfamilyName="Regular",
            copyright="Keep copyright",
            openTypeNameLicense="Keep licence",
            unitsPerEm=1000,
            ascender=800,
            descender=-200,
            xHeight=500,
            capHeight=700,
        )
        self.axes = [
            SimpleNamespace(
                name="weight",
                tag="wght",
                shortName="wt",
                minimal=100,
                default=400,
                maximum=900,
                designMin=0,
                designDef=40,
                designMax=100,
                valueWeight=lambda loc, default: loc["wt"],
            )
        ]
        self.instances = [
            SimpleNamespace(name=str(i), exportable=True, location={"wt": i * 10})
            for i in range(8)
        ]
        self.glyphsCount = len(self.layers)
        self.missing_layer = False

    @property
    def info(self):
        return self._info

    @property
    def fgPackage(self):
        return [
            SimpleNamespace(
                name=name,
                width=layer.advanceWidth,
                unicodes=[ord(name)] if len(name) == 1 else [],
            )
            for name, layer in self.layers.items()
        ]

    def findName(self, name):
        layer = self.layers.get(name)
        if layer is None:
            return None
        return SimpleNamespace(
            name=name, findLayer=lambda master: None if self.missing_layer else layer
        )

    def location(self, name):
        return {"wt": self.masters.index(name) * 50}

    def kerning(self, master):
        assert master == self.defaultMaster
        pair = SimpleNamespace(
            left=SimpleNamespace(id="A", mode="glyphMode"),
            right=SimpleNamespace(id="V", mode="glyphMode"),
        )
        return SimpleNamespace(
            items=lambda: [(pair, 0)],
            groups=SimpleNamespace(items=lambda: [("LeftA", (["A", "V"], object()))]),
        )


@pytest.fixture
def run_host(monkeypatch):
    import importlib
    from contextlib import contextmanager

    events, packages, widgets = [], {}, []

    def prepare(name, package=None, fail=False):
        module = importlib.import_module("examples.getgo." + name)
        packages[name] = package or FakePackage()

        @contextmanager
        def owned(font_id, *, mutates=False):
            events.append(("open", name, font_id, mutates))
            try:
                if fail:
                    raise RuntimeError("injected read failure")
                yield (
                    packages[name],
                    {
                        "page_url": "https://code.fontlab.com/getgo-fonts/"
                        + font_id
                        + "/"
                    },
                )
            finally:
                events.append(("close", name, font_id, mutates))

        monkeypatch.setattr(module, "owned_font", owned)
        if hasattr(module, "notify"):
            monkeypatch.setattr(
                module,
                "notify",
                lambda title, targets: events.append(("notify", name, len(targets))),
            )
        return module, packages[name]

    class Dialog:
        def __init__(self):
            self.visible, self.deleted = False, False
            widgets.append(self)

        def setWindowTitle(self, value):
            self.title = value

        def show(self):
            assert events[-1][0] == "close", (
                "The native font must close before UI display"
            )
            self.visible = True

        def close(self):
            self.visible = False

        def deleteLater(self):
            self.deleted = True

    class Layout:
        def __init__(self, parent):
            self.parent = parent

        def addWidget(self, label):
            self.parent.label = label

    class Label:
        def __init__(self, text, parent):
            self.text = text

        def setTextFormat(self, value):
            self.format = value

    qtgui = SimpleNamespace(QDialog=Dialog, QVBoxLayout=Layout, QLabel=Label)
    monkeypatch.setitem(sys.modules, "PythonQt", SimpleNamespace(QtGui=qtgui))
    monkeypatch.setitem(
        sys.modules,
        "PythonQt.QtCore",
        SimpleNamespace(QPointF=FakePoint, Qt=SimpleNamespace(PlainText=0)),
    )
    return SimpleNamespace(
        prepare=prepare, events=events, packages=packages, widgets=widgets
    )


@pytest.mark.parametrize(
    "name",
    [
        "font_audit",
        "unicode_coverage",
        "naming",
        "spacing",
        "batch_transform",
        "compare_fonts",
        "kerning_classes",
        "designspace",
        "master_compatibility",
        "font_info_ui",
        "outline_pens",
    ],
)
def test_entry_bodies_with_fresh_native_doubles_and_balanced_owned_contexts(
    run_host, monkeypatch, name
):
    from examples.getgo._checks import result_value

    module, package = run_host.prepare(name)
    if name == "font_audit":
        package.layers["A"].anchors = []
        package.layers["H"].anchors = []
    if name == "outline_pens":
        monkeypatch.setattr(
            module,
            "contour_report",
            lambda c: {
                "bounds": [0, 0, 100, 100],
                "points": 4,
                "closed": True,
                "signed_area": 10000,
                "direction": "counter-clockwise",
                "pen_protocol_verified": True,
            },
        )
    result = module.run()
    row = next(
        row
        for row in json.loads((GETGO / "native_manifest.json").read_text())["examples"]
        if row["id"] == name
    )
    for check in row["expected"]:
        result_value(
            result, check["path"]
        )  # All contract paths must be produced by real entry bodies.
    opened = [event for event in run_host.events if event[0] == "open"]
    closed = [event for event in run_host.events if event[0] == "close"]
    assert len(opened) == len(closed) == (2 if name == "compare_fonts" else 1)
    assert all(
        e[3] == (name in {"naming", "spacing", "batch_transform"}) for e in opened
    )
    if name in {"spacing", "batch_transform"}:
        assert sum(e[0] == "notify" for e in run_host.events) == 1
    if name == "batch_transform":
        assert (
            package.layers["A"].node_reads >= 2
            and result["glyphs"]["A"]["after_width"] == 165
        )
    if name == "font_info_ui":
        assert run_host.widgets[0].label.format == 0 and run_host.widgets[0].visible
        result.close()
        assert run_host.widgets[0].deleted
    else:
        json.dumps(result)  # Includes an opaque native group mode converted to text.


def test_batch_readback_rejects_wrappers_that_cache_and_discard_native_writes(run_host):
    module, package = run_host.prepare("batch_transform")
    package.layers["A"].discard = True
    with pytest.raises(AssertionError, match="coordinates"):
        module.run()
    assert run_host.events[-1][0] == "close"


@pytest.mark.parametrize("name", ["spacing", "batch_transform"])
def test_mutating_batch_preflights_all_targets_before_changing_any_node(run_host, name):
    module, package = run_host.prepare(name)
    bad = "I" if name == "spacing" else "V"
    package.layers[bad].empty = True
    before = [
        point[:] for point in package.layers["H" if name == "spacing" else "A"].points
    ]
    with pytest.raises(ValueError):
        module.run()
    assert package.layers["H" if name == "spacing" else "A"].points == before
    assert run_host.events[-1][0] == "close" and not any(
        e[0] == "notify" for e in run_host.events
    )


def test_compare_closes_first_owned_font_when_second_open_fails(run_host, monkeypatch):
    from contextlib import contextmanager

    module, _package = run_host.prepare("compare_fonts")
    original = module.owned_font

    @contextmanager
    def owned(font_id):
        if font_id == "hint":
            raise RuntimeError("second font failed")
        with original(font_id) as value:
            yield value

    monkeypatch.setattr(module, "owned_font", owned)
    with pytest.raises(RuntimeError, match="second font"):
        module.run()
    assert run_host.events[-1][0] == "close"


def test_menu_ui_is_retained_in_canonical_module_after_panel_globals_are_discarded(
    run_host, monkeypatch
):
    import runpy

    module, _package = run_host.prepare("font_info_ui")
    monkeypatch.setattr(module, "TOOL", None)
    runpy.run_path(str(GETGO / "font_info_ui.py"), run_name="__main__")
    first = module.TOOL
    assert first.widget.visible
    module.show()
    assert first.widget is None, (
        "Replacing the retained tool must close its predecessor"
    )
    module.TOOL.close()
    assert all(widget.deleted for widget in run_host.widgets)


def test_unicode_only_reader_never_fetches_layers_or_anchors():
    from examples.getgo._shared import unicodes

    package = SimpleNamespace(
        fgPackage=[SimpleNamespace(unicodes=[65, 0x1F600])],
        findName=lambda name: pytest.fail("Coverage must not look up layers"),
    )
    assert unicodes(package) == [65, 0x1F600]


def test_manifest_assertions_are_executable_and_fail_on_wrong_or_missing_values():
    from examples.getgo._checks import assert_expected

    checks = [
        {"path": ["values"], "len": 2},
        {"path": ["values"], "contains": 4},
        {"path": ["values", 0], "gt": 0},
        {"path": ["handle", "report", "ok"], "equals": True},
    ]
    assert_expected(
        {"values": [1, 4], "handle": SimpleNamespace(report={"ok": True})}, checks
    )
    with pytest.raises(AssertionError):
        assert_expected({"values": [0, 4]}, checks[:3])
    with pytest.raises(KeyError):
        assert_expected({}, checks)
    with pytest.raises(ValueError, match="Unknown"):
        assert_expected({"x": 1}, [{"path": ["x"], "unrecognized": 0}])


@pytest.mark.parametrize("is_ttf", [True, False])
def test_export_verification_detects_reversed_contours_even_when_bounds_match(
    tmp_path, is_ttf
):
    pytest.importorskip("fontTools")
    from fontTools.pens.recordingPen import RecordingPen, replayRecording
    from fontTools.pens.reverseContourPen import ReverseContourPen

    from examples.getgo._binary import compile_subset, verify_subset

    data = binary_data()
    path = tmp_path / ("winding.ttf" if is_ttf else "winding.otf")
    compile_subset(data, path, is_ttf)
    assert verify_subset(path, data, is_ttf)["winding_verified"]
    pen = RecordingPen()
    replayRecording(data["glyphs"]["A"]["recording"], ReverseContourPen(pen))
    data["glyphs"]["A"]["recording"] = pen.value
    with pytest.raises(AssertionError, match="winding"):
        verify_subset(path, data, is_ttf)


@pytest.mark.parametrize("limit,count", [(0, 0), (1, 1), (None, 2)])
def test_kerning_summary_limits_pairs_classes_and_members_but_retains_totals(
    limit, count
):
    from examples.getgo.kerning_classes import summarize_kerning

    rows = [{"left": "A", "right": "V", "value": 0}] * 2
    result = summarize_kerning(
        rows,
        [("LeftA", (["A", "V"], object())), ("Other", (["A"], 2))],
        ["A", "V"],
        limit,
    )
    assert result["pair_count"] == 2 and result["class_count"] == 2
    assert len(result["pairs"]) == len(result["classes"]) == count
    if result["classes"]:
        assert len(result["classes"][0]["members"]) == count
    json.dumps(result)
    with pytest.raises(ValueError):
        summarize_kerning([], [], [], -1)


@pytest.mark.parametrize("closed", [False, True])
def test_segment_protocol_accepts_quadratic_open_and_closed_paths_and_rejects_wrong_protocol(
    closed,
):
    pytest.importorskip("fontTools")
    from examples.getgo.outline_pens import contour_report

    def draw(pen):
        pen.moveTo((0, 0))
        pen.qCurveTo((50, 100), (100, 0))
        pen.closePath() if closed else pen.endPath()

    contour = SimpleNamespace(closed=closed, draw=draw, nodes=lambda: [None] * 3)
    result = contour_report(contour)
    assert result["pen_protocol_verified"] and result["bounds"] == [0, 0, 100, 50]
    contour.draw = lambda pen: pen.beginPath()
    with pytest.raises(RuntimeError, match="segment-pen"):
        contour_report(contour)
    contour.draw = lambda pen: pen.addComponent("A", (1, 0, 0, 1, 0, 0))
    with pytest.raises(ValueError, match="component-free"):
        contour_report(contour)


def test_compare_uses_fontgate_widths_without_layer_lookups(run_host):
    module, package = run_host.prepare("compare_fonts")
    package.findName = lambda name: pytest.fail(
        "Width comparison does not need native layer lookups"
    )
    assert "A" in module.run()["width_delta_em"]
