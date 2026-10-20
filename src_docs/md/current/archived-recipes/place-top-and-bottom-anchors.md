---
this_file: src_docs/md/current/archived-recipes/place-top-and-bottom-anchors.md
tags: ["Archived Recipes"]
categories: ["Archived Recipes"]
---

# Place Top and Bottom Anchors

Launch the preserved archive entry: Place Top and Bottom Anchors.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/anchors_from_bounds/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Place Top and Bottom Anchors.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Recipes > Place Top and Bottom Anchors** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/5c970cb583cf24f8fe57a47fb6ce569899f5be59c87b51a3ca44fe717253b9f4.py)
<!--/codeinclude-->
