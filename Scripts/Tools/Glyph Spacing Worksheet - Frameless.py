# this_file: Scripts/Tools/Glyph Spacing Worksheet - Frameless.py
# SPDX-License-Identifier: Apache-2.0
"""Compare four local spacing recipes against every selected glyph-layer advance.

Purpose:
    Keep the complete preserved part3 Spin Box Delegate lesson useful in FontLab.
    A is a font-unit increment. B is its repeat count. Edit all eight cells.
Setup:
    Use FontLab 9, Python 3.11, Fly and App>=0.2.70.dev0.
    Use matching artifacts. No automatic installation is performed.
Run:
    Select glyph layers, then open this modeless worksheet from Tools.
    Edit factors even without a font. Refresh Selection reads a complete snapshot.
    Reset Factors restores original values and types. Close cancels pending input.
Result:
    Read each captured baseline and all four baseline-plus-A-times-B candidates.
    Candidates change no font metrics. Failed refresh retains the prior report.
Compatibility:
    Native PythonQt and complete font/cache/history/reopen acceptance are pending.
    Independent behavior implementation; no preserved body/helper is executed.
    Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py
"""
# historical source sha256: 3de6b2d062d29b0721bd8491772ca89bedc4dbe22680ca2af4f333ea6cfd2084


def main() -> None:
    """Open the owned App worksheet through the lazy Fly namespace."""
    from fly.ap.spacing_worksheet import show_official

    show_official()


if __name__ == "__main__":
    main()
