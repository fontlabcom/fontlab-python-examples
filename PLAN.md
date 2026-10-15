---
this_file: PLAN.md
---

# GetGo real-font scripting acceptance

Owner request: use the public GetGo VFJ/TTF fonts for real tests and scripting
examples, keeping public code.fontlab.com links and licence provenance.

1. Copy all 99 VFJs unchanged into testdata/getgo, retain the three licence texts
   and pin source revision, hashes, attribution, public pages and download links.
   Verify every actual font file, master/axis counts and manifest completeness.
2. Run native load/read acceptance on the real corpus through the shared runner
   using owned copies; preserve every failure and source hash. Run actual
   mutations/save/reopen and exported-artifact checks on representative static,
   variable, hinted, non-Latin and OFL/Apache/CC0 fonts.
3. Build practical original scripting examples around the real fixtures: font
   audit, pen/outline interchange, metadata/kerning, multimasters/designspace and
   exported results. Public docs link each font's GetGo page; results distinguish
   supported behavior from measured native limits.
4. Verify examples natively, update the generated documentation export, run the
   complete host-free suite and record receipts/commands. Archive only complete
   groups; broader workspace integration/publication remains in the parent plan.
