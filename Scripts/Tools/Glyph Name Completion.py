# this_file: Scripts/Tools/Glyph Name Completion.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: 63ef7a0c41c7c25fc66ebb8373ea523319ee9655b7995a9ed27956e30fd9b931
"""Draft text with current-font glyph-name completions.

Purpose: Adapt the complete part2 custom-completer workflow to FontLab.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.63.dev0.
Run: Open a font, run this Tools command, and type at least three characters.
Ctrl+E also offers shorter prefixes. Use Refresh after font changes.
Result: Keep every exact glyph name in the vocabulary, including unencoded and
suffixed names. Draft text and normal text copy stay local to the owned editor.
Design: Shared App completion mechanics use native Qt case-insensitive ordering,
exact QString activation, complete source-fenced reads and safe replacement.
Part2 retains alphabetic triggers, New/Close and Vocabulary. Part3 retains its
separate punctuation/modifier, focus, suffix, popup width and About/Exit policy.
Refresh errors remove old completions but keep the draft. About information is
shown in the modeless status area. A failed disconnect refuses Close for retry.
Close releases owned callbacks and models; no original body is executed.
Compatibility: Uses FontLab's supplied PythonQt. This command edits no font, selection, preference, file or Output.
Historical source: rescued/part2/ports/tools/pyqt-official/customcompleter-10ef4dacb4db4080.py
Original source/resources are archived outside this repository and are not bundled by this facade.
"""


def main() -> None:
    """Open the complete distinct owned completion policy through Fly."""
    from fly.ap.glyph_completion import show

    show()


if __name__ == "__main__":
    main()
