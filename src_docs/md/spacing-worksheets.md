---
this_file: src_docs/md/spacing-worksheets.md
---

# Glyph spacing worksheets

Compare four spacing recipes with the selected glyph-layer advances. The
worksheet shows candidates. It does not apply them to a font.

Use FontLab 9, Python 3.11, Fly and `fontlab-fontlabapp>=0.2.70.dev0` artifacts. Install prerequisites yourself in
your intended environment. These scripts never install packages.

## Open and edit

1. Select glyphs in a Font window, or glyph-layer occurrences in a Glyph window.
2. Choose **Tools > Glyph Spacing Worksheet** or
   **Tools > Glyph Spacing Worksheet - Frameless** from Scripts.
3. Edit any of the eight table cells. A is an increment in font units. B is
   its repeat count. Each of the four rows computes A × B.
4. Read the selectable report. Each captured occurrence has its baseline and
   four baseline-plus-increment candidates. Repeated glyphs and mixed layers
   remain separate, in captured order.

The initial rows are `(1, 2)`, `(2, 4)`, `(3, 6)` and `(4, 8)`. They give
increments 2, 8, 18 and 32. For a baseline of 500.5, the candidates are
502.5, 508.5, 518.5 and 532.5. Zero is valid. The largest recipe is 100 × 100.

Both tables keep normal Qt selection, headers, grid, editing and stepping.
On macOS, Return starts cell editing. Double-click also starts editing.
Return commits; Tab and Backtab commit and move; Escape cancels pending text.
Focus-out, arrow keys, spin buttons, wheel and modifier stepping use the native
Qt behavior. Invalid, empty and out-of-range text uses Qt validation/correction.
No custom numeric parser is installed.

## Keep the distinct original profiles

| Policy | Glyph Spacing Worksheet | Frameless |
| --- | --- | --- |
| Original caption | Numeric cell delegate | Spin Box Delegate |
| Initial cell storage | Strings | Integers |
| Horizontal labels | Factor A / Factor B | Native numeric labels |
| Editor frame | Native framed default | False |
| Initial outer size | 640 × 460 | Native layout sizing |
| Editor initialization | Retained model, integer conversion | Index's own model |

Committing a part2 cell changes that cell to an integer. Reset restores its
original string type. The frameless profile keeps integers throughout.
Both use one real `QStyledItemDelegate`, a native `QStandardItemModel` and
transient `QSpinBox` editors with inclusive range 0 to 100.

## Refresh, reset and close

**Refresh Selection** commits acceptable pending input through the same
delegate, then stages the complete capture. It keeps the factors and current
cell. A changed context, missing font, empty selection or deadline failure keeps
the previous capture and gives a stale/error status. An unacceptable pending
editor refuses refresh and remains available to finish or cancel.

**Reset Factors** discards pending editor text and restores the eight original
values and types. It keeps the captured context. It does not reread the font.

**Close** cancels pending input and releases the owned widgets and signals.
If an owned signal cannot disconnect, Close refuses destruction and can be
retried. Return does not activate Close or Reset as a default button.

The complete table works without a font. The report explains that no selection
has been captured. No automatic clipboard, file, Output, preference, selection,
master, metrics or history writer is used. No values persist between launches.

## Source and qualification

The [framed source](current/tools/glyph-spacing-worksheet.md) and
[frameless source](current/tools/glyph-spacing-worksheet-frameless.md) pages
include the complete actual menu bodies. Each facade imports its App entry
through Fly inside `main()`. No archived source or source-relative helper runs.

The independent implementation follows the original behavior contracts for
`rescued/part2/ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py`
(SHA256 `539bd9a3542e02bafe8b89fc847c9b88277859b4e1edb9ac6624eeb7c18a7025`)
and the same filename below `rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/`
(SHA256 `3de6b2d062d29b0721bd8491772ca89bedc4dbe22680ca2af4f333ea6cfd2084`).
There are no companion assets. Original bytes are archived outside this repository.

The author supplies these first-party samples under Apache-2.0. NOTICE preserves the
complete Riverbank 2017/Nokia 2010 BSD header and the collection GPL metadata
discrepancy. The implementation does not bundle original bodies or helpers.

The selected-layer getter can call `findLayer`, which may complete an import.
A read-only width getter alone does not prove complete capture preservation.
