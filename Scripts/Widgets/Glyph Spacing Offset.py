# this_file: Scripts/Widgets/Glyph Spacing Offset.py
# SPDX-License-Identifier: Apache-2.0
"""Preview a horizontal ink offset across captured selected glyph layers.

Purpose:
    Compare left+offset and right-offset sidebearings at unchanged advance.
Setup:
    FontLab 9, Python3.11, Fly and reviewed App>=0.2.95.dev0. Open a font
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
    results. Native PythonQt and getter/cache preservation remain pending.
    Source: rescued/part2/ports/widgets/pyqt-official/sliders-36805750b888fba6.py
"""
# preserved-source-sha256: aa662a1158ce7f691d467ef90974895e39ef05ce33098ac7072b7cca5efbad56


def main() -> None:
    """Open the shared App preview through Fly's lazy namespace."""
    from fly.ap.slider_spacing import show

    show()


if __name__ == "__main__":
    main()
