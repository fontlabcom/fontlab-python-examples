---
this_file: src_docs/md/slider-spacing-offsets.md
---

# Preview spacing offsets

Open a font, select glyph layers and run **Widgets > Glyph Spacing Offset** or
**Glyph Spacing Offset - Stacked** with matching Fly and App0.2.95.dev0.
The result lists every captured occurrence, including repeated editor slots.
Moving ink by an offset increases the geometric left margin and decreases the
right margin while preserving advance. This is a local comparison; no font is edited.

Both tools keep minimum/maximum/value editors from−100 to100, initially0/20/5,
a slider, scrollbar and dial, orientation and appearance/key inversion. Native
arrows, PageUp/PageDown, Home/End, dragging and wheel actions remain available.
The three-control tool clamps the value editor and raises maximum to minimum.
Its initial controls now match the Horizontal label (the original wrongly
started vertical). The stacked tool keeps two complete fixed-orientation groups,
StrongFocus, ticks and native cyclic feedback. Its range editors remain
independent, and choosing an orientation activates the corresponding group.
Native feedback can leave its numeric editor beyond a slider already at its
bound; the preview always names the actual slider offset. Scrollbars initially
use their native inverted-key default; toggling the checkbox applies one setting
to every control, as in the originals.

Refresh Selection replaces all facts and preserves your drafts; capture failure
clears old results. Close, Escape and parent destruction release only owned
widgets and connections. Empty/sticker-only layers with no geometric bounds
show unavailable margins while retaining their advance. Bounds are geometric,
not slanted metrics or spacing-key evaluation.
