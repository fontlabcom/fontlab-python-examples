---
this_file: README.md
---

# FontLab Python examples

Complete source catalog for planned PythonQt ports of [pyqt/examples](https://github.com/pyqt/examples) and [eyllanesc/QtExamples](https://github.com/eyllanesc/QtExamples), for use inside running FontLab. Start at the [categorized index](catalog/INDEX.md).
Both pinned collections are fully acquired and verified locally: **1,569 files, 465 Python files**. The public catalog contains provenance and planned mappings; the upstream originals remain local. **All 298 Python entrypoint candidates plus the database initializer have port records: 148 implemented and 151 precisely blocked. Four retain recorded native acceptance; 144 implemented records await acceptance.** Collection-wide native acceptance is incomplete; ambiguous/QML/auxiliary candidates remain separate.

| Collection | Pinned revision | Original files | Python files |
| --- | --- | ---: | ---: |
| pyqt/examples | `83eed0514582c8deb60d9e9e6bff31ceffe4eaeb` | 805 | 308 |
| eyllanesc/QtExamples | `a01fd7d10d45801b10876f94c07aaefb11bc2e12` | 764 | 157 |

The [machine-readable catalog](catalog/sources.json) preserves every logical source identity, exact original byte count, Git blob SHA, SHA-256, attribution and license evidence, source URL, resource associations and distinct target path. Both `others/matplotlib/Subplot.py` and `subplot.py` have separate mappings that also remain distinct on a case-insensitive filesystem. Duplicate bytes retain every original mapping.
Static analysis identifies 298 Python entrypoint candidates, 14 ambiguous Python candidates, 153 auxiliary Python files and 3 uncertain QML launcher candidates. These are not a confirmed executable-example denominator. Static execution-scope analysis excludes deferred bodies; conditions and invoked functions need review. All imports/API requirements remain catalogued. The 69 shared/repository files have individual records with unresolved ownership; capability needs are source requirements, not proof of host support.

## Regenerate the inventory

Use Python 3.12 and explicitly supply the two receipts and the verified source roots. The recovery receipt supplies logical-to- storage mappings; unverified archive extractions are not valid inputs. The tool checks complete receipt/tree accounting, revisions and every original hash before writing output. It never imports or executes upstream code or a Qt binding.

```sh
python tools/inventory.py \
  --tree-receipt "$TREE_RECEIPT" \
  --recovery-receipt "$RECOVERY_RECEIPT" \
  --source-root "pyqt/examples=$PYQT_SOURCE" \
  --source-root "eyllanesc/QtExamples=$QTEXAMPLES_SOURCE" \
  --output catalog
```

`TREE_RECEIPT` is `examples-upstream-trees.json`; `RECOVERY_RECEIPT` is `examples-source-recovery.json`. Source-root variables must point to the verified directories described by that receipt, including its case-collision mapping. Repeated runs with unchanged receipts, bytes and interpreter produce identical JSON and Markdown bytes. Output contains no private source-root paths. Input and output filesystem failures return a portable error name and failure exit code, without a private path or traceback.

## Verify the catalog tools

The tool uses only Python's standard library. Tests use pytest and owned fixtures; they do not run a corpus example or modify FontLab, fonts or settings.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --with pytest \
  python -m pytest -q tests
uvx ruff check tools tests
uvx ruff format --check tools tests
```

## Launch implemented ports

Put this checkout on FontLab's Python module path and install `fontlab-fontlabapp` in FontLab's interpreter. The launcher uses its `OwnedWidget` and the existing PythonQt/QApplication; no additional Qt binding is installed.

```python
import fontlab_python_examples as examples
examples.available()                 # names, IDs, states and provenance; host-free handle = examples.launch("QLabel")    # run inside FontLab handle.widget                        # direct native QLabel examples.inspect("QLabel")           # JSON-friendly live state examples.close("QLabel")             # idempotent, only owned UI ```

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
| `Official dockwidgets` | `4efac54bae01fc62` | Implemented; native acceptance unexecuted |
| `Official menus` | `60d40ce5671653cf` | Implemented; native acceptance unexecuted |
| `Official recentfiles` | `09afeea11be83f4f` | Implemented; native acceptance unexecuted |
| `Official separations` | `2d36e0fe43f5d49a` | Implemented; native acceptance unexecuted |
| `Official concentriccircles` | `912e5c751b20ce97` | Implemented; native acceptance unexecuted |
| `Official painterpaths` | `13a6bb9a9d2b9037` | Implemented; native acceptance unexecuted |
| `Official svgviewer` | `b2d717e4d43806d2` | Implemented; native acceptance unexecuted |
| `Official transformations` | `c12a2071adbab88b` | Implemented; native acceptance unexecuted |
| `Official calendar` | `c56cf1699b07b350` | Implemented; native acceptance unexecuted |
| `Official orderform` | `c997677a2bdb4f34` | Implemented; native acceptance unexecuted |
| `Official syntaxhighlighter` | `428c50abcef7adfe` | Implemented; native acceptance unexecuted |
| `Official textedit` | `b34b2f696a977e74` | Implemented; native acceptance unexecuted |
| `Official textobject` | `806fd814a2ea4d46` | Blocked: QTextObjectInterface absent |
| `Official analogclock` | `d6dc56a5318ffe71` | Implemented; native acceptance unexecuted |
| `Official calculator` | `356e4e807f1e789f` | Implemented; native acceptance unexecuted |
| `Official calendarwidget` | `b91effc45f81fbb0` | Implemented; native acceptance unexecuted |
| `Official charactermap` | `499e965d86347920` | Implemented; native acceptance unexecuted |
| `Official digitalclock` | `3040b9f6b267a196` | Implemented; native acceptance unexecuted |
| `Official groupbox` | `f702b62aa47629ad` | Implemented; native acceptance unexecuted |
| `Official imageviewer` | `16456ba02f4b79cc` | Implemented; native acceptance unexecuted |
| `Official lineedits` | `84cb59e07adfae2c` | Implemented; native acceptance unexecuted |
| `Official scribble` | `8e5aa13798c2763c` | Implemented; native acceptance unexecuted |
| `Official shapedclock` | `248e64416b9b218c` | Implemented; native acceptance unexecuted |
| `Official sliders` | `36805750b888fba6` | Implemented; native acceptance unexecuted |
| `Official spinboxes` | `468179092748a72e` | Implemented; native acceptance unexecuted |
| `Official styles` | `9e21c6536fda7a23` | Implemented; native acceptance unexecuted |
| `Official tetrix` | `e63bffc17abf2fde` | Implemented; native acceptance unexecuted |
| `Official wiggly` | `509e781f1267967f` | Implemented; native acceptance unexecuted |
| `Official windowflags` | `136c45cc9f97c218` | Implemented; native acceptance unexecuted |
| `Official delayedencoding` | `43c6c2f6f5f036d3` | Implemented; native acceptance unexecuted |
| `Official dropsite` | `fa6823667fdb918f` | Implemented; native acceptance unexecuted |
| `Official anchorlayout` | `a96a7978c0b9f6ee` | Implemented; native acceptance unexecuted |
| `Official elasticnodes` | `fff97a435b73d548` | Implemented; native acceptance unexecuted |
| `Official padnavigator` | `a58650b5461c0f48` | Implemented; native acceptance unexecuted |
| `Official basicsortfiltermodel` | `9dab02b61cebbdb7` | Implemented; native acceptance unexecuted |
| `Official coloreditorfactory` | `0a3b15766909bdc3` | Implemented; native acceptance unexecuted |
| `Official combowidgetmapper` | `cc95f9719b8e4eda` | Implemented; native acceptance unexecuted |
| `Official customsortfiltermodel` | `029ea0dabe87ae57` | Implemented; native acceptance unexecuted |
| `Official dirview` | `4b8851287931abd0` | Implemented; native acceptance unexecuted |
| `Official fetchmore` | `67170c89593ad35e` | Implemented; native acceptance unexecuted |
| `Official pixelator` | `d50ad6638357e669` | Implemented; native acceptance unexecuted |
| `Official simpledommodel` | `a59dae9770bfbefb` | Implemented; native acceptance unexecuted |
| `Official simplewidgetmapper` | `39de33366209402d` | Implemented; native acceptance unexecuted |
| `Official spinboxdelegate` | `ddb20b1b68b18a91` | Implemented; native acceptance unexecuted |
| `Official spreadsheet` | `bf3b39a8c2df8e94` | Implemented; native acceptance unexecuted |
| `Official stardelegate` | `dc59f268ee01e364` | Implemented; native acceptance unexecuted |
| `Official storageview` | `cf15c3e91cdd8ded` | Implemented; native acceptance unexecuted |
| `Official blockingfortuneclient` | `79f3a23172968ad2` | Implemented; native acceptance unexecuted |
| `Official broadcastreceiver` | `0bba8a80541ab04f` | Implemented; native acceptance unexecuted |
| `Official broadcastsender` | `90721289b8108c4f` | Implemented; native acceptance unexecuted |
| `Official fortuneclient` | `fbb4e3c7288fed7c` | Implemented; native acceptance unexecuted |
| `Official fortuneserver` | `aad57160cfd51894` | Implemented; native acceptance unexecuted |
| `Official http` | `409f3d46a9555f23` | Implemented; native acceptance unexecuted |
| `Official lightmaps` | `d8803c2afaabf3d5` | Implemented; native acceptance unexecuted |
| `Official loopback` | `ebf87d5f5390b0fd` | Implemented; native acceptance unexecuted |
| `Official threadedfortuneserver` | `98f207907001ce47` | Implemented; native acceptance unexecuted |
| `Official webbrowser` | `a1273c8940d43221` | Blocked: PythonQt does not export QAxContainer |
| `Official chat` | `38465a8f4b1a229f` | Blocked: PythonQt does not export QtDBus |
| `Official listnames` | `ab719a6a5c3afe4a` | Blocked: PythonQt does not export QtDBus |
| `Official ping` | `30cfa75ad45b3447` | Blocked: PythonQt does not export QtDBus |
| `Official pong` | `57a381bc8260c85d` | Blocked: PythonQt does not export QtDBus |
| `Official car` | `54c7440bdcdc3dfc` | Blocked: PythonQt does not export QtDBus |
| `Official controller` | `3cf5db95a691d200` | Blocked: PythonQt does not export QtDBus |
| `Official calculatorform` | `27bf65f8b059fd96` | Implemented; native acceptance unexecuted |
| `Official plugins` | `960c701fa6221ac5` | Blocked: PythonQt has no QtDesigner module or QPyDesignerCustomWidgetPlugin/QDesignerCustomWidgetInterface and no PyQt Designer Python plugin loader |
| `Official designer analogclock` | `4d24cd77c74a8801` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official bubbleswidget` | `9941e3c752b3a3b7` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official counterlabel` | `1321540b04f33117` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official datetimeedit` | `7ba49e67588b1329` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official helloglwidget` | `5941e31267112c98` | Blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions() |
| `Official multipagewidget` | `de4979a99c6d0bed` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official polygonwidget` | `773db5c24ae98ffb` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official pydemo` | `bcfa5de0140286d5` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official pythonconsolewidget` | `5125860585e98b3a` | Implemented standalone; Designer integration blocked; native unexecuted |
| `Official localfortuneclient` | `0ad3432ccdca7ac0` | Implemented; native acceptance unexecuted |
| `Official localfortuneserver` | `a14d08fe23965bec` | Implemented; native acceptance unexecuted |
| `Official audiodevices` | `74af8d8d2d7774b8` | Blocked: PythonQt does not export QtMultimedia |
| `Official audiooutput` | `c391afd8516131e1` | Blocked: PythonQt does not export QtMultimedia |
| `Official camera` | `f6d352360ae9bdfb` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `Official player` | `5eb4b9eaa2d5c9dc` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `Official videographicsitem` | `a57a89e523c75b7f` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `Official videowidget` | `481c128fba3a714b` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `Official 2dpainting` | `c82d1af7d1a7b0cf` | Implemented; native acceptance unexecuted |
| `Official grabber` | `303ea3ee09c4677d` | Blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions() |
| `Official hellogl` | `1ad60855ca28f3cc` | Blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions() |
| `Official openglwindow` | `b383fecf912548bb` | Blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions() |
| `Official overpainting` | `fcada4fff6524fcf` | Blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions() |
| `Official textures` | `ed6d42d4faa7e0bb` | Blocked: PythonQt.QtGui.QOpenGLContext lacks versionFunctions() |
| `Official compile-on-the-fly` | `5a8e48d2a1396cea` | Implemented; native acceptance unexecuted |
| `Official load_ui1` | `b7db02f540cc7559` | Implemented; native acceptance unexecuted |
| `Official load_ui2` | `b9660f4ee653ca01` | Implemented; native acceptance unexecuted |
| `Official adding` | `8847cbce50b72500` | Blocked: PythonQt does not export QtQml |
| `Official attached` | `dd226ba9fbb7b330` | Blocked: PythonQt does not export QtQml |
| `Official binding` | `eb7a89f07f63cca7` | Blocked: PythonQt does not export QtQml |
| `Official coercion` | `ad499afe23726248` | Blocked: PythonQt does not export QtQml |
| `Official default` | `6417cdcf1bfd1752` | Blocked: PythonQt does not export QtQml |
| `Official grouped` | `81a6f0d16c203608` | Blocked: PythonQt does not export QtQml |
| `Official methods` | `75ca5ac77ecefd6d` | Blocked: PythonQt does not export QtQml |
| `Official properties` | `d0a18273fa604bb6` | Blocked: PythonQt does not export QtQml |
| `Official signal` | `0a13f60f5f0561db` | Blocked: PythonQt does not export QtQml |
| `Official valuesource` | `738a22ef3062ed51` | Blocked: PythonQt does not export QtQml |
| `Official qtdemo` | `85a56a1f3c25ccca` | Blocked: The full qtdemo launcher delegates to PyQt executables and qmlscene (menumanager.py launchExample/launchQmlExample), including QtQuick/QtQml examples |
| `Official animation` | `835281a1ab864833` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official canvas` | `36246fcbffecdeba` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official abstractitemmodel` | `e1316fee99c63555` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official objectlistmodel` | `68d664f95f48ce52` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official stringlistmodel` | `b64d66dbce7274fe` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official customgeometry` | `34538a4e2600b918` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official chapter1-basics` | `6b1f4f5590a5518a` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official chapter2-methods` | `8d1557cbfed9c7a0` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official chapter3-bindings` | `3cd3713a5dc9f6dc` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official chapter4-customPropertyTypes` | `831ac8ea61da03f3` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official chapter5-listproperties` | `b88e7eb0fcb53264` | Blocked: PythonQt does not export QtQuick / QtQml |
| `Official modelviewclient` | `4dbe92cd1e720dce` | Blocked: PythonQt does not export QtRemoteObjects |
| `Official modelviewserver` | `781a3a959215eb81` | Blocked: PythonQt does not export QtRemoteObjects |
| `Official directconnectdynamicclient` | `54cbd9afababdf71` | Blocked: PythonQt does not export QtRemoteObjects |
| `Official directconnectdynamicserver` | `2f1e2f679775d89e` | Blocked: PythonQt does not export QtRemoteObjects |
| `Official registryconnecteddynamicclient` | `333f0272885ca1b7` | Blocked: PythonQt does not export QtRemoteObjects |
| `Official registryconnecteddynamicserver` | `b83377c9b48aec14` | Blocked: PythonQt does not export QtRemoteObjects |
| `Official cachedtable` | `0b0d8d2fae153e5e` | Blocked: PythonQt does not export QtSql |
| `Official querymodel` | `2c4c366f259d7d80` | Blocked: PythonQt does not export QtSql |
| `Official relationaltablemodel` | `9030a87a532b8d8f` | Blocked: PythonQt does not export QtSql |
| `Official tablemodel` | `0677ebfd7fa2cc60` | Blocked: PythonQt does not export QtSql |
| `Official domtraversal` | `8d5ea81a74e30222` | Blocked: PythonQt does not export QtWebKit / QtWebKitWidgets |
| `Official fancybrowser` | `f4000cf8ca288375` | Blocked: PythonQt does not export QtWebKit / QtWebKitWidgets |
| `Official formextractor` | `6ed36280660df7ea` | Blocked: PythonQt does not export QtWebKit / QtWebKitWidgets |
| `Official framecapture` | `ca47b83fbf3f31b9` | Blocked: PythonQt does not export QtWebKit / QtWebKitWidgets |
| `Official previewer` | `47298251b3c83ecf` | Blocked: PythonQt does not export QtWebKit / QtWebKitWidgets |
| `Official simpleselector` | `ae16288fede27692` | Blocked: PythonQt does not export QtWebKit / QtWebKitWidgets |
| `Official schema` | `1e5d0f7289e1b36e` | Implemented; native acceptance unexecuted |

| `QtExamples charts/areachart/main` | `93131a29a3b71ea3` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples charts/audio/main` | `e1c73422208670cb` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples charts/barchart/main` | `9fed8c2f3765272b` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples charts/barmodelmapper/main` | `c862c1b57a0a0412` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples charts/boxplotchart/main` | `f9107c0d26ffc4aa` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples charts/callout/main` | `6bd9cbb60a6ac008` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples charts/candlestickchart/main` | `032d404c69db6baa` | Blocked: PythonQt does not export QtCharts (QtChart) |
| `QtExamples corelib/ipc/localfortuneclient/main` | `4bc27e706ac146f5` | Implemented; native acceptance unexecuted |
| `QtExamples corelib/ipc/localfortuneserver/main` | `cb1871959e42607b` | Implemented; native acceptance unexecuted |
| `QtExamples corelib/ipc/sharedmemory/dialog_ui` | `04e8e49f95de6cf5` | Blocked: PythonQt.QtCore.QSharedMemory lacks detach() |
| `QtExamples corelib/ipc/sharedmemory/main` | `24b0b2aa8998d701` | Blocked: PythonQt.QtCore.QSharedMemory lacks detach() |
| `QtExamples dbus/pingpong/ping` | `7bddaa324636868a` | Blocked: PythonQt does not export QtDBus |
| `QtExamples dbus/pingpong/pong` | `fa5e7696ac61b89f` | Blocked: PythonQt does not export QtDBus |
| `QtExamples demos/calqlatr/main` | `9d1a670d70c19b6a` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples demos/clocks/main` | `3299c18eadf92b5d` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples demos/coffee/main` | `f581c1e4f121df88` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples demos/maroon/main` | `2529316479664459` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples demos/photosurface/main` | `6386ec6f1ca4ffd4` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples embedded/lightmaps/main` | `92fc3cf4b5dd009c` | Implemented; native acceptance unexecuted |
| `QtExamples embedded/styleexample/main` | `631cc1bc310c00b9` | Implemented; native acceptance unexecuted |
| `QtExamples gui/rasterwindow/main` | `3525151ac8d550f5` | Blocked: PythonQt.QtGui.QGradient lacks the NightFade preset and its preset constructor overload, required by RasterWindow.renderNow for its exact background |
| `QtExamples main` | `a207ef153f0b81b7` | Blocked: The original launcher spawns sys.executable with a PyQt5/PySide2 binding and launches quickcontrols2/gallery, which requires absent QtQml/QtQuick/QtQuickControls2 |
| `QtExamples multimedia/audiodevices/audiodevicesbase_ui` | `0d72445fb116793d` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `QtExamples multimedia/audiodevices/main` | `307534c4e8e2211c` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `QtExamples network/googlesuggest/main` | `eea833917398267a` | Blocked: PythonQt.QtCore has no QXmlStreamReader, required by GSuggestCompletion.handleNetworkData to parse suggestions |
| `QtExamples network/loopback/main` | `ecc2e23449331df1` | Implemented; native acceptance unexecuted |
| `QtExamples positioning/logfilepositionsource/main` | `ccad55f9e06bfa93` | Blocked: PythonQt does not export QtPositioning |
| `QtExamples qpa/qrasterwindow/main` | `0b7e380ab45addbd` | Blocked: PythonQt.QtGui.QMatrix4x4 exposes neither __mul__ nor a matrix-product method |
| `QtExamples qpa/windows/main` | `b1c25455dbcb6bac` | Implemented; native acceptance unexecuted |
| `QtExamples quickcontrols2/flatstyle/main` | `8284e0348b6f7020` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples quickcontrols2/gallery/main` | `b4d27c5a05969f77` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples quickcontrols2/imagine/automotive/main` | `f5ecef06968ffad8` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples quickcontrols2/imagine/musicplayer/main` | `bd4a25944ae5b2d7` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples quickcontrols2/swipetoremove/main` | `9e402cdc525108dd` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples serialport/cenumerator/main` | `3ed66f4363a81cf2` | Blocked: PythonQt does not export QtSerialPort |
| `QtExamples serialport/enumerator/main` | `b2127700642ffb25` | Blocked: PythonQt does not export QtSerialPort |
| `QtExamples sql/cachedtable/main` | `a3c7c0e56d0452cf` | Blocked: PythonQt does not export QtSql |
| `QtExamples sql/drilldown/main` | `5b93264cdefad0d7` | Blocked: PythonQt does not export QtSql |
| `QtExamples sql/sqlwidgetmapper/main` | `fd7c0bbed85eb2d4` | Blocked: PythonQt does not export QtSql |
| `QtExamples webengine/customdialogs/main` | `b92988bc55b506ee` | Blocked: PythonQt does not export QtQml / QtQuick / QtWebEngine |
| `QtExamples webengine/lifecycle/main` | `ea0deb959e907448` | Blocked: PythonQt does not export QtQml / QtQuick / QtWebEngine |
| `QtExamples webengine/minimal/main` | `da960851c5ad3baa` | Blocked: PythonQt does not export QtQml / QtQuick / QtWebEngine |
| `QtExamples webengine/recipebrowser/main` | `5646535663e933c0` | Blocked: PythonQt does not export QtQml / QtQuick / QtWebEngine |
| `QtExamples webenginewidgets/contentmanipulation/main` | `a4f928dfc9be8596` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/cookiebrowser/cookiedialog_ui` | `e6abb656a88ccad4` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/cookiebrowser/cookiewidget_ui` | `1e800054206a98ec` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/cookiebrowser/main` | `0dfe1b3b36d41c8d` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/cookiebrowser/mainwindow_ui` | `8460861d4a65f625` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/html2pdf/main` | `1f671605e1034b71` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/maps/main` | `72838df47d1eddc0` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/markdowneditor/main` | `a7eae99cebfb1806` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/markdowneditor/mainwindow_ui` | `2253cce5a4c3a077` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/minimal/main` | `23d091dcf5a72224` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/notifications/main` | `c9510fb6daa7d1bd` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/printme/main` | `7fece60acaf2b392` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/spellchecker/main` | `856b2b33c69b4e19` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples webenginewidgets/webui/main` | `11ec97a8c43a5283` | Blocked: PythonQt does not export QtWebEngineCore / QtWebEngineWidgets |
| `QtExamples websockets/sslechoserver/main` | `768c423bdd1fa074` | Blocked: PythonQt does not export QtWebSockets |
| `QtExamples customcompleter/google_search` | `edeef5f840c20e15` | Implemented; native acceptance unexecuted |
| `QtExamples dynamicqmltable/main` | `08ba2f1b1fe02894` | Blocked: PythonQt does not export QtQml / QtQuick |
| `QtExamples gst_pipeline/main` | `a0ac1b252a14609e` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `QtExamples matplotlib/Subplot` | `f13380d705146bff` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/barchart_demo` | `52871219c50cdd21` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/date` | `7cc9bd76e925db18` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/ellipse_demo` | `b76dc05cb743e9fc` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/fill` | `43f4640a040ded3e` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/histogram_features` | `26b75bfff47f567d` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/image_demo` | `5354655012c2060e` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/legend` | `6cb023a08571bf96` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/log_demo` | `1ffcdfb872b0e689` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/main` | `8fc6773f10b89095` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas and NavigationToolbar2QT, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/path_patch` | `5c181bebc7c9773c` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/pcolormesh_levels` | `e2f27c6394aa70c8` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/pie_features` | `5d8303b0b2237124` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/plot_streamplot` | `19398065f86e2762` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/polar_demo` | `80aa961de86e1704` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/scatter_demo2` | `2588c05ccd043d91` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/simple_plot` | `8cb9580232bd8081` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/subplot` | `207f7ce534696c20` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/surface3d` | `96777c686c66d526` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/table_demo` | `d82b14fd5e1eb010` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/tex_demo` | `ee1562b25c092ee8` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/buttons` | `60a3d030c4744735` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/check_buttons` | `f5d13b3c5b699ab3` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/cursor` | `620da7edd0cd23fc` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/lasso_selector_demo` | `c6effccd6f31f416` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/menu` | `f2767c945bece214` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/multicursor` | `21a081a01365c096` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/radio_buttons` | `22be270b0ff2abf7` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/rectangle_selector` | `01be5e33878e4940` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/slider_demo` | `9007853b5b845ed9` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples matplotlib/widgets/span_selector` | `1862a5f7d89bd9b6` | Blocked: The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt |
| `QtExamples not_classified/1/main` | `b3c5b8f7bcf09a1d` | Blocked: PythonQt does not export QtMultimedia / QtMultimediaWidgets |
| `QtExamples qmlvideoviewer/main` | `e9392311a500d3dd` | Blocked: PythonQt does not export QtQml / QtMultimedia |
| `PyQt Thread 01_single_threaded` | `1e79bddb6d52574d` | Implemented; native acceptance unexecuted |
| `PyQt Thread 02_multithreaded` | `88fa78cafb505cfa` | Implemented; native acceptance unexecuted |
| `PyQt Thread 03_with_threadutil` | `83bc55d45ae367d0` | Implemented; native acceptance unexecuted |

Source IDs also work as names. `get(name)` retrieves a launched handle, including its native widget, retained callbacks and alert owners. Repeated launch reshows the same owned window. Module state keeps handles alive across isolated external calls. A native window's close button hides it; `close(name)` removes ownership and schedules native destruction. External parent destruction makes inspection safe. Existing FontLab UI and preferences are not changed.
The click alert uses asynchronous `open()` with example-window modality, keeping FontLab's event loop responsive. Dismissed alerts remain owned until the next click or named cleanup. Designer uses `QUiLoader`, loading its exact copied XML relative to the port file. Launch fails clearly outside FontLab, without an existing QApplication, for unknown names, or for known but unported source IDs and source paths.
Ordinary external Python can use [fontlab-remopy](../fontlab-remopy) to run the same calls inside an already running FontLab with its MCP bridge configured.
The [runnable Remopy example](examples/remopy.py) supports external launch, inspect and close calls while adding this checkout to the host module path.
The static [source catalog](catalog/sources.json) stays unchanged. The separate [port manifest](catalog/ports.json) records individual licenses, exact original identities, resource hashes and implementation/native states. Tests use boundary doubles; they do not count as native acceptance.

## Insights

Eighteen original Apache-2.0 examples provide owned type-design panels. See the [ranked survey](docs/pythonqt-reference-insights.md), [manifest](catalog/insights.json) and [second-batch controller guide](docs/insights-second-batch.md). Use `examples.launch(name)`, `examples.inspect(name)` and `examples.close(name)`; `examples.get(name).controls` exposes controls without adding native attributes. Ranks 1–12: `signal-lifetime`, `glyph-list`, `metrics- table`, `timer-batch`, `contour-canvas`, `owned-key-filter`, `metric-controls`, `glyph-properties`, `sandbox-settings`, `callback-errors`, `owned-dock`, `contour-scene`. Ranks 13–18: `loaded-glyph-form`, `worker-glyph-queue`, `owned-repl`, `plugin-tokens`, `metrics-undo`, `compiled-slot-exposure`. First-batch controller evidence is recorded; ranks 13–18 await native acceptance. Settings use `FontLabPythonExamples` / `InsightsSandbox`; console globals, menus and undo data are owned. Compiled exposure uses existing host bindings and fails clearly if absent. No new dependencies or copied reference code; grants unresolved.

## Licensing and remaining ports

The repository's Apache license does not relicense upstream inputs. Pinned READMEs, actual notices and source headers supply per-file evidence. All 1,569 files retain **license review pending in the static catalog**; 43 have no recognized declaration. Per-entry source and resource reviews and attribution appear in [the manifest](catalog/ports.json) and [the numbered-source notice](ports/pyqt-examples-LICENSE.md) and [the official-source notice](ports/pyqt-official-LICENSE.md) and [QtExamples notice](ports/eyllanesc-LICENSE.md). Nearby notices may apply only to specific assets: their association is evidence, not a blanket license assignment. Preserve the original notices and resolve scope before distributing a port or copying upstream resources.
Four targets retain recorded native acceptance; 144 implemented targets await acceptance. QML (06), standalone fbs/PyQt6 packaging (08), and QtSql/database (15, including its initializer) have explicit blocked records; shared memory is also blocked by its missing detach API, and textobject by the absent QTextObjectInterface. The gallery (02) preserves its BSD notice with license review unresolved. Editor styles affect only owned UI. QPainter (10) preserves bullet/audio assets but cannot play QSoundEffect through QtCore/QtGui. See [second-batch native checks](docs/second-numbered-batch.md). Future ports must use FontLab's existing PythonQt/Qt runtime and QApplication/event loop, without loading PyQt, PySide or another Qt runtime. QML, WebEngine, multimedia, GStreamer, matplotlib, database, network and platform examples remain in scope. See [PLAN.md](PLAN.md) and [TODO.md](TODO.md) for the full remaining work.
The [first-batch evidence](verification/first-native-batch.json) records native text/layout/click/Designer acceptance, destruction of all 38 owned objects and unchanged host state. This proves source loading; wheel installation and other native checks remain required. Current states live in the port manifest.
The 127 official ports use tracked callbacks, async dialogs, isolated host state and 244 exact resource copies; 60 further official entrypoints are precisely blocked. All 187 official entrypoints are accounted for; native acceptance remains a separate gate. See [adaptations and native checks](docs/pyqt-official-batch.md). Their BSD headers and GPLv3 collection notice are retained; scope remains unresolved for the BSD-header ports; five GPL alternatives are explicit.

Batch 9 adds 10 implementations and 87 blockers for all remaining 97 requested
entrypoints. The [per-entry table and native acceptance checklists](docs/pyqt-official-batch.md#batch-9-remaining-97-entrypoints) retain exact identities, paths, licences and adaptations. No native acceptance or collection completion is inferred from offline tests.
