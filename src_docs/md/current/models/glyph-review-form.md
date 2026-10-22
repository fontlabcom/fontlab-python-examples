---
this_file: src_docs/md/current/models/glyph-review-form.md
tags: ["Models"]
categories: ["Models"]
---

# Glyph Review Form

What: Save a review state and note in the current font's native glyph notes.
How: Map an Unset/Todo/Review/Done combo and a literal note field to one table
row with
QDataWidgetMapper. Apply submits only that row, checks the captured glyph id
and original note, then commits metadata through App history.commit.
Why: Native notes travel with the font; existing free-form notes stay intact
until the user explicitly applies a review state. Auto-layer glyphs are
refused.
Usage: Choose a row, select its state, enter a note and click Apply. Apply or
Discard Changes before switching rows or closing. Each Apply is one Undo step.
Benefit: Keep review decisions with the glyphs rather than in a separate draft.
Requires: FontLab 9, Python 3.11, Fly and App names_edit, history,
draft_signals
and qt_properties. Native read-back failures show the Edit > Undo recovery.

Independent rewrite of the Qt simplewidgetmapper and combowidgetmapper example
idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py
SHA256: b6cda27a2fdd03bd8cbfe3604df3e2b4e7f89dbb378d331ba8465d57291902c7
Historical source: rescued/part2/ports/itemviews/pyqt-official/simplewidgetmapper-39de33366209402d.py
SHA256: 610a6d9f48c31599b43c8bd5eecf4686d6cfd5e2915c8cd76d91a65b3248f1a9
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simplewidgetmapper-39de33366209402d.py
SHA256: fae480ee8369b1fd438007ad15563eacaa22313496ffff7bebd93cb574840ae9
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py
SHA256: 741f446ef14303840be12852cc2b9383eb5ccd716c894ebff21dfc95aa6d44d9

Run **Models > Glyph Review Form** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/673a69429e2fb3a204498657abb5c22f4513ef8ffa7c5a728e712501162fd19f.py)
<!--/codeinclude-->
