---
this_file: src_docs/md/current/archived-recipes/batch-tools-actions-on-glyphs.md
tags: ["Archived Recipes"]
categories: ["Archived Recipes"]
---

# Batch Tools Actions on Glyphs

Launch the preserved archive entry: Batch Tools Actions on Glyphs.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/glyph_actions_batch/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Batch Tools Actions on Glyphs.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Recipes > Batch Tools Actions on Glyphs** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/b4b75a7db279fc61c0c55210ffedebd9ff9175cff1df928b0a30886a51ea8e12.py)
<!--/codeinclude-->
