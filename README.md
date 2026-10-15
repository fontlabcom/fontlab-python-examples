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
| Blocked by recorded host capabilities | 91 |
| Official demos relocated, `clean_room_pending` | 187 |
| Total | 299 |

The original insight examples in [ports/insights](ports/insights) are a separate
collection; 18 have recorded native interaction checks.

## Official-demo clean-room work

Owner decision D7 moved the official-demo sources, resources and licence notes to
the private `fontlabcom/fontlab-python-examples-reference` repository, commit
`040b2e8`, under `pyqt-official-ports/`. This public tree contains their provenance
metadata and [187 behavioural specifications](clean-room-specs/INDEX.json).
The independent implementer should use those specifications and fresh resources,
without reading the private reference repository or original Git history.

Each relocated port record preserves its original source repository, revision,
path, byte counts, hashes and upstream URL, and supplies `archive` and `spec`
pointers. Removed files carry no public licence grant or current native pass.
Launching a relocated entry reports its pending state and spec before accessing
FontLab. Historical implementation/checklist material is identified in
[the batch notes](docs/pyqt-official-batch.md); it does not describe current files.

## Launch an available example

Put this checkout on FontLab's Python path and install `fontlab-fontlabapp` in its
interpreter. Use FontLab's existing PythonQt and QApplication; do not load a
second Qt binding or run another application event loop.

```python
import fontlab_python_examples as examples

examples.available()                   # Includes pending and blocked metadata
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

Regenerate from verified local receipts and source roots:

```sh
python tools/inventory.py \
  --tree-receipt "$TREE_RECEIPT" \
  --recovery-receipt "$RECOVERY_RECEIPT" \
  --source-root "pyqt/examples=$PYQT_SOURCE" \
  --source-root "eyllanesc/QtExamples=$QTEXAMPLES_SOURCE" \
  --reviews catalog/reviews.json \
  --ports catalog/ports.json \
  --output catalog
```

`inventory.py` validates original bytes without executing upstream code. It applies
hash-bound reviews and port states, regenerates sources/INDEX and refreshes the
port manifest's catalogue hash. Existing output `ports.json` is the default state
overlay when `--ports` is omitted. Relocated resources retain archive pointers;
planned inventory paths remain distinct from recorded port destinations.

## Verify

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest python -m pytest -q tests
```

Tests use owned fixtures and doubles. Cases needing relocated code skip only when
its catalogue state is `clean_room_pending`; they resume when that state changes.
Shared-helper, non-official, metadata, relocation and launcher checks remain active.
[Native evidence projections](verification/catalog-native-evidence.json) include
historical records for archived ports; offline success is not a new native run,
rendering, destruction or installed-wheel acceptance claim.

## Licences and remaining work

The repository's Apache-2.0 licence applies to its original code. Upstream inputs
keep their own recorded terms. [The per-file ledger](catalog/licenses.json) covers
112 non-official source records, 15 resources and 19 original insight files.
Fourteen non-official resource grants/creator attributions remain unresolved;
see the ledger, [numbered notices](ports/pyqt-examples-LICENSE.md) and
[QtExamples notices](ports/eyllanesc-LICENSE.md). Official notices and old licence
claims reside with the private archive, not the replacement implementations.

The remaining work is independent Apache-2.0 implementation, acceptance checks,
resource review and documentation integration: [PLAN](PLAN.md), [TODO](TODO.md).
