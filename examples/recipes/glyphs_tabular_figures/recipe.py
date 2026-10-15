#MenuTitle: Tabular Figures (Glyphs Script via Glyport)
# this_file: examples/recipes/glyphs_tabular_figures/recipe.py
"""Run the Glyphs script tabular_figures.py on the current FontLab font, unchanged.

glyport (fontlab-glyport) supplies a ``GlyphsApp`` module backed by FontLab, so
the script's ``font.glyphs[...]``, ``layer.paths`` and ``layer.width`` work on
FontLab glyphs. Needs fontlab-glyport installed in FontLab.
"""

from pathlib import Path

FIGURES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")


def run(font_id=None, glyph_names=None, width=600) -> dict:
    """Centre figures (default: zero..nine present in the font) in ``width``."""
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
        names = glyph_names or [n for n in FIGURES if font.glyphs[n] is not None]
        shifts = context.wrap(script.tabular_figures)(font, names, width)
    finally:
        context.close()
    return {"width": width, "shifts": shifts, "output": "".join(output)}


if __name__ == "__main__":
    print(run())
