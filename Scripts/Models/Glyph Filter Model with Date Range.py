# this_file: Scripts/Models/Glyph Filter Model with Date Range.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: a844adb5f7888373586f0e37f81025d991c19b96d5e205fdd376258a712c6e2d
"""Inspect and filter whole-font glyph metadata with typed Qt dates.

Purpose: Adapt the complete part3 official custom source/proxy model lesson.
Show every glyph name, all Unicode assignments and local modification datetimes.
Both read-only views share one captured model with native QDateTime cells.
Setup: FontLab9 Python3.11, fontlab-fly and reviewed unpublished App>=0.2.55.dev0.
Run: Open a font and run this Models command. Use regular expressions, wildcards
or fixed strings, and click result headers to sort.
Match either name or Unicode with Qt QRegExp, then optionally limit inclusive calendar days. Text sorting stays case-sensitive; email-shaped values use the original extracted-token comparator.
Result: Complete captured glyph metadata replaces the demonstration mail data.
Refresh reads the current font again. Empty, stale, unreadable or expired reads
clear both views and diagnose; cells never edit the font. Close releases models,
virtual callbacks, captured data and signals. No selection/history/preferences
or Output writer is called.
Compatibility: Native PythonQt dispatch, metadata/getter/cache/font/history and
complete persistence/UI acceptance remain pending. Standalone Qt is not native
FontLab proof. This replaces one preserved-source dispatcher; its original bytes
remain external and are never executed by this adaptation.

Original: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py
The two part2 workflows retain their separate Python matching/string-date rules.
Demo-specific text and2006/2007date defaults become a complete font snapshot with
empty initial pattern and optional observed date limits. Shared policy lives in App.
"""


def main() -> None:
    """Open the complete owned workflow through the lazy Fly namespace."""
    from fly.ap.glyph_catalog import show_official_custom

    show_official_custom()


if __name__ == "__main__":
    main()
