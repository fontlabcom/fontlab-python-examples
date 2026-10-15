#MenuTitle: Batch Tools Actions on Glyphs
# this_file: examples/recipes/glyph_actions_batch/recipe.py
"""Run FontLab's Tools > Actions steps on named glyphs with fontlabapp's tree.

``fontlabapp.host.glyph_actions`` lists FontLab's Actions catalogue as Python
attributes (``glyph_actions.remove_overlap``); calling one runs it through
FontLab's own ``run_actions``, with undo. ``fontlabapp.host.actions.search`` finds
the menu commands with a related name, read-only, so you can see what else the
menus offer. Needs fontlab-fontlabapp installed in FontLab.
"""

DEFAULT_STEPS = ("remove_overlap",)


def run(font_id=None, glyph_names=None, steps=DEFAULT_STEPS, layer_mode="active", search="overlap") -> dict:
    """Apply ``steps`` (Actions ids) to ``glyph_names``; returns native results."""
    if not glyph_names:
        raise ValueError("Name the glyphs to process: run(glyph_names=[...])")
    from fontlabapp import host

    known = host.glyph_actions.items()
    unknown = [step for step in steps if step not in known]
    if unknown:
        raise KeyError(f"Not in Tools > Actions: {unknown}; see dir(host.glyph_actions)")
    results = {}
    for step in steps:
        results[step] = known[step](list(glyph_names), font_id=font_id, layer_mode=layer_mode)
    related = [action.path for action in host.actions.search(search)] if search else []
    return {"steps": list(steps), "results": results, "related_menu_commands": related}


if __name__ == "__main__":
    print(run(glyph_names=["A"]))
