# this_file: lessons/src/fontlab_python_lessons/getgo/font_audit.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Audit a Real Font

"""GG Baar (CC0-1.0): metrics, encoding collisions and chosen anchor policy.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Font notices stay with the owned copy.
"""

from fontlab_python_lessons.getgo._shared import glyph_rows, owned_font


def summarize(rows: list[dict], required: dict[str, list[str]]) -> dict:
    """Find duplicate scalar assignments and missing *requested* anchors."""
    encoded, missing = {}, {}
    for row in rows:
        for scalar in row["unicodes"]:
            encoded.setdefault(f"U+{scalar:04X}", []).append(row["name"])
        absent = sorted(set(required.get(row["name"], [])) - set(row["anchors"]))
        if absent:
            missing[row["name"]] = absent
    return {
        "glyph_count": len(rows),
        "encoded_count": len(encoded),
        "unencoded": sorted(r["name"] for r in rows if not r["unicodes"]),
        "duplicate_unicodes": {k: v for k, v in encoded.items() if len(v) > 1},
        "missing_anchors": missing,
        "anchor_count": sum(len(row["anchors"]) for row in rows),
        "glyphs_with_anchors": sum(bool(row["anchors"]) for row in rows),
    }


def run() -> dict:
    """Return JSON-friendly metrics and an explicit A/H top-anchor audit."""
    with owned_font("baar") as (package, record):
        result = summarize(glyph_rows(package), {"A": ["top"], "H": ["top"]})
        result["metrics"] = {
            key: getattr(package.info, key)
            for key in ("unitsPerEm", "ascender", "descender", "xHeight", "capHeight")
        }
        return {"source": record["page_url"], **result}
