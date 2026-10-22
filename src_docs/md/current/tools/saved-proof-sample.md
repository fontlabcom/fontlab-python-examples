---
this_file: src_docs/md/current/tools/saved-proof-sample.md
tags: ["Tools"]
categories: ["Tools"]
---

# Saved Proof Sample

Keep a reusable proof sample and check it against the current font.

What: Save one proof string in an isolated example settings namespace.
How: QSettings stores only proof/sample. Check Coverage reads the full current
font catalogue with a glyph-count-scaled scan deadline capped at 120 seconds
and a Scanning label.
It reports covered and missing Unicode scalars as JSON.
Why: Persist a personal proof across launches and fonts in this tool's own
settings namespace. Coverage and clipboard output make that saved proof useful.
Usage: Edit the sample, Save Sample, Check Coverage, or Copy Proof Text to paste
in FontLab. Reset Saved Sample removes only this tool's key. Unsaved typing is
not persisted; Save Sample is explicit. Coverage always captures the font again.
Benefit: Keep a stable personal proof and compare encoding coverage across fonts.
No font or selection changes occur. Unicode coverage is not shaping coverage.
NUL and input-method transfer have known loss (fl#8567, fl#8568). This example
also conservatively refuses NBSP, U+2028/U+2029 and lone surrogates; it requires
exact proof text. This is a transfer policy, not a Unicode coverage limitation.
Setup: FontLab 9, Python 3.11, Fly, App glyph_catalog and draft_signals.
Independent rewrite of sandbox-settings.
Based on the author's own FontLab sample, Apache-2.0. No original source body is redistributed.

Run **Tools > Saved Proof Sample** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/d4429b50e714851f2bb846dde20dcef1357bad3505a4dd63a9a53fc62ab4acf6.py)
<!--/codeinclude-->
