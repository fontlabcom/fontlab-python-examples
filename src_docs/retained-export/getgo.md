# Real GetGo fonts, disposable working copies

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, now preserved under `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

Thirteen original Apache-2.0 examples for FontLab 9. Each entry verifies a
fixture SHA-256, copies its VFJ to a new temporary directory, opens that copy
and closes exactly that package in `finally`. Copy paths are resolved before opening
so macOS `/var` and `/private/var` refer to the same owned document. Successful cleanup removes the
working directory; failed close retains it. Nothing saves over testdata.
Font attribution and licences remain in the [fixture manifest](https://github.com/fontlabcom/fontlab-python-examples/blob/main/testdata/getgo/manifest.json).

All modules import outside FontLab. Entry functions need FontLab's `fontlab`,
`fontgate` objects and `fontpr` bridge. The pen/export entries additionally need
**FontTools** installed in FontLab's Python 3.11 interpreter. TypeRig and Fontport
are not required for these thirteen scripts. Run edits in a dedicated no-document
FontLab session through the workspace native runner. **Native status: 13/13 passed**
on **2026-10-16, FontLab 9.0.9783** (workspace receipt: `verification/issue-106/evidence/getgo/examples3-all/receipt.json`).
The receipt covers `run()`, declared assertions, owned cleanup and unchanged fixtures; host-free tests remain separate.

## Repository-checkout demos: run inside FontLab

These are repository-checkout demos, not standalone Scripts-folder installations.
Keep the checkout (including `testdata/getgo`) together and put its root on
`sys.path` once, then import an example:

```python
import sys

sys.path.insert(0, "/path/to/fontlab-python-examples")
from examples.getgo import font_audit

print(font_audit.run())
```

Each script also has a MenuTitle and prints its result when executed from the
Scripting panel as `__main__`; keep that root on `sys.path` for this route too.
No script chooses the current font. The UI returns an explicitly owned handle;
all other results are dictionaries. Mutation entries enforce the no-document
requirement before reading fixtures or creating a working directory and name any
open documents in the error. Read-only examples may coexist with other fonts.

## font_audit — metrics, encoding and anchor policy (native passed; 0.21 s)

[font_audit.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/font_audit.py) uses [GG Baar](https://code.fontlab.com/getgo-fonts/baar/)
(CC0-1.0). Measured: 96 glyphs, 95 encoded scalars, 2048 UPM, and no anchors.
The report also covers vertical metrics, unencoded names and Unicode collisions.
GG Baar has zero anchors: both counts make that explicit, alongside missing A/H
`top` anchors. The explicit
anchor policy demonstrates a check; an absent anchor is not automatically a font defect.

## unicode_coverage — Arabic sample text (native passed; 0.27 s)

[unicode_coverage.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/unicode_coverage.py) uses
[Zoto Kufi Arabic](https://code.fontlab.com/getgo-fonts/zoto-kufiarabic/)
(Apache-2.0). `run(text="مرحبا بالعالم 123")` compares native encodings against
unique scalars through a Unicode-only reader. Measured: eight covered code points;
U+0031/U+0032/U+0033 are missing. U+0627 is covered; no layer/anchor lookup is needed.
Encoding coverage does not prove contextual shaping.

## outline_pens — bounds, direction and complexity (native passed; 0.18 s)

[outline_pens.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/outline_pens.py) uses [GG Hint](https://code.fontlab.com/getgo-fonts/hint/)
(Apache-2.0). A/B/O contours pass through FontTools BoundsPen/AreaPen for exact
curve bounds and signed areas. Measured A/B/O: 2/3/2 contours, 11/55/42 points;
winding labels and FontLab `hasIntersPoints` boundary-intersection index pairs.
Contained counters and self-intersections are outside the pairwise test;
this is not filled-region boolean overlap detection or overlap removal. Each native
recording converts QPointF operands to tuples before segment-pen validation; open paths
require `endPath`, closed paths `closePath`. This receipt validates closed native
contours; native open-path coverage remains a follow-up.

## naming — name a disposable derivative (native passed; 0.12 s)

[naming.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/naming.py) uses [GG Baar](https://code.fontlab.com/getgo-fonts/baar/)
(CC0-1.0). Measured: assigned family, style, preferred and PostScript names read back;
family becomes `Scripting Sample`, PS name `ScriptingSample-Regular`.
Copyright/licence stay intact. The small policy accepts ASCII letters, digits
and spaces and enforces the 63-character PS limit. Changes are discarded on close.

## kerning_classes — pairs retain their meaning (native passed; 0.19 s)

[kerning_classes.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/kerning_classes.py) uses
[GG Stroke Chan OFL Italic](https://code.fontlab.com/getgo-fonts/stroke-chan/)
(OFL-1.1). Measured on the Italic master: default-master pair count, typed pair sides,
explicit zero values, class members/modes and dangling member names. The default
`run(limit=5)` returns totals (619 pairs across 79 left sides, 233 classes) and up to five pairs, classes
and members per class; `run(limit=None)` returns complete data. Opaque native
modes become text for JSON. No class expansion or OFL font renaming occurs.

## designspace — axes, masters and instances (native passed; 0.26 s)

[designspace.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/designspace.py) uses [GG Cosm](https://code.fontlab.com/getgo-fonts/cosm-var/)
(CC0-1.0). Measured: three masters, one `wght` axis, separate user/design ranges,
master and eight export-instance coordinates in axis order. `valueWeight` reads design
coordinates. The selected master stays unchanged; no interpolation is implied.

## master_compatibility — compare direct-contour topology (native passed; 0.23 s)

[master_compatibility.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/master_compatibility.py) uses
[GG Plum](https://code.fontlab.com/getgo-fonts/plum-var/) (CC0-1.0).
Measured: A/V/a match across all three masters; reports include closed flags, `compatible`
and `missing_layers`. Missing layers differ from empty layers. Equal topology
does not prove component compatibility, contour correspondence or interpolation quality.

## spacing — I borrows H's bearings (native passed; 0.11 s)

[spacing.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/spacing.py) uses [GG Baar](https://code.fontlab.com/getgo-fonts/baar/)
(CC0-1.0). It plans I's shift/new width, moves direct nodes and anchors and
reads bearings back. Measured: I's bearings [128, 0], shift 48, new width 416, plus
`plan` and resulting `sidebearings`. The fixed H/I inputs have direct outlines;
only I on the owned font's default master changes. The basic node/anchor move
follows [the existing sidebearing recipe](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/recipes/sidebearings_from_reference/recipe.py);
this demo adds an owned real input, an RSB-aware plan and bounds from re-read nodes
of the straight-line I outline; native cached boundingBox/contourRect remain stale.

## batch_transform — widen A and V (native passed; 0.11 s)

[batch_transform.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/batch_transform.py) uses [GG Baar](https://code.fontlab.com/getgo-fonts/baar/)
(CC0-1.0). `run(scale=1.1)` preflights both glyphs and scales direct node/anchor
x coordinates and advances, retaining y coordinates. Expected: A/V point counts
Measured A/V widths: 640 → 704. Readback re-fetches the layer
and contours instead of inspecting the wrappers just assigned; anchors and
advance widths are checked too. Scaling about x=0 also scales both sidebearings.
Only the disposable default master changes; source data stays intact.

## export_ttf — compile and reopen quadratic outlines (native passed; 0.17 s)

[export_ttf.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/export_ttf.py) uses [GG Baar](https://code.fontlab.com/getgo-fonts/baar/)
(CC0-1.0). Native contour pens capture `.notdef`, `space`, `A`, `V`; the font
closes before Cu2QuPen/TTGlyphPen and FontBuilder create a TTF geometry subset.
The native pen adapter detaches QPointF coordinates into ordinary tuples for both exports.
Measured: `verified: true`, `format: glyf`, retained binary path, exact glyph
order/cmap/advances/UPM and full licence name record. Reopened bounds must agree
within two units for curve conversion and coordinate rounding. Every contour
is also measured with AreaPen after binary reopening: TTF signs must reverse
the source signs, and CFF signs must match. `winding_verified` and per-contour
`winding` reports expose those checks without assuming absolute source winding.

## export_otf — compile and reopen CFF outlines (native passed; 0.11 s)

[export_otf.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/export_otf.py) uses [GG Baar](https://code.fontlab.com/getgo-fonts/baar/)
(CC0-1.0). T2CharStringPen builds the same subset as CFF OpenType.
Measured: `verified: true`, `format: CFF` and the same readback checks.
Both exports accept `run(destination="/absolute/new-sample.otf")` (use `.ttf`
for TTF); the default retains a new temporary export directory. Existing files
and symlinks are refused. Outputs are named `Scripting Sample`, with complete
CC0 text, copyright and public source URL. These geometry subsets omit native
hints, features, kerning, axes and other layers. They demonstrate pen interchange,
not FontLab's export profiles.

## font_info_ui — a tiny PythonQt tool (native passed; 0.15 s)

[font_info_ui.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/font_info_ui.py) uses
[GG Stroke Chan OFL Italic](https://code.fontlab.com/getgo-fonts/stroke-chan/)
(OFL-1.1). It closes the font before showing a QtGui QDialog with a plain text
QLabel. Measured: GG Stroke Chan OFL, 106 glyphs, 1000 UPM, Italic master. Retain the handle:
`tool = font_info_ui.run()`, inspect `tool.report`/`tool.widget`, call
`tool.close()` in `finally`, then drain deferred deletion events in the native
runner. The Scripting-panel `__main__` route calls canonical-module `show()`,
which retains `font_info_ui.TOOL` even when panel globals are discarded; a second
launch closes the predecessor. Native acceptance must exercise this route and
verify the plain-text enum, visibility and deferred deletion. Cleanup is idempotent. No signals, QApplication or second loop are created.

## compare_fonts — compare in em units (native passed; 0.31 s)

[compare_fonts.py](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/compare_fonts.py) uses
[GG Baar](https://code.fontlab.com/getgo-fonts/baar/) (CC0-1.0) and
[GG Hint](https://code.fontlab.com/getgo-fonts/hint/) (Apache-2.0).
Measured: 96 common glyphs, 274 Hint-only glyphs, none Baar-only; width differences
in em units (right minus left), using each font's own UPM. Nested owned contexts
close both documents even if opening or inspecting the second fails.

## Native execution and host-free verification

[native_manifest.json](https://github.com/fontlabcom/fontlab-python-examples/blob/main/examples/getgo/native_manifest.json) lists all entries, fonts, dependencies,
observable checks, cleanup and measured native passes from the linked receipt.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
```

FontLab's `run_python` has a fixed **5-second deadline**. Never execute a complete
`run()` synchronously through it: file opening, import cold starts and compilation
can exceed it. Use the Scripting panel or an event-loop callback outside the
request, keeping `run_python` calls to short setup/enqueue/poll operations. Preserve
a detached result/error receipt and poll it; a client timeout is not a native pass.

Manifest `expected` entries are machine assertions (`path` plus exactly one of
`equals`, `len`, `contains`, `gt`), executed by `_checks.assert_expected(result,
row["expected"])`. Paths include dictionary keys, list indices and UI handle
attributes. UI cleanup is explicitly `handle.close`. The manifest's
`native_followups` retain save-prompt, metadata-renormalization, refreshed-bounds,
segment-pen and Scripting-panel UI checks for the native worker.

Add `--with fonttools` to `uv run` and target `tests/test_getgo_scripts.py` for
real pens, binary and winding-tamper checks. No Fontport dependency or legacy
`scripts.py` API remains; the needed master-report helper now lives in designspace.py.
