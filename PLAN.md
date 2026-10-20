---
this_file: PLAN.md
---

# GetGo real-font scripting acceptance

Owner request: use the public GetGo VFJ/TTF fonts for real tests and scripting
examples, keeping public code.fontlab.com links and licence provenance.

Done and archived in CHANGELOG.md: item 1 (fixtures, provenance, verification).

2. Native acceptance is recorded for the current VFJs (corpus 99/99; 17 fonts edited,
   saved, reopened, exported; 6 of 16 variable exports pass, the other 10 fail on the
   unedited originals). Remaining: after F1 fixes the source VFJs, re-sync them into
   testdata/getgo (new hashes), re-run corpus and variable exports.
3. Done: the 13 examples pass natively 13/13 (archived in CHANGELOG.md).
4. Docs export (getgo.md) and the 1874-test suite are done. Close the group when 2 and 3
   are complete; broader publication stays in the parent plan.


## Issue120 menu integration W1

- [x] Verify the combined source layout, immutable release provenance and all existing tests.
- [ ] Review feature-branch integration without changing canonical checkouts or live installs.
- [ ] Qualify pending archived workflows in native FontLab before any acceptance or cleanup claim.
