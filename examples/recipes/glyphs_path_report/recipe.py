#MenuTitle: Path Problem Report (Glyphs Script via Glyport)
# this_file: examples/recipes/glyphs_path_report/recipe.py
"""Run the Glyphs script path_report.py on the current FontLab font, unchanged.

Read-only. glyport (fontlab-glyport) supplies a ``GlyphsApp`` module backed by
FontLab. Needs fontlab-glyport installed in FontLab.
"""

from pathlib import Path


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


def run(font_id=None, glyph_names=None) -> dict:
    """{glyph: [problems]} on FontLab's current master for ``glyph_names`` (default: every glyph)."""
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
        font = glyphs_app.Glyphs.font
        report = context.wrap(script.path_report)(font, glyph_names, current_master_id(font, font_id))
    finally:
        context.close()
    return {"problems": report, "output": "".join(output)}


if __name__ == "__main__":
    print(run()["output"])
