# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/_binary.py
"""Standard-pen geometry subset compilation, with independent binary readback.

This intentionally omits native hints, features, kerning, axes and other layers.
FontTools imports stay lazy; a FontLab build with FontTools installed is needed
only to run the two export examples, not to import this module.
"""

import tempfile
from pathlib import Path

from examples.getgo._pens import TuplePen
from examples.getgo._shared import FIXTURES, owned_font, required_layer
from examples.getgo._winding import verify_winding

SUBSET = (".notdef", "space", "A", "V")


def snapshot(package, record: dict) -> dict:
    """Detach explicit default-master contours before closing the owned font."""
    from fontTools.pens.recordingPen import RecordingPen

    encoding = {g.name: list(g.unicodes) for g in package.fgPackage}
    glyphs = {}
    for name in SUBSET:
        _, layer = required_layer(package, name)
        if layer.components:
            raise ValueError(
                f"This direct-outline subset cannot drop components: {name}"
            )
        pen = RecordingPen()
        for contour in layer.getContours():
            if not contour.closed:
                raise ValueError(f"Binary subset needs closed contours: {name}")
            contour.draw(TuplePen(pen))
        glyphs[name] = {
            "width": round(layer.advanceWidth),
            "unicodes": encoding[name],
            "recording": pen.value,
        }
    return {
        "glyphs": glyphs,
        "upm": round(package.info.unitsPerEm),
        "ascender": round(package.info.ascender),
        "descender": round(package.info.descender),
        "copyright": package.info.copyright,
        "source": record["page_url"],
        "license": (FIXTURES / record["license_path"]).read_text(),
    }


def outline(data: dict, is_ttf: bool):
    """Build a glyph with a cubic-to-quadratic pen for TTF, or Type 2 for OTF."""
    from fontTools.pens.recordingPen import replayRecording

    if is_ttf:
        from fontTools.pens.cu2quPen import Cu2QuPen
        from fontTools.pens.ttGlyphPen import TTGlyphPen

        pen = TTGlyphPen(None)
        replayRecording(
            data["recording"], Cu2QuPen(pen, max_err=1.0, reverse_direction=True)
        )
        return pen.glyph()
    from fontTools.pens.t2CharStringPen import T2CharStringPen

    pen = T2CharStringPen(data["width"], None)
    replayRecording(data["recording"], pen)
    return pen.getCharString()


def compile_subset(data: dict, target: str | Path, is_ttf: bool) -> Path:
    """Write a new geometry subset exclusively; never overwrite an existing file."""
    from fontTools.fontBuilder import FontBuilder
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.recordingPen import replayRecording

    path = Path(target).expanduser().absolute()
    if path.suffix.lower() != (".ttf" if is_ttf else ".otf"):
        raise ValueError("Destination suffix differs from the chosen format")
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    glyphs = data["glyphs"]
    if next(iter(glyphs), None) != ".notdef":
        raise ValueError("The subset must start with .notdef")
    builder = FontBuilder(data["upm"], isTTF=is_ttf)
    builder.setupGlyphOrder(list(glyphs))
    builder.setupCharacterMap(
        {u: name for name, g in glyphs.items() for u in g["unicodes"]}
    )
    outlines = {name: outline(g, is_ttf) for name, g in glyphs.items()}
    if is_ttf:
        builder.setupGlyf(outlines)
    else:
        builder.setupCFF(
            "ScriptingSample-Regular",
            {"FullName": "Scripting Sample Regular"},
            outlines,
            {},
        )
    metrics = {}
    for name, glyph in glyphs.items():
        bounds = BoundsPen(None)
        replayRecording(glyph["recording"], bounds)
        metrics[name] = (
            glyph["width"],
            round(bounds.bounds[0]) if bounds.bounds else 0,
        )
    builder.setupHorizontalMetrics(metrics)
    builder.setupHorizontalHeader(ascent=data["ascender"], descent=data["descender"])
    builder.setupNameTable(
        {
            "familyName": "Scripting Sample",
            "styleName": "Regular",
            "psName": "ScriptingSample-Regular",
            "fullName": "Scripting Sample Regular",
            "uniqueFontIdentifier": "GetGo scripting subset 1.0",
            "version": "Version 1.0",
            "copyright": data["copyright"],
            "licenseDescription": data["license"],
            "description": "Geometry subset from " + data["source"],
        }
    )
    builder.setupOS2(
        sTypoAscender=data["ascender"],
        sTypoDescender=data["descender"],
        usWinAscent=max(0, data["ascender"]),
        usWinDescent=max(0, -data["descender"]),
        fsType=0,
    )
    builder.setupPost()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        builder.save(stream)
    return path


def verify_subset(path: str | Path, data: dict, is_ttf: bool) -> dict:
    """Reopen the actual SFNT; verify format, cmap, advances, licence and outlines."""
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.recordingPen import RecordingPen, replayRecording
    from fontTools.ttLib import TTFont

    with TTFont(path, checkChecksums=2) as font:
        glyphs = data["glyphs"]
        expected_cmap = {u: name for name, g in glyphs.items() for u in g["unicodes"]}
        expected_table = "glyf" if is_ttf else "CFF "
        if expected_table not in font or font.getGlyphOrder() != list(glyphs):
            raise AssertionError("Wrong outline format or glyph order")
        if (
            font.getBestCmap() != expected_cmap
            or font["head"].unitsPerEm != data["upm"]
        ):
            raise AssertionError("Exported Unicode coverage or UPM differs")
        if font["name"].getDebugName(13) != data["license"]:
            raise AssertionError("Exported licence differs")
        bounds, winding = {}, {}
        glyph_set = font.getGlyphSet()
        for name, source in glyphs.items():
            expected, actual = BoundsPen(None), BoundsPen(glyph_set)
            replayRecording(source["recording"], expected)
            glyph_set[name].draw(actual)
            recording = RecordingPen()
            glyph_set[name].draw(recording)
            winding[name] = verify_winding(source["recording"], recording.value, is_ttf)
            if font["hmtx"][name][0] != source["width"]:
                raise AssertionError(f"Advance differs: {name}")
            if (expected.bounds is None) != (actual.bounds is None):
                raise AssertionError(f"Empty/nonempty outline differs: {name}")
            if expected.bounds and any(
                abs(a - b) > 2.0 for a, b in zip(expected.bounds, actual.bounds)
            ):
                raise AssertionError(f"Outline bounds differ: {name}")
            bounds[name] = list(actual.bounds) if actual.bounds else None
        return {
            "path": str(Path(path).absolute()),
            "format": expected_table.strip(),
            "glyphs": list(glyphs),
            "cmap": {str(k): v for k, v in expected_cmap.items()},
            "upm": font["head"].unitsPerEm,
            "bounds": bounds,
            "winding": winding,
            "winding_verified": True,
            "verified": True,
        }


def export_subset(target: str | Path | None, is_ttf: bool) -> dict:
    """Read GG Baar in FontLab, close it, then compile and reopen its subset."""
    with owned_font("baar") as (package, record):
        data = snapshot(package, record)
    if target is None:
        target = Path(tempfile.mkdtemp(prefix="getgo-export-")) / (
            "sample.ttf" if is_ttf else "sample.otf"
        )
    path = compile_subset(data, target, is_ttf)
    return {"source": data["source"], **verify_subset(path, data, is_ttf)}
