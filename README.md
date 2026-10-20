---
this_file: README.md
---

# FontLab Python examples

This integration candidate combines 22 practical menu facades and 488
preserved-source launchers. All entries use one category folder beneath
`Scripts`. Each archived launcher is explicitly marked native compatibility
pending. Counts describe source layout, not accepted native workflows.

Copy the practical `Scripts` entries into FontLab 9's Scripts folder. Use
Python 3.11, Fly, the reviewed App 0.2.57.dev0 candidate and the reviewed
`fontlab-python-lessons` 1.0.4.dev0 package. These are
unpublished prerequisites; use their reviewed artifacts. Do not change a live
FontLab environment as part of automated setup or test runs.

## Preserved-source launchers

Archived launchers additionally need the exact private/local `rescued` tree
beside `Scripts`, as recorded in `rescue-index.json`. Those bodies are retained
outside this feature branch and are not copied into public commits, packages
or documentation. A fresh checkout alone cannot run these pending entries.
Their purpose, source SHA and compatibility limit are stated in each launcher.
The documentation also retains 18 first-party Apache-2.0 insight listings as inert
text, with their licence and SHA manifest; these are not launcher dependencies.
No archived body was executed during integration or verification.

For an offline hash audit, set `FONTLAB_PRESERVED_ROOT` to the existing checkout
that contains the matching `rescued` tree. Tests read its bytes only; simulated
dispatch targets remain in this checkout. Missing/mismatched source data fails
the audit. Providing this path does not authorize executing original bodies.

## Integration and acceptance

The 26 practical facades include three existing Forms/Models lessons,
13 GetGo lessons and ten complete part2/part3 adaptations: sort/filter models,
read-only trees, modification calendars and glyph-name completion editors. The latter
replace their indexed wrappers through menu-adaptations.json; rescue-index.json
and all494original source identities remain unchanged. Part3 variants keep typed Qt dates, native regexp matching and original
locale/range/comparator rules; part2 keeps its separate string/Python semantics. Basic keeps Qt QRegExp; Custom keeps
Python re/fnmatch/substring, OR fields, inclusive dates and angle-tail sorting. Licensed GetGo fixtures, complete notices and runtime code
remain in the `lessons` package. Existing packaged lesson and fixture bytes stay unchanged.

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

The docs wrapper reads src_docs/retained-export without executing archived
code. If its bytes differ, supply a reviewed checkpoint with
`FONTLAB_RETAINED_EXPORT=/path/to/reviewed-export ./build.sh --offline`. Stale
hashes fail before the accepted export is replaced. Current menu source pages
are separate from the historical retained catalogue; no native result is implied.


Documentation-only SDK tests are in `tests_docs`; run them with
`uv run --locked python -m pytest -q tests_docs`. Runtime and lesson suites
remain separate Python3.11 processes, both required by the workspace push gate.
Set `EXAMPLES_LEGACY_API_SOURCE` to the reviewed read-only first-party API
checkout for namespace compatibility tests. This input supplies only the old
API metadata/launcher with owned doubles; it does not run historical scripts,
restore deleted source or replace the current root test suite.


Z10 documentation output: `./build.sh --offline` now renders into `.build/site`,
separate from retained authored guides in `docs`. Two successive real clean
builds preserve the guide bytes. The earlier default overwrote those guides in
the isolated test checkout; their exact branch bytes were restored and the first
render retained as evidence. No canonical owner path or live site was changed.

The two read-only Simple Tree Model adaptations show full glyph/Unicode/local-date hierarchies. Part2 keeps selection status and File > Exit; part3 keeps its distinct data roles/columns. Both use shared App tree models and remain native-unqualified; separate editable-tree lessons stay pending.

The part2 Calendar Controls adaptation is Glyph Modification Calendar. It keeps every original locale/date/format option and shows all glyphs modified on the chosen local day. It requires reviewed unpublished App>=0.2.60.dev0 through Fly. The distinct part3 calendar has its own complete policy below; both remain native-unqualified.

Glyph Modification Calendar with Formats is the distinct complete part3 workflow: every Qt locale, seven week starts, font-style headers and independent first-Friday/May-1 rules. It shares generic date/ownership/report mechanics with part2 through reviewed unpublished App>=0.2.61.dev0 and Fly. Both remain native-unqualified.

`glyph_completion.show/show_official` adapt both complete custom-completers to current-font glyph names. Distinct key/focus/menu rules share generic injected-Qt mechanics; Refresh keeps the local draft, removes stale completions and uses all names. Failed disconnections refuse Close for retry. Requires reviewed unpublished App>=0.2.63.dev0 through Fly. Native qualification remains pending.
