# this_file: Scripts/Tools/Glyph Name Completion with Focus.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 05e5a74c23f345163374d8b557dc116b93245f46e6557f1e78efb0a7a9150094
"""Draft text with current-font glyph-name completions.

Purpose: Adapt the complete part3 custom-completer workflow to FontLab.
Setup: FontLab 9, Python 3.11, Fly and reviewed unpublished App>=0.2.63.dev0.
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
Compatibility: Actual PythonQt/font/cache/history/dirty/save/reopen acceptance
is pending D25. This command edits no font, selection, preference, file or Output.
Original: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/customcompleter-10ef4dacb4db4080.py
Original source/resources stay preserved and are not bundled by this facade.
"""


def main() -> None:
    """Open the complete distinct owned completion policy through Fly."""
    from fly.ap.glyph_completion import show_official

    show_official()


if __name__ == "__main__":
    main()
