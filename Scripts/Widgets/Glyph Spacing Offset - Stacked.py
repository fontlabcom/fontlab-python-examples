# this_file: Scripts/Widgets/Glyph Spacing Offset - Stacked.py
# SPDX-License-Identifier: Apache-2.0
"""Preview a horizontal ink offset across captured selected glyph layers.

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
"""
# historical source sha256: 24312666a881173fd0a203fd1217ea8d13be8edc0e70b08628e3c4addc49cc5d


def main() -> None:
    """Open the shared App preview through Fly's lazy namespace."""
    from fly.ap.slider_spacing import show_stacked

    show_stacked()


if __name__ == "__main__":
    main()
