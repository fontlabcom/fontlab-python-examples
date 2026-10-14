---
this_file: README.md
---

# FontLab Python examples

Complete source catalog for planned PythonQt ports of [pyqt/examples](https://github.com/pyqt/examples) and
[eyllanesc/QtExamples](https://github.com/eyllanesc/QtExamples), for use inside running FontLab. Start at the [categorized index](catalog/INDEX.md).

Both pinned collections are fully acquired and verified locally: **1,569 files, 465 Python files**. The public catalog contains provenance and planned mappings;
the upstream originals remain local. **Four entrypoints are native-verified; seven further numbered examples and 56 official demos are implemented and await
native acceptance.** Neither requested collection is complete.

| Collection | Pinned revision | Original files | Python files |
| --- | --- | ---: | ---: |
| pyqt/examples | `83eed0514582c8deb60d9e9e6bff31ceffe4eaeb` | 805 | 308 |
| eyllanesc/QtExamples | `a01fd7d10d45801b10876f94c07aaefb11bc2e12` | 764 | 157 |

The [machine-readable catalog](catalog/sources.json) preserves every logical source identity, exact original byte count, Git blob SHA, SHA-256, attribution and
license evidence, source URL, resource associations and distinct target path. Both `others/matplotlib/Subplot.py` and `subplot.py` have separate mappings that
also remain distinct on a case-insensitive filesystem. Duplicate bytes retain every original mapping.

Static analysis identifies 298 Python entrypoint candidates, 14 ambiguous Python candidates, 153 auxiliary Python files and 3 uncertain QML launcher candidates.
These are not a confirmed executable-example denominator. Static execution-scope analysis excludes deferred bodies; conditions and invoked functions need
review. All imports/API requirements remain catalogued. The 69 shared/repository files have individual records with unresolved ownership; capability needs are
source requirements, not proof of host support.

## Regenerate the inventory

Use Python 3.12 and explicitly supply the two receipts and the verified source roots. The recovery receipt supplies logical-to- storage mappings; unverified
archive extractions are not valid inputs. The tool checks complete receipt/tree accounting, revisions and every original hash before writing output. It never
imports or executes upstream code or a Qt binding.

```sh
python tools/inventory.py \
  --tree-receipt "$TREE_RECEIPT" \
  --recovery-receipt "$RECOVERY_RECEIPT" \
  --source-root "pyqt/examples=$PYQT_SOURCE" \
  --source-root "eyllanesc/QtExamples=$QTEXAMPLES_SOURCE" \
  --output catalog
```

`TREE_RECEIPT` is `examples-upstream-trees.json`; `RECOVERY_RECEIPT` is `examples-source-recovery.json`. Source-root variables must point to the verified
directories described by that receipt, including its case-collision mapping. Repeated runs with unchanged receipts, bytes and interpreter produce identical JSON
and Markdown bytes. Output contains no private source-root paths. Input and output filesystem failures return a portable error name and failure exit code,
without a private path or traceback.

## Verify the catalog tools

The tool uses only Python's standard library. Tests use pytest and owned fixtures; they do not run a corpus example or modify FontLab, fonts or settings.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest \
  python -m pytest -q tests
uvx ruff check tools tests
uvx ruff format --check tools tests
```

## Launch implemented ports

Put this checkout on FontLab's Python module path and install `fontlab-fontlabapp` in FontLab's interpreter. The launcher uses its `OwnedWidget` and the
existing PythonQt/QApplication; no additional Qt binding is installed.

```python
import fontlab_python_examples as examples

examples.available()                 # names, IDs, states and provenance; host-free
handle = examples.launch("QLabel")    # run inside FontLab
handle.widget                        # direct native QLabel
examples.inspect("QLabel")           # JSON-friendly live state
examples.close("QLabel")             # idempotent, only owned UI
```

| Name | Original source ID | Preserved behavior |
| --- | --- | --- |
| `QLabel` | `ce3e17a7a2a03a02` | `Hello World!` label |
| `QVBoxLayout` | `f5ddfd0eaacbf845` | `Top`, then `Bottom` vertically |
| `Signals and Slots` | `79cc15680bc2cebb` | `Click` opens `You clicked the button!` |
| `Qt Designer` | `402068f40005cd66` | Exact original UI, OK/Cancel wiring |
| `PyQt Widgets` | `2d8e8e07a6469499` | Implemented; native acceptance unexecuted |
| `Qt Text Editor` | `a601a41dc5a3c23a` | Implemented; native acceptance unexecuted |
| `Qt dark theme` | `a33bb8c2dce4e115` | Implemented; native acceptance unexecuted |
| `QPainter` | `1151b1cb878f192a` | Implemented; native acceptance unexecuted |
| `QTreeView` | `f5bf995791f1e87b` | Implemented; native acceptance unexecuted |
| `QListView` | `1bf0ade33cd6bf12` | Implemented; native acceptance unexecuted |
| `QAbstractTableModel` | `31fc7691c18d55f2` | Implemented; native acceptance unexecuted |
| `Official classwizard` | `035f3fbd2b81479a` | Implemented; native acceptance unexecuted |
| `Official configdialog` | `3f5f77c0358d9fef` | Implemented; native acceptance unexecuted |
| `Official extension` | `a1c26dbf9f995edb` | Implemented; native acceptance unexecuted |
| `Official findfiles` | `63f2eeefd052f701` | Implemented; native acceptance unexecuted |
| `Official standarddialogs` | `e1a0a829f8f2e311` | Implemented; native acceptance unexecuted |
| `Official tabdialog` | `dab5fd4c94ec518d` | Implemented; native acceptance unexecuted |
| `Official trivialwizard` | `c0d4a173b261a3e5` | Implemented; native acceptance unexecuted |
| `Official basiclayouts` | `2f94fe07de765888` | Implemented; native acceptance unexecuted |
| `Official borderlayout` | `f48955d43ed6196c` | Implemented; native acceptance unexecuted |
| `Official flowlayout` | `675c9f79650d7507` | Implemented; native acceptance unexecuted |
| `Official application` | `7da7020aa7e2732b` | Implemented; native acceptance unexecuted |
| `Official mdi` | `1415facde30a25cf` | Implemented; native acceptance unexecuted |
| `Official sdi` | `eba98690c141a070` | Implemented; native acceptance unexecuted |
| `Official basicdrawing` | `907f39d8bf387501` | Implemented; native acceptance unexecuted |
| `Official codecs` | `19571722ed96aa9c` | Implemented; native acceptance unexecuted |
| `Official customcompleter` | `10ef4dacb4db4080` | Implemented; native acceptance unexecuted |
| `Official i18n` | `eca1cd9ef1528607` | Implemented; native acceptance unexecuted |
| `Official regexp` | `626fd0acec74fd91` | Implemented; native acceptance unexecuted |
| `Official settingseditor` | `9e41e71c41b116a8` | Implemented; native acceptance unexecuted |
| `Official icons` | `505d60a757bbc177` | Implemented; native acceptance unexecuted |
| `Official movie` | `a3b3cbe51c1506c6` | Implemented; native acceptance unexecuted |
| `Official stylesheet` | `876eab33b6a99e31` | Implemented; native acceptance unexecuted |
| `Official tooltips` | `e62ce3eb648cfb4c` | Implemented; native acceptance unexecuted |
| `Official draggableicons` | `5781fa4ba55c884f` | Implemented; native acceptance unexecuted |
| `Official draggabletext` | `700e96dec485e7a8` | Implemented; native acceptance unexecuted |
| `Official fridgemagnets` | `da76600eaea7a121` | Implemented; native acceptance unexecuted |
| `Official draganddrop puzzle` | `c5b4e385cc921da4` | Implemented; native acceptance unexecuted |
| `Official lighting` | `b823a76f79197d84` | Implemented; native acceptance unexecuted |
| `Official chart` | `306c12d5cc1db46c` | Implemented; native acceptance unexecuted |
| `Official editabletreemodel` | `227efef76ed4ac74` | Implemented; native acceptance unexecuted |
| `Official frozencolumn` | `c98ae8ac71886586` | Implemented; native acceptance unexecuted |
| `Official interview` | `090c76a87351e771` | Implemented; native acceptance unexecuted |
| `Official itemviews puzzle` | `878fe9f714df3b5e` | Implemented; native acceptance unexecuted |
| `Official simpletreemodel` | `321f8e535facafde` | Implemented; native acceptance unexecuted |
| `Official addressbook part1` | `e1f313d96e43adff` | Implemented; native acceptance unexecuted |
| `Official addressbook part2` | `55bcde890cd77ed7` | Implemented; native acceptance unexecuted |
| `Official addressbook part3` | `f4d9e2927469223c` | Implemented; native acceptance unexecuted |
| `Official addressbook part4` | `4d19e62d93dd761c` | Implemented; native acceptance unexecuted |
| `Official addressbook part5` | `94ab271d023d1ca3` | Implemented; native acceptance unexecuted |
| `Official addressbook part6` | `2719ebb336f3a29e` | Implemented; native acceptance unexecuted |
| `Official addressbook part7` | `bb1c114d38fb756a` | Implemented; native acceptance unexecuted |

| `Official embeddeddialogs` | `0578c17977b471f1` | Implemented; native acceptance unexecuted |
| `Official mandelbrot` | `0788354954c8e613` | Implemented; native acceptance unexecuted |
| `Official diagramscene` | `1ca857d797199ecf` | Implemented; native acceptance unexecuted |
| `Official animatedtiles` | `1cf57c0f2ac8880a` | Implemented; native acceptance unexecuted |
| `Official stickman` | `243ae486f9528e8c` | Implemented; native acceptance unexecuted |
| `Official waitconditions` | `27709a02d37b9ba9` | Implemented; native acceptance unexecuted |
| `Official states` | `29f6a7d0a3bb6813` | Implemented; native acceptance unexecuted |
| `Official dragdroprobot` | `2cd6ffc2b2ed65bb` | Implemented; native acceptance unexecuted |
| `Official screenshot` | `65d15d1fbc1b15e9` | Implemented; native acceptance unexecuted |
| `Official moveblocks` | `b7283d74afb78218` | Implemented; native acceptance unexecuted |
| `Official semaphores` | `b95b687bbc541207` | Implemented; native acceptance unexecuted |
| `Official easing` | `bd6c8feb783ba845` | Implemented; native acceptance unexecuted |
| `Official systray` | `c1b878b63f80e733` | Implemented; native acceptance unexecuted |
| `Official appchooser` | `de30d23621025fe6` | Implemented; native acceptance unexecuted |
| `Official sharedmemory` | `de35a965dfcfd678` | Blocked: QSharedMemory.detach absent |
| `Official collidingmice` | `fcfaf9667206bbd6` | Implemented; native acceptance unexecuted |

Source IDs also work as names. `get(name)` retrieves a launched handle, including its native widget, retained callbacks and alert owners. Repeated launch
reshows the same owned window. Module state keeps handles alive across isolated external calls. A native window's close button hides it; `close(name)` removes
ownership and schedules native destruction. External parent destruction makes inspection safe. Existing FontLab UI and preferences are not changed.

The click alert uses asynchronous `open()` with example-window modality, keeping FontLab's event loop responsive. Dismissed alerts remain owned until the next
click or named cleanup. Designer uses `QUiLoader`, loading its exact copied XML relative to the port file. Launch fails clearly outside FontLab, without an
existing QApplication, for unknown names, or for known but unported source IDs and source paths.

Ordinary external Python can use [fontlab-remopy](../fontlab-remopy) to run the same calls inside an already running FontLab with its MCP bridge configured.

The [runnable Remopy example](examples/remopy.py) supports external launch, inspect and close calls while adding this checkout to the host module path.

The static [source catalog](catalog/sources.json) stays unchanged. The separate [port manifest](catalog/ports.json) records individual licenses, exact original
identities, resource hashes and implementation/native states. Tests use boundary doubles; they do not count as native acceptance.

## Insights

Eighteen original Apache-2.0 examples provide owned type-design panels. See the [ranked survey](docs/pythonqt-reference- insights.md),
[manifest](catalog/insights.json) and [second-batch controller guide](docs/insights-second-batch.md). Use `examples.launch(name)`, `examples.inspect(name)` and
`examples.close(name)`; `examples.get(name).controls` exposes controls without adding native attributes. Ranks 1–12: `signal-lifetime`, `glyph-list`, `metrics-
table`, `timer-batch`, `contour-canvas`, `owned-key-filter`, `metric-controls`, `glyph-properties`, `sandbox-settings`, `callback-errors`, `owned-dock`,
`contour-scene`. Ranks 13–18: `loaded-glyph-form`, `worker-glyph-queue`, `owned-repl`, `plugin-tokens`, `metrics-undo`, `compiled-slot-exposure`. First-batch
controller evidence is recorded; ranks 13–18 await native acceptance. Settings use `FontLabPythonExamples` / `InsightsSandbox`; console globals, menus and undo
data are owned. Compiled exposure uses existing host bindings and fails clearly if absent. No new dependencies or copied reference code; grants unresolved.

## Licensing and remaining ports

The repository's Apache license does not relicense upstream inputs. Pinned READMEs, actual notices and source headers supply per-file evidence. All 1,569 files
retain **license review pending in the static catalog**; 43 have no recognized declaration. Per-entry source and resource reviews and attribution appear in [the
manifest](catalog/ports.json) and [the numbered-source notice](ports/pyqt-examples-LICENSE.md) and [the official-source notice](ports/pyqt-official-LICENSE.md).
Nearby notices may apply only to specific assets: their association is evidence, not a blanket license assignment. Preserve the original notices and resolve
scope before distributing a port or copying upstream resources.

Four targets retain native acceptance; 63 implemented targets await acceptance. QML (06), standalone fbs/PyQt6 packaging (08), and QtSql/database (15, including
its initializer) have explicit blocked records; shared memory is also blocked by its missing detach API. The gallery (02) preserves its BSD notice with license
review unresolved. Editor styles affect only owned UI. QPainter (10) preserves bullet/audio assets but cannot play QSoundEffect through QtCore/QtGui. See
[second-batch native checks](docs/second-numbered-batch.md). Future ports must use FontLab's existing PythonQt/Qt runtime and QApplication/event loop, without
loading PyQt, PySide or another Qt runtime. QML, WebEngine, multimedia, GStreamer, matplotlib, database, network and platform examples remain in scope. See
[PLAN.md](PLAN.md) and [TODO.md](TODO.md) for the full remaining work.

The [first-batch evidence](verification/first-native-batch.json) records native text/layout/click/Designer acceptance, destruction of all 38 owned objects and
unchanged host state. This proves source loading; wheel installation and other native checks remain required. Current states live in the port manifest.

The 56 official ports use tracked callbacks, async dialogs, isolated host state and 167 exact resource copies. See [adaptations and native checks](docs/pyqt-
official-batch.md). Their BSD headers and GPLv3 collection notice are retained; scope remains unresolved for the BSD-header ports; two new GPL alternatives are
explicit.
