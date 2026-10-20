---
this_file: src_docs/md/current/archived-recipes/path-problem-report.md
tags: ["Archived Recipes"]
categories: ["Archived Recipes"]
---

# Path Problem Report

Launch the preserved archive entry: Path Problem Report.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/glyphs_path_report/path_report.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Path Problem Report.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Recipes > Path Problem Report** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/965126ec1513ce56716c5f8aa15b42b7b224d16e3b39c862cac307148bc898fd.py)
<!--/codeinclude-->
