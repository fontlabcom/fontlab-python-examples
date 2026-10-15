---
this_file: README.md
---

# FontLab Python examples

PythonQt examples for the existing FontLab application, with a complete pinned
upstream inventory and explicit implementation states. Start at the
[categorized catalogue](catalog/INDEX.md) or [port records](catalog/ports.json).

| Current port state | Records |
| --- | ---: |
| Implemented, with recorded native launch/inspect/close | 21 |
| Blocked by recorded host capabilities | 151 |
| Independent clean-room implementations, native unexecuted | 127 |
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
hash and review basis. All replacement native acceptance remains **unexecuted**.
The 21 previously accepted non-official ports retain their recorded acceptance.

Each record preserves its original source repository, revision, path, byte counts,
hashes, upstream URL, archive and spec pointers. These identify archived inputs;
they do not describe replacement bytes or grant Apache-2.0 to archived resources.
`sources.json` keeps replacement grants in `port_license`. Historical passes for
removed implementations remain historical, as described in the
[batch notes](docs/pyqt-official-batch.md).

## Launch an available example

Put this checkout on FontLab's Python path and install `fontlab-fontlabapp` in its
interpreter. Use FontLab's existing PythonQt and QApplication; do not load a
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

Run the native acceptance driver separately, against an owned FontLab session
with Fontlabapp installed in its interpreter:

```sh
uv run --python 3.11 tools/native_cleanroom.py --batch-size 8 \
  --output /private/tmp/fontlab-cleanroom-native.jsonl
# Optional selection (space- or comma-separated IDs):
uv run --python 3.11 tools/native_cleanroom.py \
  --ids 035f3fbd2b81479a 960c701fa6221ac5 --batch-size 2 \
  --output /private/tmp/fontlab-cleanroom-selected.jsonl
```

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
Fourteen non-official resource grants/creator attributions remain unresolved;
see the ledger, [numbered notices](ports/pyqt-examples-LICENSE.md) and
[QtExamples notices](ports/eyllanesc-LICENSE.md). Official notices and old licence
claims reside with the private archive, not the replacement implementations.

The remaining work is new native acceptance, further interaction checks,
resource review and documentation integration: [PLAN](PLAN.md), [TODO](TODO.md).
