---
this_file: lessons/src/fontlab_python_lessons/getgo/README.md
---

# GetGo font lessons

These 13 packaged lessons use real licensed fonts and retain the original
algorithms, defaults, font operations and temporary-copy cleanup. The complete
99-font GetGo fixture collection, its original manifest and license texts ship
in data beside the Python modules. No rescued directory is needed at runtime.
Native acceptance of this packaged adaptation is **pending**. Historical9783
receipts in historical-native.json describe the old source only.

Install the lessons and the matching Fly/App packages in FontLab9/Python3.11.
The reports API requires the unreleased App0.2.26.dev0 candidate or its later
release; App0.2.22 lacks it. Pen and export lessons additionally require the
fonttools extra. This candidate must be reviewed/released before normal use.
Choose a GetGo Fonts menu entry. Twelve dictionary lessons show a detached,
nonmodal plain-text JSON report with source links and calculated results.
Font Info Mini Tool returns its retained InfoTool, with report/widget/close.
Close releases owned callbacks. Running the same entry replaces its own window.
The active font and Output panel are not report destinations.

Each native operation opens a SHA-256-verified fixture as an absolute temporary
copy and closes only its exact package through fontpr, including partial-open
failures. Mutation lessons naming/spacing/batch_transform require a dedicated
no-document FontLab session and discard their edits. A failed close retains the
temporary directory and raises. Never run these mutations in an owner session.
Export paths must be new, use the chosen .ttf/.otf suffix and are retained.
Default exports use a newly created temporary directory and report its path.

For scripting, call `from fontlab_python_lessons.getgo import launch` followed
by `handle = launch("font_audit")`, then `handle.close()` when done. To consume
a dictionary without a window, import an entry module and call its original
`run(**kwargs)`. Parameters and defaults are documented below. Errors propagate;
there is no silent no-op or alternate algorithm.

## font_audit

GG Baar (CC0-1.0): metrics, encoding collisions and chosen anchor policy.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Font notices stay with the owned copy.

Original call: `run() -> dict`.

Expected output and limits: glyph_count equals manifest glyphs (96) metrics.unitsPerEm is positive missing_anchors follows explicit A/H top-anchor policy

Fixtures: `baar`. Changes owned copy: false. Additional dependencies: none.

## unicode_coverage

Zoto Kufi Arabic (Apache-2.0): check a short text's Unicode coverage.
Source font: https://code.fontlab.com/getgo-fonts/zoto-kufiarabic/
Original example code: Apache-2.0. Coverage does not test Arabic shaping.

Original call: `run(text: str='مرحبا بالعالم 123') -> dict`.

Expected output and limits: covered contains U+0627 for the default Arabic sample covered and missing are disjoint; their union equals distinct sample scalars

Fixtures: `zoto-kufiarabic`. Changes owned copy: false. Additional dependencies: none.

## outline_pens

GG Hint (Apache-2.0): exact curve bounds, signed areas and point counts.
Source font: https://code.fontlab.com/getgo-fonts/hint/
Original example code: Apache-2.0. Intersections are boundary tests, not boolean overlap.

Original call: `run() -> dict`.

Expected output and limits: A/B/O each report nonempty contours and positive point counts bounds contain four finite numbers closed directions agree with signed_area; intersections list valid contour indices

Fixtures: `hint`. Changes owned copy: false. Additional dependencies: fontTools.

## naming

GG Baar (CC0-1.0): rename only an owned in-memory working copy.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Source copyright and licence remain intact.
Requires a dedicated FontLab session with no other documents; enforced by owned_font.

Original call: `run() -> dict`.

Expected output and limits: after.familyName equals Scripting Sample after.postscriptFontName equals ScriptingSample-Regular embedded copyright and licence survive assignments

Fixtures: `baar`. Changes owned copy: true. Additional dependencies: none.

## kerning_classes

GG Stroke Chan OFL Italic (OFL-1.1): inspect typed pairs and group members.
Source font: https://code.fontlab.com/getgo-fonts/stroke-chan/
Original example code: Apache-2.0. No class expansion or renaming is performed.

Original call: `run(limit: int | None=5) -> dict`.

Expected output and limits: pair_count equals length of pairs classes retain native member names and mode each pair preserves native left/right object mode and explicit zero values

Fixtures: `stroke-chan`. Changes owned copy: false. Additional dependencies: none.

## designspace

GG Cosm (CC0-1.0): report master, axis and eight export-instance coordinates.
Source font: https://code.fontlab.com/getgo-fonts/cosm-var/
Original example code: Apache-2.0. Design coordinates differ from user coordinates.

Original call: `run() -> dict`.

Expected output and limits: masters contains 3 names; axes contains 1 axis tagged wght; instances contains 8 export instances locations and instance coordinates have one coordinate per axis default/current master selection is unchanged

Fixtures: `cosm-var`. Changes owned copy: false. Additional dependencies: none.

## master_compatibility

GG Plum (CC0-1.0): compare direct-contour topology across three masters.
Source font: https://code.fontlab.com/getgo-fonts/plum-var/
Original example code: Apache-2.0. Equal topology alone does not prove interpolation quality.

Original call: `run() -> dict`.

Expected output and limits: A/V/a contain one signature per native master compatible equals the equality of actual contour/node-type signatures with no missing layer no claim about component compatibility or geometric interpolation quality

Fixtures: `plum-var`. Changes owned copy: false. Additional dependencies: none.

## spacing

GG Baar (CC0-1.0): give I the left and right sidebearings of H.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Changes are discarded when the owned copy closes.
Requires a dedicated FontLab session with no other documents; enforced by owned_font.

Original call: `run() -> dict`.

Expected output and limits: I sidebearings match H within 0.01 units after editing I advance equals plan.width only I on the default master is edited

Fixtures: `baar`. Changes owned copy: true. Additional dependencies: none.

## batch_transform

GG Baar (CC0-1.0): horizontally scale A/V nodes, anchors and advances.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Only the owned copy's default master changes.
Requires a dedicated FontLab session with no other documents; enforced by owned_font.
Scaling about x=0 scales left/right sidebearings along with outlines and advances.

Original call: `run(scale: float=1.1) -> dict`.

Expected output and limits: A/V after_width equals before_width times scale within 0.01 units all edited nodes read back their planned x/y within 0.01 units anchors x scale and y stay unchanged

Fixtures: `baar`. Changes owned copy: true. Additional dependencies: none.

## export_ttf

GG Baar (CC0-1.0): export .notdef/space/A/V as a verified TrueType subset.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Native hints/features/kerning are omitted.

Original call: `run(destination: str | Path | None=None) -> dict`.

Expected output and limits: verified is true; format equals glyf binary reopens with exactly .notdef/space/A/V, preserved cmap and advances name ID 13 matches the full fixture licence; bounds agree within 2 units

Fixtures: `baar`. Changes owned copy: false. Additional dependencies: fontTools.

## export_otf

GG Baar (CC0-1.0): export .notdef/space/A/V as a verified CFF OpenType subset.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Native hints/features/kerning are omitted.

Original call: `run(destination: str | Path | None=None) -> dict`.

Expected output and limits: verified is true; format equals CFF binary reopens with exactly .notdef/space/A/V, preserved cmap and advances name ID 13 matches the full fixture licence; bounds agree within 2 units

Fixtures: `baar`. Changes owned copy: false. Additional dependencies: fontTools.

## font_info_ui

GG Stroke Chan OFL Italic (OFL-1.1): show a detached font-info snapshot.
Source font: https://code.fontlab.com/getgo-fonts/stroke-chan/
Original example code: Apache-2.0. PythonQt.QtGui uses FontLab's existing event loop.

Original call: `run() -> InfoTool`.

Expected output and limits: handle.widget is a visible owned QDialog with a read-only QPlainTextEdit displaying the detached report fields handle.report.glyphs equals manifest glyphs (106) font document is already closed when the window is shown handle.close() clears widget; repeated close is safe; process deferred deletion events

Fixtures: `stroke-chan`. Changes owned copy: false. Additional dependencies: none.

## compare_fonts

GG Baar (CC0-1.0) and GG Hint (Apache-2.0): normalized glyph-width comparison.
Source fonts: https://code.fontlab.com/getgo-fonts/baar/
https://code.fontlab.com/getgo-fonts/hint/
Original example code: Apache-2.0. Each input has its own temporary copy.

Original call: `run() -> dict`.

Expected output and limits: only_left/only_right agree with native glyph name differences width_delta_em uses each fonts own UPM both owned documents are closed after returning or failing

Fixtures: `baar`, `hint`. Changes owned copy: false. Additional dependencies: none.

## Provenance and acceptance

Code remains Apache-2.0. Fonts use Apache-2.0, CC0-1.0 and OFL-1.1; retain each
original license and copyright. data/manifest.json records upstream revision,
paths, links and immutable hashes for all99fonts. lessons/provenance/getgo.json
records each source code hash and its packaged destination. Original function
bodies and comments are retained except namespace/fixture relocation, the
shared report adapter and the new typed menu/registry interface.

Pure tests, faked native objects, real FontTools export/reopen tests and
separately installed wheel/sdist checks establish offline behavior and package
closure. They do not prove FontLab native geometry/history/UI behavior. All13
packaged runtime manifest rows remain pending until dedicated owned-font native
runs verify actual results, cleanup and persistence on the final artifact.
