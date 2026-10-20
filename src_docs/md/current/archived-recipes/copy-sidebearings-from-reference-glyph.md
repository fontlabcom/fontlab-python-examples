---
this_file: src_docs/md/current/archived-recipes/copy-sidebearings-from-reference-glyph.md
tags: ["Archived Recipes"]
categories: ["Archived Recipes"]
---

# Copy Sidebearings from Reference Glyph

Launch the preserved archive entry: Copy Sidebearings from Reference Glyph.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/sidebearings_from_reference/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Copy Sidebearings from Reference Glyph.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Recipes > Copy Sidebearings from Reference Glyph** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a13c4ec9b96d4f03b1c7d93f5caaf80081ea5a593057beca4e289c298cff0751.py)
<!--/codeinclude-->
