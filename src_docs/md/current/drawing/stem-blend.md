---
this_file: src_docs/md/current/drawing/stem-blend.md
tags: ["Drawing"]
categories: ["Drawing"]
---

# Stem Blend

What: Write a stem-compensated blend into a new layer of the current glyph.
How: Divide target stems by scale to choose independent X/Y interpolation
fractions. Unslant, blend, scale and reslant. The final stems match the typed
measurements when the source stems interpolate linearly.
Why: Make scaled lettering at a requested stem size without changing masters.
Usage: Open a glyph. Choose two source layers. Enter measured source and target
stems and scale factors. Build, inspect the output name, then Create Layer.
The layer name is Stem <vertical>x<horizontal> (<current master>), for example
Stem 75x60 (Light). Names containing @ or #, starting with |temp|, or matching
a master name are refused. An existing layer name is refused. Each new layer
is recorded as one Undo step through App history. The new layer becomes the
active layer.
Benefit: Keep native font-unit geometry without an artwork import transform.

The angle starts at minus the current master's italic angle; positive means
that the top moves right. Refresh Sources reloads layer choices and the angle.
Targets divided by scale must lie between the measured source stems. Equal
stems, components, shape transforms and incompatible paths are refused.
TrueType off-curves stay quadratic, including implied on-curve midpoints.
The new layer keeps the first source's advance. Anchors, hints, node flags
and other source metadata are not copied. Automatic-layer owners and bases of
automatic composites are kept unchanged and named in the refusal message.
Copy SVG is secondary artwork only. SVG import may rescale or reposition it;
no SVG import preserves scale by this tool's guarantee.
No stored axis setup, extrapolation or batch target baking is provided.
Use native Font > Generate Instance for native instance generation.
Requires FontLab 9, Python 3.11, Fly and App >= 0.2.150.dev0.

Credit: Independent behaviour rewrite of Delta.py and DeltaNew.py by Vassil
Kateliev, TypeRig, kateliev/TypeRig, MPL-2.0.
https://github.com/kateliev/TypeRig
No source code, comments, icons or preset formats are copied.
Read-back allows coordinate changes up to 1e-5 units. Advance is checked against
its detached value read immediately after the native setter applies the current
rounding preference, with the same tolerance. The coordinate tolerance comes
from native source; it is unmeasured in native FontLab execution.

Run **Drawing > Stem Blend** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/7cdfda967292c4d6956e3fa22412634ef99b58e253455df6051a1699e1997a9d.py)
<!--/codeinclude-->
