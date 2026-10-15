---
this_file: README.md
---

# FontLab Python examples

PythonQt examples for the existing FontLab application, with a complete pinned
upstream inventory and explicit implementation states. Start at the
[categorized catalogue](catalog/INDEX.md) or [port records](catalog/ports.json).

| Current port state | Records |
| --- | ---: |
| Implemented, with recorded native launch/inspect/close | 148 |
| of which independent clean-room implementations | 127 |
| Blocked by recorded host capabilities | 151 |
| Total | 299 |

The original insight examples in [ports/insights](ports/insights) are a separate
collection; 18 have recorded native interaction checks.

## Official-demo clean-room work

Owner decision D7 moved the official-demo sources, resources and licence notes to
the private `fontlabcom/fontlab-python-examples-reference` repository, commit
`040b2e8`, under `pyqt-official-ports/`. This public tree contains their provenance
metadata and [187 behavioural specifications](clean-room-specs/INDEX.json).
All 187 receipts are integrated: **127 implemented, 60 blocked**. The replacements
and their newly authored resources use Apache-2.0; the catalogue records the spec
hash and review basis. **All 187 pass native acceptance in FontLab 9.0.9783**: the
127 implementations launch, show a populated window and close with every owned
object, timer and window gone; the 60 blocked records raise their recorded
capability reason without touching the host. Two independent runs agree (workspace
evidence `examples-cleanroom/final*` and `examples-cleanroom/controller/`).
Interactions: 106 implementations had every state control changed and read back
without a slot error, then were closed and relaunched; 21 whose specs need files,
network, printing, the clipboard or the tray were skipped by reason
(`examples-cleanroom/interactions-final.jsonl`). The 22 implementations without state
controls were driven with synthetic mouse, keyboard and drop events on their own
widgets (`examples-cleanroom/events-final.jsonl`): 20 passed; delayedencoding (drag-out
only, a system drag loop) and broadcastsender (LAN broadcast) are skipped by reason. The 21 earlier non-official ports
retain their recorded acceptance.

Each record preserves its original source repository, revision, path, byte counts,
hashes, upstream URL, archive and spec pointers. These identify archived inputs;
they do not describe replacement bytes or grant Apache-2.0 to archived resources.
`sources.json` keeps replacement grants in `port_license`. Historical passes for
removed implementations remain historical, as described in the
[batch notes](docs/pyqt-official-batch.md).

## Launch an available example

Put this checkout on FontLab's Python path and install `fontlab-fontlabapp` in its
interpreter (or, for the native driver, keep a sibling `fontlab-fontlabapp` checkout). Use FontLab's existing PythonQt and QApplication; do not load a
second Qt binding or run another application event loop.

```python
import fontlab_python_examples as examples

examples.available()                   # Includes implemented and blocked metadata
handle = examples.launch("QLabel")     # Inside FontLab
handle.widget                         # Direct owned native widget
examples.inspect("QLabel")             # JSON-friendly live state
examples.close("QLabel")               # Owned cleanup; FontLab stays open
```

The four introductory examples are QLabel, QVBoxLayout, Signals and Slots, and
Qt Designer. Further implemented numbered examples and QtExamples entries are
listed in the catalogue. `examples/remopy.py` provides an external controller.
The [numbered-example checks](docs/second-numbered-batch.md) describe their scope.

## Recipes for everyday glyph work

[examples/recipes](examples/recipes/README.md) holds nine small FontLab 9 scripts,
each checked natively on a font it creates and throws away: layer backup,
coordinate rounding, contour direction and start points, anchors from bounds,
sidebearings from a reference glyph, kerning pairs from text, Tools > Actions on
named glyphs (via fontlab-fontlabapp), and two unchanged Glyphs scripts run through
fontlab-glyport. They are written from scratch (Apache-2.0); TypeRig and Glyphs
scripts were consulted for tool names and behaviour only. Host-free tests:
`tests/test_recipes.py`.

## Inventory and provenance

| Collection | Pinned revision | Original files | Python files |
| --- | --- | ---: | ---: |
| pyqt/examples | `83eed0514582c8deb60d9e9e6bff31ceffe4eaeb` | 805 | 308 |
| eyllanesc/QtExamples | `a01fd7d10d45801b10876f94c07aaefb11bc2e12` | 764 | 157 |

[sources.json](catalog/sources.json) retains all 1,569 source identities and 465
Python files, including both case-colliding matplotlib filenames. It distinguishes
raw static observations, [review decisions](catalog/reviews.json) and port states.
The original 298 entrypoint candidates plus the database initializer retain 299
port records. Reviewed additional launcher, QML, plugin and helper roles remain
visible without being presented as implemented examples.

Regenerate current states and the derived inventory without accessing originals:

```sh
python3 tools/integrate_cleanroom.py
```

The tool validates all receipts, target paths, source headers and spec hashes,
keeps the immutable source/resource provenance, regenerates sources/INDEX and
updates the manifest's source-catalogue hash. Reapplying is deterministic and
resets replacement native acceptance to unexecuted. Original-tree acquisition
and analysis through `tools/inventory.py` remain separate from this clean-room
integration; they are not required to regenerate the checked-in catalogue.

## Verify

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
```

Tests use owned fixtures and doubles. Every clean-room record has a receipt,
import/build or explicit capability check, and public-launcher coverage. The
independent batches exercise replacement behavior; obsolete assertions about
removed fixtures and Python implementation details have been replaced. Shared
helpers, binding regressions and unchanged non-official ports remain covered.

Run the native acceptance driver separately, in a FontLab session without open
documents, from the workspace root (it resolves `fontlab-remopy` from the sibling
checkout and imports `fontlab-fontlabapp` from `../fontlab-fontlabapp/src` when
FontLab has it not installed):

```sh
verification/issue-104/fl-native.sh --lane L6c -- bash -c "cd fontlab-python-examples && \
  uv run --python 3.11 tools/native_cleanroom.py --batch-size 8 --output OUT.jsonl"
# --ids ID ... selects ports; --reset-stale first clears sessions an interrupted run left.
```

Run it from a clean, committed checkout: the summary records the commit, whether
the tree was dirty and whether the revision stayed unchanged, and every receipt
hashes the port's whole dependency closure (its files, the ports it loads and the
launcher package) before it runs. Derive a proposal from the receipts, review it,
then record it. `apply` refuses the whole proposal and writes nothing unless every
receipt shows six successful phase envelopes and clean teardown, the run commit is
in this checkout's history and clean, the driver matches that commit, and each
closure matches both the run commit and the current files:

```sh
python3 tools/record_native.py propose --output PROPOSAL.json OUT*.jsonl
python3 tools/record_native.py apply PROPOSAL.json --commit <examples commit of the run>
```

`tools/integrate_cleanroom.py` resets replacement acceptance; run `record_native.py`
again after it.

Batches reuse client connections; every host phase is a separate call with a
3.5-second host budget and a four-second transport deadline. The driver purges
stale example modules, verifies this checkout's import, restores `sys.path` after
every call, checks visible top-level content and owned cleanup/deferred native
destruction, and verifies blocked launches before host/builder access. It stops
if cleanup fails or execution becomes uncertain, records remaining IDs as not
run, and never retries a launch after a timeout. Outputs are JSONL plus a sibling
`.summary.json`; choose a new output name for each run.

The driver performs launch/inspect/close only, without screen capture, clipboard,
tray notifications or font edits. It does not update catalogue acceptance.
[Existing native evidence](verification/catalog-native-evidence.json) includes
historical archived-code records; offline tests and this driver implementation
do not constitute new native execution or installed-wheel acceptance.

## Licences and remaining work

The repository's Apache-2.0 licence applies to its original code. Upstream inputs
keep their own recorded terms. [The per-file ledger](catalog/licenses.json) covers
112 non-official source records, 15 resources and 19 original insight files.
The 14 non-official resources that had no individual grant are replaced by
self-authored Apache-2.0 files (`tools/replacement_assets.py`); see the ledger, [numbered notices](ports/pyqt-examples-LICENSE.md) and
[QtExamples notices](ports/eyllanesc-LICENSE.md). Official notices and old licence
claims reside with the private archive, not the replacement implementations.

The remaining work is new native acceptance, further interaction checks,
resource review and documentation integration: [PLAN](PLAN.md), [TODO](TODO.md).
