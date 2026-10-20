---
this_file: src_docs/md/current/archived-recipes/path-problem-report-glyphs-script-via-glyport.md
tags: ["Archived Recipes"]
categories: ["Archived Recipes"]
---

# Path Problem Report (Glyphs Script via Glyport)

Launch the preserved archive entry: Path Problem Report (Glyphs Script via Glyport).

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/glyphs_path_report/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Path Problem Report (Glyphs Script via Glyport).
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Recipes > Path Problem Report (Glyphs Script via Glyport)** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c44a8632f60cc8533935c12349047b5c0d2fbf6684c1cff1bd847d2fd3465301.py)
<!--/codeinclude-->
