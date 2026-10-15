# this_file: tests/test_getgo.py
"""Verify the actual licensed GetGo corpus used by the native scripting tests."""

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

ROOT = Path(__file__).resolve().parents[1] / "testdata/getgo"
MANIFEST = json.loads((ROOT / "manifest.json").read_text())


def test_getgo_manifest_covers_every_vfj_and_preserves_all_three_licences():
    expected = {row["path"] for row in MANIFEST["fonts"]}
    assert len(expected) == 99, "the complete owner-provided VFJ corpus is required"
    assert expected == {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.vfj")}
    assert {r["license"] for r in MANIFEST["fonts"]} == {"CC0-1.0", "Apache-2.0", "OFL-1.1"}
    for row in MANIFEST["licenses"]:
        body = (ROOT / row["path"]).read_bytes()
        assert hashlib.sha256(body).hexdigest() == row["sha256"], row["path"]


@pytest.mark.parametrize("row", MANIFEST["fonts"], ids=lambda r: r["id"])
def test_real_vfj_bytes_metadata_and_public_provenance_match_the_manifest(row):
    path = ROOT / row["path"]
    body = path.read_bytes()
    assert len(body) == row["bytes"], row["path"]
    assert hashlib.sha256(body).hexdigest() == row["sha256"], row["path"]
    font = json.loads(body)["font"]
    assert font["glyphs"] and len(font["glyphs"]) == row["glyphs"], row["path"]
    assert len(font["masters"]) == row["masters"], row["path"]
    assert len(font.get("axes", [])) == row["axes"], row["path"]
    assert urlparse(row["page_url"]).netloc == "code.fontlab.com", row["page_url"]
    assert row["page_url"].endswith("/getgo-fonts/" + row["id"] + "/")
    assert (ROOT / row["license_path"]).is_file(), "each font retains its licence text"
    assert row["copyright"] is not None, "retain the catalogue's original attribution"


FOLDER_LICENSE = {"apache": "Apache-2.0", "cc0": "CC0-1.0", "ofl": "OFL-1.1"}


@pytest.mark.parametrize("row", MANIFEST["fonts"], ids=lambda r: r["id"])
def test_row_licence_folder_links_and_counts_are_consistent(row):
    folder = row["path"].split("/")[0]
    assert FOLDER_LICENSE[folder] == row["license"], row["path"]
    assert row["license_path"] == folder + "/LICENSE.txt"
    raw = "https://raw.githubusercontent.com/fontlabcom/getgo-fonts/main/getgo-fonts/"
    assert row["vfj_url"] == raw + row["path"]
    assert row["ttf_url"] == raw + row["path"][:-4] + ".ttf"
    assert row["masters"] >= 1 and row["glyphs"] > 0 and row["axes"] >= 0
    assert row["axes"] > 0 or row["masters"] == 1, "several masters need at least one axis"


def test_vfj_files_are_marked_no_diff_and_fit_the_documented_size_bound():
    attributes = (ROOT.parents[1] / ".gitattributes").read_text().splitlines()
    assert "*.vfj -diff" in attributes
    assert max(r["bytes"] for r in MANIFEST["fonts"]) <= 64 * 1024 * 1024 + 1024 * 1024


def _fake_source(tmp_path, monkeypatch, row):
    """A minimal upstream tree + catalogue matching one manifest row."""
    from tools import verify_getgo_source as v

    source = tmp_path / "src"
    target = source / "getgo-fonts" / row["path"]
    target.parent.mkdir(parents=True)
    target.write_bytes((ROOT / row["path"]).read_bytes())
    target.with_suffix(".ttf").write_bytes(b"ttf")
    catalogue = {row["name"]: {"full_name": row["name"], "copyright": row["copyright"],
                               "license": {v2: k for k, v2 in v.LICENSE_NAMES.items()}[row["license"]],
                               "url": {"vfj": row["vfj_url"], "ttf": row["ttf_url"]}}}
    return v, source, catalogue


SMALL = min(MANIFEST["fonts"], key=lambda r: r["bytes"])


def test_verify_source_when_everything_matches_then_no_problems(tmp_path, monkeypatch):
    v, source, catalogue = _fake_source(tmp_path, monkeypatch, SMALL)
    assert v.check_row(SMALL, source, catalogue) == []


def test_verify_source_when_source_bytes_or_catalogue_differ_then_reports_each(tmp_path, monkeypatch):
    v, source, catalogue = _fake_source(tmp_path, monkeypatch, SMALL)
    (source / "getgo-fonts" / SMALL["path"]).write_bytes(b"{}")
    next(iter(catalogue.values()))["copyright"] = "other"
    problems = v.check_row(SMALL, source, catalogue)
    assert any("source VFJ bytes differ" in p for p in problems), problems
    assert any("copied VFJ differs" in p for p in problems), problems
    assert any("copyright" in p for p in problems), problems


def test_verify_source_when_font_missing_or_unlisted_then_reports(tmp_path, monkeypatch):
    v, source, catalogue = _fake_source(tmp_path, monkeypatch, SMALL)
    assert v.check_row(SMALL, source, {}) == ["not listed in fonts.json"]
    (source / "getgo-fonts" / SMALL["path"]).unlink()
    assert "source VFJ missing" in v.check_row(SMALL, source, catalogue)


def _driver():
    import importlib.util

    spec = importlib.util.spec_from_file_location("native_getgo_edits", ROOT.parents[1] / "tools/native_getgo_edits.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _glyph(name, unicode_="0041", **layer):
    contour = {"nodes": ["0 0", "10 0", "10 10"]}
    layer.setdefault("elements", [{"elementData": {"contours": [contour]}}])
    return {"name": name, "unicode": unicode_, "layers": [{"name": "Regular", "advanceWidth": 500, **layer}]}


def test_edit_driver_candidates_when_glyphs_are_plain_then_only_those_are_kept_with_preferred_first():
    driver = _driver()
    font = {"glyphs": [
        _glyph("b", "0062"),
        _glyph("A"),
        _glyph("composite", elements=[{"component": {"glyphName": "A"}}]),
        _glyph("transformed", elements=[{"elementData": {"contours": [{"nodes": []}]}, "transform": {"xOffset": 5}}]),
        _glyph("stroked", elements=[{"elementData": {"contours": [{"nodes": []}]}, "stroke": {"thickness": 60}}]),
        _glyph("open", elements=[{"elementData": {"contours": [{"open": True, "nodes": []}]}}]),
        _glyph("formula", metricsLeft="=H*.6"),
        _glyph("shared", elements=[{"elementData": "shared-ref"}]),
        _glyph("no-unicode", unicode_=None),
    ]}
    assert driver.candidates(font) == ["A", "b"]
    assert driver.candidates(font, strokes=True) == ["A", "b", "stroked", "open"], "strokes mode admits live strokes and open contours"


def test_edit_driver_candidates_when_real_fonts_are_static_then_a_sample_exists():
    driver = _driver()
    for ident in ("baar", "hint", "zoto-kufiarabic"):
        row = next(r for r in MANIFEST["fonts"] if r["id"] == ident)
        names = driver.candidates(json.loads((ROOT / row["path"]).read_bytes())["font"])
        assert names, f"{ident}: no plain outline glyph to edit"


def test_edit_driver_native_tail_when_output_has_blank_lines_then_last_lines_are_returned():
    driver = _driver()
    record = {"native_output": "a\n\nb\n  \nc\nd\n"}
    assert driver.native_tail(record, 2) == ["c", "d"]
    assert driver.native_tail({}) == []
