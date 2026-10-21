# this_file: Scripts/Tools/Glyph Name Pattern Lab.py
# SPDX-License-Identifier: Apache-2.0
"""Author native Qt 5 patterns against complete captured FontLab glyph names.

Purpose:
    Keep the complete Pattern Matching Inspector useful for glyph-name rules.
    Test captures, positions and lengths before using a pattern in another tool.
Setup:
    Use FontLab 9, Python 3.11, Fly and App>=0.2.76.dev0.
    Install the prerequisites yourself. This script installs nothing.
Run:
    Open this modeless lab from Tools. Edit the pattern and test-text histories.
    Choose Regular expression, Regular expression 2, Wildcard or Fixed string.
    Toggle case sensitivity or minimal matching. Every edit updates the result.
    Refresh Glyph Names captures the complete current-font vocabulary.
    Choose a captured name to use it as test text; both authored drafts survive Refresh.
Result:
    Inspect the escaped pattern, native position/length and every capture.
    Inspect all matching captured glyph names and their individual captures.
    Positions and lengths use Qt UTF-16 units. The lab changes no font data.
Compatibility:
    Native PythonQt, complete getter/cache/history/dirty/reopen acceptance pending.
    Independent implementation; no original body or source helper is executed.
    Preserved source: rescued/part2/ports/tools/pyqt-official/regexp-626fd0acec74fd91.py
"""
# preserved-source-sha256: c45e9688f256a61cbe36eb3fd91e73750dec4f08175acda54a667db37bc8823e


def main() -> None:
    """Open the owned pattern laboratory through the lazy Fly namespace."""
    from fly.ap.glyph_pattern import show

    show()


if __name__ == "__main__":
    main()
