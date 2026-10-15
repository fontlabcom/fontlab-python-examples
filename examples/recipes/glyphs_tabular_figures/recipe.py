#MenuTitle: Tabular Figures (Glyphs Script via Glyport)
# this_file: examples/recipes/glyphs_tabular_figures/recipe.py
"""Run the Glyphs script tabular_figures.py on the current FontLab font, unchanged.

glyport (fontlab-glyport) supplies a ``GlyphsApp`` module backed by FontLab, so
the script's ``font.glyphs[...]``, ``layer.paths`` and ``layer.width`` work on
FontLab glyphs. Needs fontlab-glyport installed in FontLab.
"""

from pathlib import Path

FIGURES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def current_master_id(font, font_id):
    """glyport master id of FontLab's current master (by name) for this font."""
    import fontlab
    import fontpr

    if font_id is None:
        font_id = fontpr.call("get_active_font")["id"]
    name = fontlab.flWorkspace.instance().findPackageId(font_id).master
    found = [m.id for m in font.masters if m.name == name]
    if len(found) != 1:
        raise LookupError(f"FontLab master {name!r} not found once among {[m.name for m in font.masters]}")
    return found[0]


def run(font_id=None, glyph_names=None, width=600) -> dict:
    """Centre figures on FontLab's current master (default: zero..nine present in
    the font; an empty list does nothing) in ``width``."""
    import fontpr
    from fontlab_glyport import ExecutionContext
    from fontlab_glyport.glyphsapp.fontlab_bridge import fontlab_glyphsapp_provider

    if font_id is not None:  # Glyphs.font is FontLab's current font
        fontpr.call("set_active_font", font_id=font_id)
    output = []
    context = ExecutionContext(Path(__file__).parent, "glyphs3", sink=output.append)
    context.adapters["GlyphsApp"] = fontlab_glyphsapp_provider(context, version=(3.2, 3234.0))
    try:
        with context:
            script = context.import_module("tabular_figures")
            glyphs_app = context.import_module("GlyphsApp")
        font = glyphs_app.Glyphs.font
        if glyph_names is None:
            names = [n for n in FIGURES if font.glyphs[n] is not None]
        else:
            names = list(glyph_names)
        master = current_master_id(font, font_id)
        shifts = context.wrap(script.tabular_figures)(font, names, width, master)
    finally:
        context.close()
    return {"width": width, "shifts": shifts, "output": "".join(output)}


# Menu use: name the figures, then run the script. Nothing happens while GLYPHS is empty.
GLYPHS = []  # e.g. list(FIGURES)
WIDTH = 600

if __name__ == "__main__":
    if GLYPHS:
        print(run(glyph_names=GLYPHS, width=WIDTH))
    else:
        print("Tabular Figures: set GLYPHS (and WIDTH) at the end of this script first.")
