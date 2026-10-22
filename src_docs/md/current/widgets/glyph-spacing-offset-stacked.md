---
this_file: src_docs/md/current/widgets/glyph-spacing-offset-stacked.md
tags: ["Widgets"]
categories: ["Widgets"]
---

# Glyph Spacing Offset - Stacked

Preview a horizontal ink offset across captured selected glyph layers.

Purpose:
    Compare left+offset and right-offset sidebearings at unchanged advance.
Setup:
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
    Complete distinct sliders part3 control profile. Part2 starts horizontal
    to match its label; part3 retains two stacked cyclic groups, activated-only
    orientation and independent range editors. Preview uses actual slider value.
    Bounds are geometric, not slanted metrics/keys; refresh failures clear stale
    results.
    Historical source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/sliders-36805750b888fba6.py

Run **Widgets > Glyph Spacing Offset - Stacked** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/245041a889a0ab50a97d7d40f1c1114b0cd17693ebd139082a42fedeafde3a5d.py)
<!--/codeinclude-->
