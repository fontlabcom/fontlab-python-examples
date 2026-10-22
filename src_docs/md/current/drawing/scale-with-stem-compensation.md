---
this_file: src_docs/md/current/drawing/scale-with-stem-compensation.md
tags: ["Drawing"]
categories: ["Drawing"]
---

# Scale With Stem Compensation

What: Scale selected glyphs with independent vertical/horizontal stem compensation.
How: Each checked master row supplies two source layers, their measured stems,
target stems, scale X/Y and slant. Unslant all nodes, blend X/Y independently,
scale and reslant. Preview lists every glyph/master and output layer. Confirm,
then Create Layers. The entire batch is recorded as one Undo step.
Why: Plain scaling changes stems. Per-master stem measurements make derived
small caps or superiors without changing the source masters.
Usage: Select glyphs in the Font window. Use Selection, check target master rows,
edit their source pairs and measurements, Preview, inspect kept rows, confirm.
Benefit: Generate many compensated glyph layers in one repeatable action.

Outputs are new auxiliary layers named master + suffix. Existing outputs are
kept. New names cannot contain @ or # or start with |temp|. No in-place overwrite
or whole-font default is provided. Preview and Apply each scan dependencies once;
control edits never scan fonts. Apply rechecks the displayed plan.
All nodes and controls use the same affine blend; TT contours remain quadratic,
including consecutive controls and implied on-curves. First-source node names,
raw flags and contour names are retained, with selection flags cleared. Advance
is first-source advance times scale X. Components, transforms, automatic or locked
sources, custom node/contour properties and unsafe automatic dependants are kept.
Anchors, guides, hints, element metadata and metrics expressions are not copied.
Source layers stay unchanged. Slant defaults to minus the current master's angle;
each table row can override it. Extrapolation, boundary-fix, stem probing and
saved table presets are not provided. Partial failures direct you to Edit > Undo.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0. Non-modal panel.

Independent behaviour rewrite of DeltaMachine.py, Vassil Kateliev / Karandash
Type Foundry, kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
The small arithmetic helper reuses the Apache-2.0 Stem Blend implementation.
No TypeRig code, private identifiers, comments or assets copied.
Capture allows 3 seconds plus one second per selected glyph/master. A timeout
refuses the whole preview; select fewer glyphs.
Read-back allows coordinate changes up to 1e-5 units. Advance is checked against
its detached value read immediately after the native setter applies the current
rounding preference, with the same tolerance. The coordinate tolerance comes
from native source; it is unmeasured in native FontLab execution.

Run **Drawing > Scale With Stem Compensation** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/043cbd001b372180c7ec0a9920d8cb7991f9d61c2ab013a4c1816ea4b91d4064.py)
<!--/codeinclude-->
