# this_file: lessons/src/fontlab_python_lessons/getgo/kerning_classes.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Kerning and Classes Report

"""GG Stroke Chan OFL Italic (OFL-1.1): inspect typed pairs and group members.
Source font: https://code.fontlab.com/getgo-fonts/stroke-chan/
Original example code: Apache-2.0. No class expansion or renaming is performed.
"""

from fontlab_python_lessons.getgo._shared import owned_font


def summarize_kerning(
    pairs: list[dict],
    groups: list,
    glyph_names: list[str],
    limit: int | None = 5,
) -> dict:
    """Keep pair modes and explicit zero values; identify dangling group members."""
    if limit is not None and (type(limit) is not int or limit < 0):
        msg = "limit must be a nonnegative integer or None"
        raise ValueError(msg)
    names = set(glyph_names)
    classes = [
        {"name": str(name), "members": list(members), "mode": str(mode)}
        for name, (members, mode) in groups
    ]
    missing = {g["name"]: sorted(set(g["members"]) - names) for g in classes}
    return {
        "pair_count": len(pairs),
        "class_count": len(classes),
        "pairs": pairs[:limit],
        "classes": [
            {**g, "members": g["members"][:limit], "member_count": len(g["members"])}
            for g in classes[:limit]
        ],
        "limit": limit,
        "missing_members": {name: members for name, members in missing.items() if members},
    }


def run(limit: int | None = 5) -> dict:
    """Summarize kerning; pass limit=None for complete pair/class/member lists."""
    summarize_kerning([], [], [], limit)
    with owned_font("stroke-chan") as (package, record):
        kerning = package.kerning(package.defaultMaster)
        pairs = [
            {
                "left": pair.left.id,
                "right": pair.right.id,
                "value": float(value),
                "left_mode": str(pair.left.mode),
                "right_mode": str(pair.right.mode),
            }
            for pair, value in kerning.items()
        ]
        result = summarize_kerning(
            pairs,
            list(kerning.groups.items()),
            [g.name for g in package.fgPackage],
            limit,
        )
        return {"source": record["page_url"], "master": package.defaultMaster, **result}
