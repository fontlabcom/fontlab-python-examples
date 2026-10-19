# this_file: lessons/src/fontlab_python_lessons/getgo/master_compatibility.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Compare Master Topology

"""GG Plum (CC0-1.0): compare direct-contour topology across three masters.
Source font: https://code.fontlab.com/getgo-fonts/plum-var/
Original example code: Apache-2.0. Equal topology alone does not prove interpolation quality.
"""

from fontlab_python_lessons.getgo._shared import owned_font


def compatibility(signatures: dict) -> dict:
    """Distinguish missing layers from different contour/node sequences."""
    missing = [name for name, value in signatures.items() if value is None]
    values = list(signatures.values())
    return {
        "compatible": bool(values) and not missing and all(v == values[0] for v in values),
        "missing_layers": missing,
        "signatures": signatures,
    }


def run() -> dict:
    """Compare closed flags and native node types for A/V/a in each master."""
    with owned_font("plum-var") as (package, record):
        result = {}
        for name in ("A", "V", "a"):
            glyph = package.findName(name)
            signatures = {}
            for master in package.masters:
                layer = glyph.findLayer(master) if glyph is not None else None
                signatures[master] = (
                    None
                    if layer is None or layer.isNull
                    else [
                        [bool(c.closed), [n.type for n in c.nodes()]] for c in layer.getContours()
                    ]
                )
            result[name] = compatibility(signatures)
        return {"source": record["page_url"], "glyphs": result}
