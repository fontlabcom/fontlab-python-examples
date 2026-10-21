---
this_file: src_docs/md/current/tools/localized-font-names.md
tags: ["Tools"]
categories: ["Tools"]
---

# Localized Font Names

What: Draft localized typographic family and subfamily names for a font build.
How: Prefill from current-master package names, with family/style fallback.
Only the current master is read; the tool never changes the active master.
Escape Windows UTF-16 name strings and export an OpenType feature fragment.
Why: Keep language-specific name IDs 16 and 17 separate from legacy names.
Usage: Refresh, enter translations and a Windows language ID, then Export New.
Include the resulting .fea in an AFDKO makeotf or fontmake feature file;
inspect the compiled
name table. This tool does not install a translation or edit the open font.
Benefit: Produce build input instead of changing global application language.
Export or explicitly discard edited translations before closing. Language IDs
are decimal or 0x-prefixed; the tool checks range, not language registration.
Syntax: https://adobe-type-tools.github.io/afdko/OpenTypeFeatureFileSpecification.html#9.e

Setup: FontLab 9, Python 3.11, Fly and App draft_signals/qt_properties.
Modeless panel; font data, selection and application preferences stay unchanged.

Independent rewrite of the Qt i18n example idea (Qt/Riverbank Computing;
Nokia Corporation). Based on the author's own FontLab sample, Apache-2.0.
Source: rescued/part3/pyqt-official-ports/ports/tools/pyqt-official/i18n-eca1cd9ef1528607.py
SHA256: a60c542ce24e27441a1c022e8fc57630edf380676eda4904bebc50510eb03047
Source: rescued/part2/ports/tools/pyqt-official/i18n-eca1cd9ef1528607.py
SHA256: 6253c957368cdf32b0a298001f6bb07cec0abc724e4f0918918facba0cde245f

Run **Tools > Localized Font Names** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/ec313369624f9aba4ac87efb86c9b1e2c833a360fb80ffa48492c7b51c8c7ada.py)
<!--/codeinclude-->
