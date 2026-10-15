# this_file: examples/recipes/_native.py
"""Shared native driver for the recipes: owned font, fixture, run, read back, clean up.

Each recipe's ``native.py`` calls :func:`main`. It needs a FontLab session that has
no documents open (the recipes edit fonts), and Remopy on the host side:

    verification/issue-104/fl-native.sh --mutating --lane L6b -- \\
        uv run --project fontlab-remopy python \\
        fontlab-python-examples/examples/recipes/<name>/native.py [EVIDENCE.json]

The driver creates its own font, adds the fixture glyphs with FontLab's
``set_glyph`` tool, runs the recipe's ``run()`` inside FontLab (one
``run_python`` call, below the 5-second host deadline), reads the result back
independently through ``get_glyph``/``list_kerning_pairs``, closes the font
without saving and checks that no font is left behind.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fontlab_remopy import FontLab

RECIPES = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get("FONTLAB_WORKSPACE", RECIPES.parents[2]))
# Sibling checkouts the recipes may import inside FontLab (prepended to sys.path).
SOURCES = {
    "fontlabapp": Path(
        os.environ.get("FONTLABAPP_SRC", WORKSPACE / "fontlab-fontlabapp" / "src")
    ),
    "fontlab_glyport": Path(
        os.environ.get("GLYPORT_SRC", WORKSPACE / "fontlab-glyport" / "src")
    ),
}

RUN = r"""
import importlib.util, sys
for path in paths:
    if path not in sys.path:
        sys.path.insert(0, path)
for name in [m for m in sys.modules if m == module_name or m.split(".")[0] in purge]:
    del sys.modules[name]
spec = importlib.util.spec_from_file_location(module_name, recipe_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.run(font_id=font_id, **arguments)
"""


def glyph(
    name: str,
    contours: list[list[tuple[float, float]]],
    width: float = 600,
    unicode: str | None = None,
    anchors: dict[str, tuple[float, float]] | None = None,
    layer: str = "Regular",
) -> dict[str, Any]:
    """VFJ glyph JSON for ``set_glyph``: straight-line closed contours and anchors."""
    data: dict[str, Any] = {
        "name": name,
        "layers": [
            {
                "name": layer,
                "advanceWidth": width,
                "elements": [
                    {
                        "elementData": {
                            "contours": [
                                {"nodes": [f"{x:g} {y:g}" for x, y in contour]}
                                for contour in contours
                            ]
                        }
                    }
                ]
                if contours
                else [],
                "anchors": [
                    {"name": n, "point": f"{x:g} {y:g}"}
                    for n, (x, y) in (anchors or {}).items()
                ],
            }
        ],
    }
    if unicode:
        data["unicode"] = unicode
    return data


def read_layer(data: dict[str, Any], layer: str = "Regular") -> dict[str, Any]:
    """Plain contours, anchors and width of one layer from ``get_glyph`` JSON."""
    found = next(
        (item for item in data.get("layers", []) if item.get("name") == layer), None
    )
    if found is None:
        return {"exists": False}
    contours = []
    for element in found.get("elements", []):
        for contour in element.get("elementData", {}).get("contours", []):
            nodes = contour.get("nodes_list", [])
            contours.append([(float(n["x"]), float(n["y"])) for n in nodes])
    anchors = {
        a["name"]: tuple(float(v) for v in a["point"].split())
        for a in found.get("anchors", [])
    }
    return {
        "exists": True,
        "width": float(found.get("advanceWidth", 0)),
        "contours": contours,
        "anchors": anchors,
    }


def signed_area(points: list[tuple[float, float]]) -> float:
    """Shoelace area in y-up coordinates: positive means counter-clockwise."""
    return (
        sum(
            x0 * y1 - x1 * y0
            for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1])
        )
        / 2
    )


def _commit(path: Path) -> str | None:
    try:
        head = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain", "--", "."],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return head + ("+dirty" if dirty else "")


def main(
    recipe: str,
    glyphs: list[dict[str, Any]],
    arguments: dict[str, Any],
    check: Callable[..., dict[str, bool]],
    *,
    needs: tuple[str, ...] = (),
    setup: Callable[[Any, int], None] | None = None,
    read: tuple[str, ...] = (),
) -> None:
    """Run ``recipe`` on an owned font and exit 0 only when every check passes.

    ``check(report, glyphs, fl, font_id)`` gets the recipe's own report and the
    ``get_glyph`` JSON of every fixture glyph (plus ``read``), and returns named
    booleans. ``needs`` names sibling packages to put on FontLab's path.
    """
    evidence: dict[str, Any] = {
        "recipe": recipe,
        "arguments": arguments,
        "sources": {n: _commit(SOURCES[n]) for n in needs},
        "examples_commit": _commit(RECIPES),
    }
    checks: dict[str, bool] = {}
    with FontLab(timeout=30) as fl:
        before = {f["id"] for f in fl.fonts()}
        if before:
            raise SystemExit("refusing: FontLab has documents open")
        fl.new_font(family_name="Recipe " + recipe, style_name="Regular")
        font_id = next(iter({f["id"] for f in fl.fonts()} - before))
        try:
            for data in glyphs:
                fl.tool(
                    "set_glyph",
                    font_id=font_id,
                    glyph_name=data["name"],
                    glyph_data=data,
                    create=True,
                )
            if setup is not None:
                setup(fl, font_id)
            fl.activate_font(font_id=font_id)
            outcome = fl.run(
                RUN,
                paths=[str(SOURCES[n]) for n in needs],
                purge=list(needs),
                module_name="recipe_" + recipe,
                recipe_path=str(RECIPES / recipe / "recipe.py"),
                font_id=font_id,
                arguments=arguments,
            )
            evidence["report"], evidence["stdout"] = (
                outcome.value,
                outcome.stdout[-4000:],
            )
            names = [g["name"] for g in glyphs] + list(read)
            readback = {
                n: fl.tool("get_glyph", font_id=font_id, glyph_name=n) for n in names
            }
            evidence["readback"] = {n: read_layer(d) for n, d in readback.items()}
            checks.update(check(outcome.value, readback, fl, font_id))
        except Exception as error:  # noqa: BLE001 - recorded, then the font is still closed
            evidence["error"] = f"{type(error).__name__}: {error}"[:3000]
        finally:
            fl.close_font(font_id=font_id)
            checks["no_fonts_left"] = {f["id"] for f in fl.fonts()} == before
    evidence["checks"] = checks
    evidence["passed"] = (
        "error" not in evidence and bool(checks) and all(checks.values())
    )
    text = json.dumps(evidence, indent=1, ensure_ascii=False, default=str)
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(text + "\n", encoding="utf-8")
    print(text)
    sys.exit(0 if evidence["passed"] else 1)
