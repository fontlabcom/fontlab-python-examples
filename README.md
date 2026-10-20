---
this_file: README.md
---

# FontLab Python examples

This integration candidate combines 16 practical menu facades and 494
preserved-source launchers. All entries use one category folder beneath
`Scripts`. Each archived launcher is explicitly marked native compatibility
pending. Counts describe source layout, not accepted native workflows.

Copy the practical `Scripts` entries into FontLab 9's Scripts folder. Use
Python 3.11, Fly, the reviewed App 0.2.40.dev0 candidate and the reviewed
`fontlab-python-lessons` 1.0.4.dev0 package. These are
unpublished prerequisites; use their reviewed artifacts. Do not change a live
FontLab environment as part of automated setup or test runs.

## Preserved-source launchers

Archived launchers additionally need the exact private/local `rescued` tree
beside `Scripts`, as recorded in `rescue-index.json`. Those bodies are retained
outside this feature branch and are not copied into public commits, packages
or documentation. A fresh checkout alone cannot run these pending entries.
Their purpose, source SHA and compatibility limit are stated in each launcher.
No archived body was executed during integration or verification.

For an offline hash audit, set `FONTLAB_PRESERVED_ROOT` to the existing checkout
that contains the matching `rescued` tree. Tests read its bytes only; simulated
dispatch targets remain in this checkout. Missing/mismatched source data fails
the audit. Providing this path does not authorize executing original bodies.

## Integration and acceptance

The 16 practical lessons include the three existing Forms/Models lessons and
13 GetGo lessons. Licensed GetGo fixtures, complete notices and runtime code
remain in the `lessons` package. No fixture or runtime byte changed here.

Existing dirty checkouts were read only. The integration uses isolated worktrees.
Native FontLab execution, complete font/history preservation, UI/Close and the
whole original-source migration remain pending. No tag, release, site publication
or live installation is part of this candidate. Archive removal still requires
complete disposition, provenance, recovery and accepted destinations.

The [earlier guide](docs/PRE-INTEGRATION-GUIDE.md) retains historical workflow
and release descriptions. Some historical relative links refer to the earlier
layout; documentation routes and publication require their own review.

## Verification

Run pytest with plugin autoload disabled and the preserved-source root supplied.
Scriptmix also requires the reviewed installed App and `--original-source-root`
for original-byte checks. Examples retains its repository tests and the `lessons`
package suites. Exact commands, skips and limitations are recorded in WORK.md.
