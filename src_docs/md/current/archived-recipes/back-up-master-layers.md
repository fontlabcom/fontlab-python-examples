---
this_file: src_docs/md/current/archived-recipes/back-up-master-layers.md
tags: ["Archived Recipes"]
categories: ["Archived Recipes"]
---

# Back Up Master Layers

Launch the preserved archive entry: Back Up Master Layers.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/layer_backup/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Back Up Master Layers.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Recipes > Back Up Master Layers** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c0b1aa52700e8bb8351130cc87b94f223708670d2774bc232c7c34300d56908b.py)
<!--/codeinclude-->
