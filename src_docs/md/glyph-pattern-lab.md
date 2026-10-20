---
this_file: src_docs/md/glyph-pattern-lab.md
---

# Glyph Name Pattern Lab

Author a Qt 5 pattern and inspect its captures against the current font's complete
glyph-name vocabulary. Use the results to prepare rules for another naming or
filtering tool. The laboratory edits local drafts. It applies no font changes.

Use FontLab 9, Python 3.11, Fly and reviewed unpublished App>=0.2.76.dev0. Install
matching prerequisites yourself. [The complete current source](current/tools/glyph-name-pattern-lab.md)
imports its owned App panel through Fly only when it runs.

## Author and test a rule

1. Choose **Tools > Glyph Name Pattern Lab** from Scripts.
2. Edit **Pattern** or **Test text**. Both fields are editable native combo boxes.
   Return retains the current entry in that panel's history. Closing the panel
   discards these local histories.
3. Choose **Regular expression**, **Regular expression 2**, **Wildcard** or
   **Fixed string**. Toggle **Case sensitive** and **Minimal match** independently.
4. Read the escaped pattern, position, matched length and every captured group.
   Each edit updates the complete result immediately. Group zero is the match.
5. Press **Refresh Glyph Names** to capture all names in font order. Choose a
   captured name from the adjacent list to put it into Test text. The pattern
   stays intact. Every matching glyph has its own match position, length and
   complete captures in `glyph_matches`.

The retained initial pattern is `(s\w+)`; its test text is `small stones`.
Both checkboxes start off and the first regular-expression syntax is selected.
In that configuration, the match starts at0, has length5 and captures `small`.
For glyph-name rules, try `^([A-Za-z]+)\.(.+)$` in regular-expression mode.
`A.alt` captures `A.alt`, `A` and `alt`. Fixed string treats pattern punctuation
literally. A malformed pattern has `valid: false` and Qt's native error text;
missing matches have position/length-1 and no captures, with no stale groups.

The `escaped` field is the JSON-quoted pattern literal. The surrounding report is
also JSON, so its representation quotes that literal again. Normal text selection
and manual copy are available. There is no automatic clipboard or Output action.

## Preserve the native semantics

All matching uses the host's **QRegExp**, including the two different regular-
expression modes, wildcard behavior, case folding and minimal matching. Qt's
reported positions and lengths are UTF-16 code-unit counts. A supplementary
Unicode character before a match occupies two such units. No Python `re` or
QRegularExpression substitute is used.

The original controls and outputs follow [Qt 5 QRegExp](https://doc.qt.io/qt-5/qregexp.html)
and native [editable combo-box histories](https://doc.qt.io/qt-5/qcombobox.html).
The standalone Qt 5 rehearsal is separate from actual FontLab PythonQt acceptance.

## Refresh and close

Refresh replaces the entire captured vocabulary. It keeps both authored texts,
syntax and checkboxes. A missing font, changed context, incomplete capture,
rendering failure or expired traversal clears stale font choices and reports the
failure. The local pattern/input workflow remains usable without a font.
Capture and evaluation share a two-second deadline. A Python deadline cannot
preempt a blocking native getter or regular-expression call.

**Close** fences queued slots, disconnects only the panel's own callbacks and
releases captured names and results. A failed disconnect retains the exact owner
and refuses destruction so Close can be retried. Parent destruction releases the
remaining owners without dereferencing destroyed widgets.

## Source and acceptance

The source identity is
`rescued/part2/ports/tools/pyqt-official/regexp-626fd0acec74fd91.py`, SHA256
`c45e9688f256a61cbe36eb3fd91e73750dec4f08175acda54a667db37bc8823e`.
It is the preserved Apache-2.0 clean-room replacement for specification626fd0acec74fd91,
SHA256 `f5e9501abe8d7ed6086e8979f881c79c3370c350dfa97ea3d70e9028504407fc`.
The source catalogue also retains the original pyqt/examples revision/path/hash.
There are no companion assets. NOTICE retains that complete attribution; the
existing full licences and archived metadata stay unchanged. No original body
or source helper is imported or executed.

Compiled PythonQt QRegExp return types/semantics, native signals and lifetime,
complete getter/font/cache/history/dirty/save/reopen preservation remain **native
pending**. Earlier acceptance of the archived port does not accept this new
adaptation. No native acceptance, live installation, release or publication is
implied.
