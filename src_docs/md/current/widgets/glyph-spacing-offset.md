---
this_file: src_docs/md/current/widgets/glyph-spacing-offset.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Spacing Offset

Preview a horizontal ink offset across captured selected glyph layers.

Purpose:
    Compare left+offset and right-offset sidebearings at unchanged advance.
Original profile setup:
    FontLab 9, Python3.11, Fly and App>=0.2.95.dev0. Open a font
    and select glyph layers in a Font or Glyph window. Installs nothing.
Run:
    Edit offset/minimum/maximum (-100..100), drag the slider, scrollbar or dial,
    use arrow/page/home/end keys or the wheel, change orientation and invert
    appearance or key bindings. Refresh Selection replaces all captured facts
    while preserving local controls. Close/Escape releases this owned panel.
Result:
    The live local preview lists captured and candidate geometric sidebearings
    and unchanged advance for every occurrence, including repeated layers.
    Layers without geometric bounds show unavailable margins. No font writes.
Compatibility:
    Complete distinct sliders part2 control profile. Part2 starts horizontal
    to match its label; part3 retains two stacked cyclic groups, activated-only
    orientation and independent range editors. Preview uses actual slider value.
    Bounds are geometric, not slanted metrics/keys; refresh failures clear stale
    results.
    Historical source: rescued/part2/ports/widgets/pyqt-official/sliders-36805750b888fba6.py


Setup: FontLab 9, Fly, fontlab-python-lessons and the matching App WP09
core PythonQt labs candidate.
Consolidated in Labs > Metrics Controls Lab; opens the Glyph Spacing Offset profile.

Run **Widgets > Glyph Spacing Offset** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source identity

SHA256: `3dbf80198e3a89a61080c83b8867bce0c6523a0aaf01bbd4cf2b0ac54e04294a`

[Python source at `f9d4d5f5b16f`](https://github.com/fontlabcom/fontlab-python-examples/blob/f9d4d5f5b16fcd9bcffe9cb9d08fa61d54076f3d/Scripts/Widgets/Glyph%20Spacing%20Offset.py)
