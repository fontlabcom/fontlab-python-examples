---
this_file: TODO.md
---

- [x] Run native corpus acceptance (99/99, corpus3) and real edits/save/reopen/TTF-OTF exports on 17 owned copies (edits7, edits9-heavy); variable-export failures reproduce on the unedited originals and are retained.
- [ ] Re-sync the F1-fixed VFJs into testdata/getgo when the controller hands them over (new hashes, manifest, counts), re-run corpus and variable exports, record which failures disappear.
- [x] Add practical original GetGo scripting examples with public font links (13, ac57342, a83f4a7).
- [ ] Commit X2's close_font fix in examples/getgo/_shared.py (native 13/13 pass only with it, examples3-all) and update the README/native_manifest "unexecuted" status to the measured receipts.
- [x] Regenerate docs-export with examples/getgo and run the full suite (54bf14d, 4e3f8aa; 1874 passed with fontTools).
