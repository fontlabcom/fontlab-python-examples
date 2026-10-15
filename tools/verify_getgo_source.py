# this_file: tools/verify_getgo_source.py
"""Verify testdata/getgo against the upstream getgo-fonts checkout.

Compares every manifest row with the source VFJ (bytes), the three licence
texts, the catalogue ``fonts.json`` (licence, copyright, links) and, with
``--online``, the public code.fontlab.com page. Prints a JSON report and exits 1
on any mismatch. Read-only on both trees.
"""

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "testdata/getgo"
LICENSE_NAMES = {"Apache": "Apache-2.0", "CC-0": "CC0-1.0", "OFL": "OFL-1.1"}
RAW = "https://raw.githubusercontent.com/fontlabcom/getgo-fonts/main/getgo-fonts/"
PAGE = "https://code.fontlab.com/getgo-fonts/{}/"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_row(row: dict, source: Path, catalogue: dict) -> list[str]:
    """Return the problems found for one manifest row (empty = verified)."""
    problems = []
    src = source / "getgo-fonts" / row["path"]
    if row["source_path"] != "getgo-fonts/" + row["path"]:
        problems.append("source_path differs from path")
    if not src.is_file():
        return problems + ["source VFJ missing"]
    if src.stat().st_size != row["bytes"] or sha256(src) != row["sha256"]:
        problems.append("source VFJ bytes differ from the manifest")
    if sha256(FIXTURES / row["path"]) != sha256(src):
        problems.append("copied VFJ differs from source")
    if not src.with_suffix(".ttf").is_file():
        problems.append("source TTF missing")
    entry = next((e for e in catalogue.values() if e["url"]["vfj"] == RAW + row["path"]), None)
    if entry is None:
        return problems + ["not listed in fonts.json"]
    if row["vfj_url"] != entry["url"]["vfj"] or row["ttf_url"] != entry["url"]["ttf"]:
        problems.append("download links differ from fonts.json")
    if LICENSE_NAMES[entry["license"]] != row["license"]:
        problems.append(f"licence {row['license']} != catalogue {entry['license']}")
    if entry["copyright"] != row["copyright"]:
        problems.append("copyright differs from fonts.json")
    if row["name"] != entry["full_name"]:
        problems.append("name differs from fonts.json")
    if row["page_url"] != PAGE.format(row["id"]):
        problems.append("page_url is not the code.fontlab.com page for the id")
    if Path(row["path"]).stem != row["id"]:
        problems.append("id differs from the VFJ file stem")
    return problems


def check_licences(source: Path, manifest: dict) -> list[str]:
    problems = []
    for row in manifest["licenses"]:
        src = source / "getgo-fonts" / row["path"]
        if not src.is_file() or sha256(src) != sha256(FIXTURES / row["path"]):
            problems.append(f"{row['path']}: licence text differs from source")
    return problems


def head(url: str) -> int:
    request = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="getgo-fonts repository root")
    parser.add_argument("--online", action="store_true", help="HEAD every public page and VFJ/TTF link")
    args = parser.parse_args()
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    catalogue = json.loads((args.source / "fonts.json").read_text())
    report = {"revision_in_manifest": manifest["source_revision"], "fonts": {}, "licenses": check_licences(args.source, manifest)}
    on_disk = {p.relative_to(args.source / "getgo-fonts").as_posix() for p in (args.source / "getgo-fonts").rglob("*.vfj")}
    report["source_vfj_not_in_manifest"] = sorted(on_disk - {r["path"] for r in manifest["fonts"]})
    report["catalogue_entries_not_in_manifest"] = len(catalogue) - len(manifest["fonts"])
    for row in manifest["fonts"]:
        problems = check_row(row, args.source, catalogue)
        if args.online:
            for key in ("page_url", "vfj_url", "ttf_url"):
                try:
                    status = head(row[key])
                except Exception as error:
                    status = f"{type(error).__name__}: {error}"
                if status != 200:
                    problems.append(f"{key} -> {status}")
        report["fonts"][row["id"]] = problems
    bad = {k: v for k, v in report["fonts"].items() if v}
    report["verified"] = len(report["fonts"]) - len(bad)
    report["problems"] = bad
    report["ok"] = not bad and not report["licenses"] and not report["source_vfj_not_in_manifest"] and report["catalogue_entries_not_in_manifest"] == 0
    print(json.dumps({k: v for k, v in report.items() if k != "fonts"}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
