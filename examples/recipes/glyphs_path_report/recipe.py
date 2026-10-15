#MenuTitle: Path Problem Report (Glyphs Script via Glyport)
# this_file: examples/recipes/glyphs_path_report/recipe.py
"""Run the Glyphs script path_report.py on the current FontLab font, unchanged.

Read-only. glyport (fontlab-glyport) supplies a ``GlyphsApp`` module backed by
FontLab. Needs fontlab-glyport installed in FontLab.
"""

from pathlib import Path


def run(font_id=None, glyph_names=None) -> dict:
    """{glyph: [problems]} for ``glyph_names`` (default: every glyph)."""
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
            script = context.import_module("path_report")
            glyphs_app = context.import_module("GlyphsApp")
        report = context.wrap(script.path_report)(glyphs_app.Glyphs.font, glyph_names)
    finally:
        context.close()
    return {"problems": report, "output": "".join(output)}


if __name__ == "__main__":
    print(run()["output"])
