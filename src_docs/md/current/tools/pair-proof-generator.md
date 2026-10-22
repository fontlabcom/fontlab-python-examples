---
this_file: src_docs/md/current/tools/pair-proof-generator.md
tags: ["Tools"]
categories: ["Tools"]
---

# Pair Proof Generator

What: Generate current-font glyph pairs from two explicit name lists.
How: Combine all left/right names, or zip equal-length lists. Apply each side's
suffix, then validate every resulting name against the current font.
Why: Cartesian combinations expose spacing relationships absent from an
adjacent-pair proof. Unencoded alternates remain usable through slash names.
Usage: Enter space-separated names without slashes. Choose Product or Zip.
Optional fillers are name lists. Copy Fresh Result to a Glyph window text bar.
Benefit: Prepare every requested pair in stable order without editing kerning.
This tool generates proofs. Use File > Export > Metrics for AFM kerning output
and scriptmix Kerning > Classes Browser for class inspection.
scriptmix Kerning > Missing Pairs also builds Cartesian combinations, filtered
to missing kerning. This tool keeps all pairs and adds Zip, suffixes and fillers.
It does not extract existing-kerning proof strings or export KRN, Unicode
strings or OpenType class declarations.

Independent behaviour-only rewrite of the pair-generation idea from Pairs.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Run **Tools > Pair Proof Generator** from FontLab's Scripts menu.

Read [collections](../../collections.md) and [contributing](../../contribute.md) before use.

## Source

<!--codeinclude-->
[Python source](../../../../.build/menu-sources/c1eceaa122f0ed1ae170e2d87fa63b06d76cff1810827d2049a37eba5af24499.py)
<!--/codeinclude-->
