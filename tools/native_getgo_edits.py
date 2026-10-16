# this_file: tools/native_getgo_edits.py
"""Edit, save, reopen and export real GetGo fonts natively; then verify the artifacts.

Two steps, both through the workspace fl-native.sh guard:

    fl-native.sh --mutating --lane E1-getgo-native -- \
        uv run --project fontlab-remopy python tools/native_getgo_edits.py run --output DIR --ids ...
    uv run --no-project --with fonttools python tools/native_getgo_edits.py check DIR

``run`` works only on owned copies under DIR in a no-document session: it renames the
family, widens the sample glyph and moves its first node on every master layer, saves a
VFJ copy, reopens it, checks the edits survived and exports TTF/OTF (and variable
binaries for multi-master fonts) with the native export engine. ``check`` reads the
exports back with fontTools and compares them with the recorded edits. FontLab's
``info.familyName`` is the typographic family (name ID 16); name IDs 1/4/6 keep their
own stored values, so ``check`` asserts ID 16 and records ID 1.
"""

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "testdata/getgo"
EDIT_DX, EDIT_DY, EDIT_DW = 13, 7, 24
RESAVE_PROBE_MAX_BYTES = 20 * 1024 * 1024
PROFILES = {"ttf": 0, "otf": 1, "vf-ttf": 11, "vf-otf": 12}
DEFAULT_IDS = ("baar", "hint", "stroke-grot", "stroke-chan", "zoto-kufiarabic", "zotosans-tamil",
               "zotosans-hebrew", "plum-var", "cosm-var", "cosm-italic-var", "rafi-var", "rafi-italic-var",
               "club-var", "ptit")

NATIVE = '''
import fontlab
from PythonQt import QtCore

def call(x):
    return x() if callable(x) else x

def snapshot(pkg, sample):
    glyph = pkg.findName(sample)
    layers = {}
    for name in pkg.masters:
        layer = glyph.findLayer(name)
        if layer is None or layer.isNull:
            continue
        shapes = call(layer.shapes)
        contours = [c for s in shapes for c in call(s.contours)]
        first = call(contours[-1].nodes)[0] if contours else None
        layers[name] = {"width": layer.advanceWidth, "contours": len(contours),
                        "node": [first.x, first.y] if first is not None else None}
    return {"family": pkg.info.familyName, "glyphs": len(list(pkg.fgPackage)),
            "masters": list(pkg.masters), "unicodes": list(glyph.fgGlyph.unicodes), "layers": layers}

def package():
    p = fontlab.flWorkspace.instance().findPackageId(font_id)
    assert p is not None and not p.isNull, "document gone"
    assert str(p.path) == copy_path, "not the owned copy"
    return p

if action == "pick":
    p = package()
    best = None
    for candidate in candidates:
        glyph = p.findName(candidate)
        if glyph is None or glyph.isNull:
            continue
        ok = True
        for master in p.masters:
            layer = glyph.findLayer(master)
            # hasComposites: contours of component-built layers are derived copies,
            # so in-place node edits would be reverted (measured 2026-10-15, edits1).
            ok = ok and layer is not None and not layer.isNull and not layer.hasComposites \\
                and bool(call(layer.shapes)) and all(bool(call(s.contours)) for s in call(layer.shapes))
        if ok:
            best = candidate
            break
    result = {"sample": best}
elif action == "snapshot":
    result = snapshot(package(), sample)
elif action == "edit":
    p = package()
    before = snapshot(p, sample)
    history = [p, p.mastersContainer()]
    p.checkInitHistoryState(0)
    fontlab.flItems.notifyChangesApplied("GetGo acceptance info", history)
    p.info.familyName = family
    style = str(p.info.styleName or "Regular")
    p.info.postscriptFullName = family + " " + style  # FontLab warns when it does not start with the family
    p.info.postscriptFontName = family.replace(" ", "") + "-" + style.replace(" ", "")
    p.info.openTypeNameCompatibleFullName = family + " " + style
    fontlab.flItems.notifyChangesApplied("GetGo acceptance info", history)
    glyph = p.findName(sample)
    touched = []
    for name in p.masters:
        layer = glyph.findLayer(name)
        layer.advanceWidth = layer.advanceWidth + dw
        shapes = call(layer.shapes)
        # Last contour (an inner counter): editing the outer contour's first node of A changes the
        # auto-generated hint masters and rafi-var then fails Variable TT (probe: evidence/getgo/hint-probe).
        node = call([c for s in shapes for c in call(s.contours)][-1].nodes)[0]
        node.x = node.x + dx
        node.y = node.y + dy
        touched.append(layer)
    fontlab.flItems.notifyChangesApplied("GetGo acceptance outline", touched + [glyph])
    result = {"before": before, "after": snapshot(p, sample)}
elif action == "export":
    import builtins, time, traceback
    from PythonQt import QtCore
    p = package()
    ec = fontlab.ExportControl()
    ec.profileId = profile
    ec.destinationMode = 3
    ec.destinationFolder = folder
    ec.conflictMode = 1
    ec.contentMode = 0
    ec.groupProfiles = False
    ec.groupFamily = False
    state = {"profile": ec.profileName, "done": False, "error": None,
             "out_before": len(str(fontlab.GetProperty("output") or ""))}
    builtins._e1_export = state

    def export_later():
        # Outside run_python: its 5 s deadline would abort exports that call Python.
        start = time.time()
        try:
            fontlab.flWorkspace.instance().exportFont(p, ec)
        except BaseException:
            state["error"] = traceback.format_exc()
        state["seconds"] = round(time.time() - start, 2)
        state["done"] = True

    builtins._e1_export_cb = export_later
    QtCore.QTimer.singleShot(0, export_later)
    result = {"profile": state["profile"], "armed": True}
elif action == "export_status":
    import builtins
    state = dict(getattr(builtins, "_e1_export", {"done": None}))
    if state.get("done"):
        text = str(fontlab.GetProperty("output") or "")
        state["output"] = text[state["out_before"]:][-6000:]
    result = state
'''


def candidates(font: dict, strokes: bool = False, limit: int = 40) -> list[str]:
    """Glyphs with Unicode whose layers are plain closed contours: no components or transforms,
    and (unless ``strokes``) no live pen/stroke, whose export expands the outline."""
    def plain(layer: dict) -> bool:
        elements = layer.get("elements") or []
        # metricsLeft/metricsRight/metricsWidth expressions recompute the advance on
        # every change (measured: club-var, edits6), so edits to such layers do not stick.
        return not any(k.startswith("metrics") for k in layer) and bool(elements) and all(
            isinstance(e.get("elementData"), dict) and not ({"transform"} if strokes else {"pen", "stroke", "transform"}) & set(e)
            and e["elementData"].get("contours")
            and (strokes or not any(isinstance(c, dict) and c.get("open") for c in e["elementData"]["contours"]))
            for e in elements)

    names = [g["name"] for g in font["glyphs"]
             if g.get("unicode") and g.get("layers") and all(plain(l) for l in g["layers"] if l.get("name") != "Background")]
    first = [n for n in ("A", "alef-ar", "a", "alef-hb", "uni0627") if n in names]
    return (first + [n for n in names if n not in first])[:limit]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wait_export(native, path, font_id, limit=900.0) -> dict:
    """Poll the deferred export; the poll itself queues behind a busy host."""
    start = time.time()
    while time.time() - start < limit:
        state = native("export_status", path, font_id)
        if state.get("done"):
            return {"done": True, "seconds": state.get("seconds"), "host_error": state.get("error"),
                    "native_output": state.get("output", "")}
        time.sleep(0.5)
    return {"done": False, "error": f"export still running after {limit} s"}


def retry_busy(call, tries: int = 120, pause: float = 5.0):
    """Run a host call, waiting while FontLab reports that a save is still in progress.

    Returns a note when it had to wait (measured on boto-var, 64 MB: save_font and
    close_font both answered "A save is already in progress for this font").
    """
    for attempt in range(tries):
        try:
            call()
            return f"waited {attempt} x {pause} s for a running save" if attempt else None
        except Exception as error:
            if "save is already in progress" not in str(error):
                raise
            time.sleep(pause)
    raise TimeoutError("FontLab still reports a save in progress")


def export(native, path, font_id, directory, name, kind, output) -> dict:
    """One native export into its own folder; failures stay in the record."""
    folder = directory / name
    folder.mkdir()
    record = {"folder": str(folder.relative_to(output))}
    try:
        record.update(native("export", path, font_id, profile=PROFILES[kind], folder=str(folder)))
        record.update(wait_export(native, path, font_id))
    except Exception as error:
        record["error"] = f"{type(error).__name__}: {error}"
    record["files"] = sorted(str(p.relative_to(folder)) for p in folder.rglob("*"))
    record["name_warnings"] = [l for l in record.get("native_output", "").splitlines() if "Full name" in l or "should begin" in l]
    return record


def run_one(fl, row: dict, output: Path) -> dict:
    """Edit/save/reopen/export one font; never raises, every outcome is data."""
    item = {"id": row["id"], "license": row["license"], "page_url": row["page_url"],
            "masters": row["masters"], "axes": row["axes"], "steps": []}
    source = FIXTURES / row["path"]
    directory = output / row["id"]
    owned: set[int] = set()
    try:
        assert sha256(source) == row["sha256"], "fixture changed"
        directory.mkdir(parents=True)
        copy = directory / (row["id"] + ".vfj")
        shutil.copyfile(source, copy)

        def native(action, path, font_id, **kw):
            return fl.run(NATIVE, action=action, font_id=font_id, copy_path=str(path), **kw).value

        def open_owned(path):
            fl.open_font(path=str(path))
            opened = fl.fonts()
            assert len(opened) == 1, f"unexpected documents: {opened}"
            owned.add(opened[0]["id"])
            return opened[0]["id"]

        font_id = open_owned(copy)
        item["steps"].append("opened")
        vfj = json.loads(source.read_bytes())["font"]
        sample = native("pick", copy, font_id, candidates=candidates(vfj))["sample"]
        item["stroked"] = sample is None
        if sample is None:  # stroke fonts: the live stroke expands on export, so no node comparison
            sample = native("pick", copy, font_id, candidates=candidates(vfj, strokes=True))["sample"]
        assert sample, "no glyph with unicodes and contours on every master layer"
        item["sample"] = sample
        item["control_exports"] = {}
        if row["masters"] > 1 or row["axes"] > 0:
            for kind in ("vf-ttf", "vf-otf"):
                item["control_exports"][kind] = export(native, copy, font_id, directory, "control-" + kind, kind, output)
        family = f"GetGo Acceptance {row['id']}"
        item["family"] = family
        edit = native("edit", copy, font_id, sample=sample, family=family,
                      dx=EDIT_DX, dy=EDIT_DY, dw=EDIT_DW)
        item.update(before=edit["before"], after=edit["after"])
        for name, layer in edit["after"]["layers"].items():
            old = edit["before"]["layers"][name]
            assert layer["width"] == old["width"] + EDIT_DW, ("width", name)
            assert layer["node"] == [old["node"][0] + EDIT_DX, old["node"][1] + EDIT_DY], ("node", name)
        assert edit["after"]["family"] == family
        item["steps"].append("edited in memory")
        # Variable binaries are exported from the edited in-memory package: FontLab's VFJ writer
        # turns integer axisGraph keys back into tag IDs on re-save (fontlab/fl#8506), so a
        # saved copy of cosm fails Variable TT for a reason unrelated to the edit.
        # The saved copy is still exported below, to keep that defect on record.
        multi = row["masters"] > 1 or row["axes"] > 0
        item["exports"] = {}
        if multi:
            for kind in ("vf-ttf", "vf-otf"):
                item["exports"][kind] = export(native, copy, font_id, directory, "export-" + kind, kind, output)
                item["exports"][kind]["source"] = "edited in-memory package"
            item["steps"].append("variable exports from memory")
        saved = directory / (row["id"] + "-edited.vfj")
        item["save_note"] = retry_busy(lambda: fl.tool("save_font", font_id=font_id, path=str(saved), overwrite=True))
        assert saved.is_file() and saved.stat().st_size > 0, "save_font wrote nothing"
        item["saved_bytes"] = saved.stat().st_size
        item["steps"].append("saved copy")
        retry_busy(lambda: fl.close_font(font_id=font_id, save=False))
        owned.discard(font_id)
        font_id = open_owned(saved)
        reopened = native("snapshot", saved, font_id, sample=sample)
        assert reopened == edit["after"], "reopened VFJ differs from the edited state"
        item["reopened_equal"] = True
        item["steps"].append("reopened equal")
        for kind in ("ttf", "otf"):
            item["exports"][kind] = export(native, saved, font_id, directory, "export-" + kind, kind, output)
            item["exports"][kind]["source"] = "reopened saved copy"
        if multi and row["bytes"] <= RESAVE_PROBE_MAX_BYTES:
            # Informational, not part of ``check``: documents the re-save defect (fl#8506).
            item["resave_probe"] = export(native, saved, font_id, directory, "resaved-vf-ttf", "vf-ttf", output)
        item["steps"].append("exports attempted")
        item["native_ok"] = True
    except Exception as error:
        item.update(native_ok=False, error=f"{type(error).__name__}: {error}")
    finally:
        for font in fl.fonts():
            if font["id"] in owned:
                try:
                    retry_busy(lambda: fl.close_font(font_id=font["id"], save=False))
                except Exception as error:
                    item.setdefault("cleanup_errors", []).append(f"{type(error).__name__}: {error}")
        item["no_fonts_left"] = not fl.fonts()
        item["fixture_unchanged"] = sha256(source) == row["sha256"]
    return item


def run(args) -> int:
    from fontlab_remopy import FontLab

    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    ids = args.ids or list(DEFAULT_IDS)
    rows = {r["id"]: r for r in manifest["fonts"]}
    unknown = [i for i in ids if i not in rows]
    if unknown:
        raise SystemExit(f"unknown GetGo font IDs: {unknown}")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    receipt = output / "receipt.json"
    if receipt.exists():
        raise SystemExit("choose a new evidence directory")
    report = {"requested": ids, "results": [], "remaining": list(ids)}
    with FontLab(timeout=args.timeout) as fl:
        assert not fl.fonts(), "requires a no-document session"
        for ident in ids:
            item = run_one(fl, rows[ident], output)
            report["results"].append(item)
            report["remaining"].remove(ident)
            receipt.write_text(json.dumps(report, indent=2) + "\n")
            print(ident, "native ok" if item["native_ok"] else item["error"], flush=True)
            if not (item["no_fonts_left"] and item["fixture_unchanged"]):
                print("host state uncertain; stopping", file=sys.stderr)
                break
    report["native_ok"] = not report["remaining"] and all(r["native_ok"] for r in report["results"])
    receipt.write_text(json.dumps(report, indent=2) + "\n")
    return 0 if report["native_ok"] else 1


def outline_points(font, glyph: str) -> set[tuple[int, int]]:
    """All on/off-curve coordinates in the glyph's drawn outline (TrueType or CFF)."""
    from fontTools.pens.recordingPen import RecordingPen

    pen = RecordingPen()
    font.getGlyphSet()[glyph].draw(pen)
    return {(round(x), round(y)) for _, points in pen.value for x, y in (p for p in points if p)}


def check_static(item: dict, kind: str, path: Path) -> dict:
    """Compare a static export with the recorded edits.

    The export renames glyphs (production names), so the sample is found by its
    Unicode. A multi-master font exports an interpolated instance: its width must lie
    between the edited master widths and the exact node is not compared.
    """
    from fontTools.ttLib import TTFont

    after, before = item["after"], item["before"]
    key = next(iter(after["layers"]))
    multi = len(after["layers"]) > 1
    with TTFont(path, lazy=False) as font:
        cmap = font.getBestCmap()
        exported = cmap.get(after["unicodes"][0])
        widths = [round(v["width"]) for v in after["layers"].values()]
        advance = font["hmtx"][exported][0] if exported else None
        result = {
            "tables": sorted(font.keys()),
            "glyphs": len(font.getGlyphOrder()),
            "exported_glyph_name": exported,
            "name_id_1": font["name"].getDebugName(1),
            "name_id_16": font["name"].getDebugName(16),
            "family_ok": font["name"].getDebugName(16) == item["family"],
            "full_name_ok": (font["name"].getDebugName(4) or "").startswith(item["family"]),
            "width_ok": advance is not None and (min(widths) <= advance <= max(widths) if multi else advance == widths[0]),
            "unicode_ok": exported is not None and all(cmap.get(u) == exported for u in after["unicodes"]),
            "upm": font["head"].unitsPerEm,
            "kind_ok": ("glyf" in font) if kind == "ttf" else ("CFF " in font),
        }
        required = ["family_ok", "full_name_ok", "width_ok", "unicode_ok", "kind_ok"]
        if not multi and exported and not item.get("stroked"):
            points = outline_points(font, exported)
            result["moved_node_present"] = tuple(round(v) for v in after["layers"][key]["node"]) in points
            result["old_node_absent"] = tuple(round(v) for v in before["layers"][key]["node"]) not in points
            required += ["moved_node_present", "old_node_absent"]
    result["ok"] = all(result[k] for k in required)
    return result


def check_variable(item: dict, kind: str, path: Path) -> dict:
    from fontTools.ttLib import TTFont

    after = item["after"]
    widths = {round(v["width"]) for v in after["layers"].values()}
    with TTFont(path, lazy=False) as font:
        axes = font["fvar"].axes if "fvar" in font else []
        cmap = font.getBestCmap()
        exported = cmap.get(after["unicodes"][0])
        result = {
            "tables": sorted(font.keys()),
            "glyphs": len(font.getGlyphOrder()),
            "exported_glyph_name": exported,
            "name_id_1": font["name"].getDebugName(1),
            "name_id_16": font["name"].getDebugName(16),
            "family_ok": font["name"].getDebugName(16) == item["family"],
            "axes": [a.axisTag for a in axes],
            "axes_ok": len(axes) == item["axes"],
            "default_width_in_edited_master_widths": exported is not None and font["hmtx"][exported][0] in widths,
            "unicode_ok": exported is not None,
            "variation_tables": [t for t in ("gvar", "HVAR", "CFF2", "avar", "STAT") if t in font],
        }
    result["ok"] = all(result[k] for k in ("family_ok", "axes_ok", "default_width_in_edited_master_widths", "unicode_ok")) \
        and bool(result["variation_tables"])
    return result


def native_tail(record: dict, lines: int = 3) -> list[str]:
    """Last non-empty lines of the native Output panel text captured around an export."""
    return [l[:300] for l in record.get("native_output", "").splitlines() if l.strip()][-lines:]


def check(args) -> int:
    from fontTools.ttLib import TTFont

    directory = args.directory.resolve()
    native = json.loads((directory / "receipt.json").read_text())
    out = directory / "export-check.json"
    if out.exists():
        raise SystemExit("export-check.json exists; keep it and use a fresh run")
    report = {"results": []}
    for item in native["results"]:
        entry = {"id": item["id"], "native_ok": item["native_ok"], "kinds": {}}
        if item["native_ok"]:
            for kind, record in item["exports"].items():
                files = [directory / record["folder"] / f for f in record["files"]]
                binaries = sorted((f for f in files if f.is_file() and f.suffix in (".ttf", ".otf") and "~VF" not in str(f)),
                                  key=lambda f: ("SVG" in f.name, f.name))
                if "error" in record or record.get("host_error") or not binaries:
                    control = item.get("control_exports", {}).get(kind)
                    entry["kinds"][kind] = {
                        "ok": False, "files": record["files"],
                        "error": record.get("error") or record.get("host_error") or "no file exported",
                        "native_output_tail": native_tail(record),
                        # the same export of the unedited original fails too: not caused by the edits
                        "control_also_fails": bool(control) and not any(
                            (directory / control["folder"] / f).suffix in (".ttf", ".otf")
                            and (directory / control["folder"] / f).is_file() and "~VF" not in f
                            for f in control["files"]),
                    }
                    continue
                path = binaries[0]
                try:
                    check = (check_static if kind in ("ttf", "otf") else check_variable)(item, kind, path)
                except Exception as error:
                    check = {"ok": False, "error": f"{type(error).__name__}: {error}"}
                check.update(file=path.name, bytes=path.stat().st_size, files=record["files"])
                entry["kinds"][kind] = check
            probe = item.get("resave_probe")
            if probe:  # informational: Variable TT of the re-saved copy (fontlab/fl#8506)
                entry["resave_probe_exported"] = any(
                    f.endswith((".ttf", ".otf")) and "~VF" not in f for f in probe["files"])
                entry["resave_probe_tail"] = native_tail(probe)
            if item["id"] == "hint":
                hinting = [t for t in ("fpgm", "prep", "cvt ") if t in entry["kinds"].get("ttf", {}).get("tables", [])]
                entry["hinting_tables_in_native_ttf"] = hinting
        report["results"].append(entry)
    report["summary"] = {
        k: sum(1 for e in report["results"] if e["kinds"].get(k, {}).get("ok")) for k in PROFILES
    }
    kinds = [v for e in report["results"] for v in e["kinds"].values()]
    report["failed_kinds"] = sum(1 for v in kinds if not v["ok"])
    report["failed_but_control_also_fails"] = sum(1 for v in kinds if not v["ok"] and v.get("control_also_fails"))
    report["passed"] = all(e["native_ok"] for e in report["results"]) and not report["failed_kinds"]
    report["passed_apart_from_host_limits"] = all(e["native_ok"] for e in report["results"]) and \
        report["failed_kinds"] == report["failed_but_control_also_fails"]
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"summary": report["summary"], "passed": report["passed"]}))
    return 0 if report["passed"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("run")
    one.add_argument("--output", required=True, type=Path)
    one.add_argument("--ids", nargs="*")
    one.add_argument("--timeout", type=float, default=120, help="seconds per host call (raise for 60 MB fonts)")
    two = sub.add_parser("check")
    two.add_argument("directory", type=Path)
    args = parser.parse_args()
    return run(args) if args.command == "run" else check(args)


if __name__ == "__main__":
    raise SystemExit(main())
