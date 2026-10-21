---
this_file: src_docs/md/glyph-character-map.md
---

# Glyph Character Map

Open a FontLab font and run **Widgets → Glyph Character Map** or **Glyph
Character Map - Styles**. Both retain their complete original character picker.
The grid shows an installed **Reference Font**. It does not render the current
FontLab document's unsaved outlines.

Each cell's small corner square reports the captured FontLab font: filled blue
means covered, hollow means missing. Hover to see every matching glyph name.
The proof below the grid lists each text occurrence and its matching glyphs or
MISSING. Duplicate Unicode assignments, multiply encoded and unencoded glyphs
remain represented. The grid covers the BMP; pasted non-BMP proof text is still
checked against the full FontLab Unicode map. Missing coverage does not prevent
an otherwise valid original character selection.

The basic profile has Regular/Bold/Italic styles and a 6–72 size spin box,
initially 14. It appends at the end on any valid mouse-button click and requires
reference-font membership. The Styles profile keeps the original database
style/size lists, activated-only family/style changes, editable size Return
behaviour, red last-cell highlight and native cursor/selection insertion. Its
size list is established at opening, as in the original; changing family updates
styles without rebuilding that size list. Font merging retains its own rules.

The basic Copy button writes Clipboard; Styles writes Clipboard then Selection,
subject to the platform's Selection support. Verification uses isolated sinks.
Isolated surrogate cells cannot be inserted or copied as characters; the Styles
profile explains this original-bug correction instead of substituting text.

**Refresh FontLab coverage** atomically rereads the complete current font. It
preserves proof text and reference-font controls; failed or changing reads clear
old coverage. No font, preference, history or Output writer is used. Close,
Escape and replacement release owned signals and widgets.

Use the matching reviewed App0.2.103.dev0 candidate through Fly on FontLab9 /
Python3.11. Source and standalone Qt checks do not establish native PythonQt or
whole-font preservation acceptance; those gates remain pending.
