---
this_file: src_docs/md/current/archived-launcher/archived-example-launcher.md
tags: ["Archived Launcher"]
categories: ["Archived Launcher"]
---

# Archived Example Launcher

Launch the preserved archive entry: Archived Example Launcher.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part1/launcher.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Launcher > Archived Example Launcher.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.

Run **Archived Launcher > Archived Example Launcher** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/a5f43f33ae57bae12bc38cf1bfe6c31d525cf12ec87ee282211834e0829ee982.py)
<!--/codeinclude-->
