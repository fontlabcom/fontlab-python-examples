# this_file: tools/native_getgo.py
"""Open real GetGo copies and verify native FontParts/point-pen readback.

Run through the workspace fl-native.sh --mutating guard. This driver never saves
over testdata. Each font has a separate owned document and durable receipt.
"""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from fontlab_remopy import FontLab

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "testdata/getgo"
READ = '''
import sys
saved = sys.path[:]
try:
    sys.path[:0] = [site]
    for key in list(sys.modules):
        if key == "fontlab_fontport" or key.startswith("fontlab_fontport."):
            del sys.modules[key]
    import fontlab, fontlab_fontport.host as host
    from fontlab_fontport.live import RFont
    from fontTools.pens.recordingPen import RecordingPointPen
    import hashlib, json, math
    from pathlib import Path
    assert host.__file__.startswith(site + "/"), host.__file__
    backend = host.NativeFontBackend(font_id)
    p = backend._package()
    assert Path(p.path).resolve() == Path(copy_path).resolve(), "not the owned fixture copy"
    native_names = [g.name for g in p.fgPackage]
    masters = list(p.masters)
    assert set(masters) == set(expected_masters), (masters, expected_masters)
    assert len(native_names) == expected_glyphs, (len(native_names), expected_glyphs)
    layer = backend.default_layer()
    native = p.findName(sample).findLayer(layer)
    if native is None or native.isNull:
        layer = next(x.name for x in p.findName(sample).layers)
        native = p.findName(sample).findLayer(layer)
    glyph = backend.read_glyph(sample, layer)
    pen = RecordingPointPen()
    glyph.drawPoints(pen)
    assert glyph.width == native.advanceWidth, "native width differs from point-pen model"
    assert math.isfinite(glyph.width)
    for operation, arguments, keywords in pen.value:
        if operation == "addPoint":
            assert all(math.isfinite(n) for n in arguments[0]), "nonfinite outline point"
    font = RFont(backend)
    assert font.info.unitsPerEm == p.info.unitsPerEm
    result = {"fontport_origin":host.__file__, "family":p.info.familyName,
              "glyphs":len(native_names), "masters":masters, "sample":sample,
              "layer":layer, "width":glyph.width, "pen_operations":len(pen.value),
              "point_pen_sha256":hashlib.sha256(json.dumps(pen.value,sort_keys=True).encode()).hexdigest(),
              "upm":font.info.unitsPerEm}
finally:
    sys.path[:] = saved
'''


def main() -> int:
    """Keep all requested fonts in the denominator; stop only when host state is uncertain."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fontport-site", required=True, type=Path)
    parser.add_argument("--ids", nargs="*")
    args = parser.parse_args()
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    selected = set(args.ids or [r["id"] for r in manifest["fonts"]])
    rows = [r for r in manifest["fonts"] if r["id"] in selected]
    if selected != {r["id"] for r in rows}:
        parser.error("unknown GetGo font ID")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if (output / "receipt.json").exists():
        parser.error("choose a new evidence directory")
    report = {"requested":len(rows), "results":[], "remaining":[r["id"] for r in rows]}
    with FontLab(timeout=60) as fl:
        assert not fl.fonts(), "requires a no-document session"
        for row in rows:
            item, owned = {"id":row["id"], "source_sha256":row["sha256"], "page_url":row["page_url"]}, set()
            source = FIXTURES / row["path"]
            target = output / (row["id"] + ".vfj")
            try:
                body = source.read_bytes()
                assert hashlib.sha256(body).hexdigest() == row["sha256"], "fixture changed"
                font = json.loads(body)["font"]
                names = [g["name"] for g in font["glyphs"]]
                sample = next((n for n in ("A","a","uni0627","alef-ar") if n in names), None)
                if sample is None:
                    sample = next((g["name"] for g in font["glyphs"] if any(layer.get("elements") for layer in g.get("layers",[]))), names[0])
                shutil.copyfile(source, target)
                fl.open_font(path=str(target))
                opened = fl.fonts()
                assert len(opened) == 1, "unexpected document opened during the fixture run"
                font_id = opened[0]["id"]
                owned.add(font_id)
                item["native"] = fl.run(READ, site=str(args.fontport_site.resolve()), font_id=font_id,
                                        copy_path=str(target), sample=sample, expected_glyphs=row["glyphs"],
                                        expected_masters=[m["fontMaster"]["name"] for m in font["masters"]]).value
                item["passed"] = True
            except Exception as error:
                item.update(passed=False, error=f"{type(error).__name__}: {error}")
            finally:
                for opened in fl.fonts():
                    if opened["id"] in owned:
                        fl.close_font(font_id=opened["id"])
                item["no_fonts_left"] = not fl.fonts()
                item["fixture_unchanged"] = hashlib.sha256(source.read_bytes()).hexdigest() == row["sha256"]
                item["passed"] = item.get("passed",False) and item["no_fonts_left"] and item["fixture_unchanged"]
                report["results"].append(item)
                report["remaining"].remove(row["id"])
                report["passed"] = not report["remaining"] and all(x["passed"] for x in report["results"])
                (output / "receipt.json").write_text(json.dumps(report,indent=2)+"\n")
                print(row["id"],"PASS" if item["passed"] else item.get("error","FAIL"),flush=True)
            if not (item["no_fonts_left"] and item["fixture_unchanged"]):
                break  # a failure alone is kept and the run goes on; uncertain host state stops it
    return 0 if report.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
