---
this_file: testdata/getgo/README.md
---

# GetGo real-font fixtures

These 99 unchanged VFJs are copied from [GetGo Fonts for FontLab](https://code.fontlab.com/getgo-fonts/)
at source revision cf1319fa3c0c9f8c0703615231eabeab02cb5901. Each file's public
font page, original VFJ/TTF download links, SHA-256, size, glyph/master/axis counts,
licence and original attribution are in [manifest.json](manifest.json).
CC0-1.0, Apache-2.0 and OFL-1.1 texts remain in their original licence folders;
embedded font notices are unchanged. These fonts retain their own terms.

All scripting mutation tests first copy fixtures into their owned output directory
and open those copies in a dedicated FontLab session. Fixture bytes are never
saved over. Shared workspace tests refer to this corpus instead of duplicating
it into every package distribution. Real-font native receipts are kept outside
the public examples repository.

## Verification

- `tests/test_getgo.py` checks every VFJ against the manifest (bytes, SHA-256,
  glyph/master/axis counts, licence folder, public links).
- `tools/verify_getgo_source.py --source <getgo-fonts checkout> [--online]` compares
  the copies, licence texts and catalogue (`fonts.json`) with the upstream checkout
  and, with `--online`, HEADs each public page, VFJ and TTF link.
- `tools/native_getgo.py` opens every copy in FontLab and reads it back;
  `tools/native_getgo_edits.py` edits, saves, reopens and exports representative
  fonts and checks the exported TTF/OTF/variable binaries with fontTools.
- `*.vfj` is marked `-diff` in `.gitattributes` (the largest file is 64 MB).
