---
this_file: docs/pythonqt-reference-insights.md
---

# PythonQt reference insights for FontLab 9

2026-10-14. Ranked by usefulness for safe type-design panels, then availability
in the measured host, then added coverage beyond existing ports. All 18
have original Apache-2.0 examples. First-batch native evidence is recorded in the
manifest; ranks 13–18 remain **unexecuted** for controller acceptance.
Launch names are slugs in [insights.json](../catalog/insights.json). Every build
accepts the injected PythonQt module and returns an ExampleHandle.

## Survey method and limits

Read README, PLAN, WORK, CHANGELOG, handle/launcher, ports.json, QLabel and QPainter
ports, plus existing tests/doubles. Read every listed Python file as bytes/text
through a systematic scanner, collecting numbered signal/lifetime/model/painting/
settings/event/plugin matches. Contextual excerpts were then reviewed per source,
with longer focused reads of the repeating TypeRig, Director, Slicer, Naali,
pyTSon and graphics-view implementations. Byte reads are not 895 deep reviews.
No third-party example was imported, executed, edited or copied.

Priority order: jcfr_PythonQt → kateliev_TypeRig → RobotLocomotion_director →
Slicer → Naali/Tundra → CsoundQt, then the remaining sources. Forks and vendored
Director copies repeat evidence rather than supply independent host validation.
The supplied manifest contains **895 files in 29 source entries** (rather than
28). The table reports files actually read by the scanner, not all Python files
in each upstream repository.

The manifest contains paths under `license_files`, **no licence identifiers or
licence text**. Those licence files are absent from this read-only corpus.
Consequently each cited source grant is explicitly unresolved; filename evidence
is retained instead of guessing MIT/BSD/GPL/LGPL. This does not affect the licence
of our original code, and is not permission to copy any reference implementation.
Individual file headers can have narrower terms: VeloView's WrapPythonQt.py has
an Apache-2.0 notice, but it cannot establish a blanket source licence.

## Binding contract

FontLab 9 has Python 3.11 / Qt 5.15. Widgets and the two model bases used here
are in PythonQt.QtGui; QObject is in PythonQt.private. Qt properties are
attributes, not getters. Native class instances reject new Python attributes;
only Python subclasses may add fields. Controls are retained on the plain Python
ExampleHandle (`get(name).controls`), never added to a native widget. Protected
base event calls use explicit native bases.
FontLab owns QApplication and its event loop. No build constructs an application,
runs exec(), uses worker Qt calls, or changes fonts, host preferences or Output.

ExampleHandle stops timers/removes filters, disconnects recorded signals, clears
callbacks/inspect/model references, releases owned wrapper references, then closes
its native owner. New builders share only a small rollback context manager:
failed builds close the partial owned root. Parent-owned children are not separately
deleted. A native owner already destroyed is not called during timer/filter cleanup.
The settings example writes one key only after an explicit click, in an isolated
namespace. Its own persistence is intentional; Reset removes that sample key.

Official API documentation consulted before implementation:
[PythonQt](https://mevislab.github.io/pythonqt/),
[QObject](https://doc.qt.io/qt-5/qobject.html),
[QTimer](https://doc.qt.io/qt-5/qtimer.html),
[QStringListModel](https://doc.qt.io/qt-5/qstringlistmodel.html),
[QAbstractTableModel](https://doc.qt.io/qt-5/qabstracttablemodel.html),
[QPainterPath](https://doc.qt.io/qt-5/qpainterpath.html),
[QSettings](https://doc.qt.io/archives/qt-5.15/qsettings.html),
[QDockWidget](https://doc.qt.io/qt-5/qdockwidget.html), and
[QGraphicsView](https://doc.qt.io/qt-5/qgraphicsview.html).
C++ contracts guide method arguments and lifetime; measured FontLab facts override
module-placement assumptions. Existing Qt/PythonQt supplies these techniques;
no extra package or runtime dependency is needed.

## Ranked catalogue

### 1. String-signature connects and owned wrapper lifetime

Category: Signals and ownership. Example: `signal-lifetime`.

**What and FontLab value.** Connect a named Qt signal to a retained Python callable, then disconnect that exact pair before releasing child wrappers or deleting the owner. A metrics-preview button is a small example of the same lifetime contract used by real panels.

**PythonQt gotcha.** PythonQt accepts string signatures and bound signals; overload spelling and callback arity must match. Keep Python references as well as Qt parents. A wrapper is not proof that its C++ object is alive; never use Python id() as a durable native identity. Clear subclass-held wrappers before deletion.

**Existing coverage.** Covered: Signals and Slots; all editor/chat/gallery connections; ExampleHandle. New example makes the lifecycle explicit.

- `_reference/jcfr_PythonQt/examples/PyGettingStarted/GettingStarted.py:21` — source licence **unresolved**; manifest evidence: `COPYING`.
- `_reference/Slicer_SlicerGitSVNArchive/Base/Python/slicer/ScriptedLoadableModule.py:114` — source licence **unresolved**; manifest evidence: `License.txt`.

### 2. Model/view separation with QStringListModel

Category: Models and views. Example: `glyph-list`.

**What and FontLab value.** Keep glyph names in a model rather than populate a visual list independently. A prefix filter replaces the list atomically; the inspection reads the live model. This transfers the shared-model approach found in file-transfer views to type-design data.

**PythonQt gotcha.** The corpus uses richer custom/proxy models, not necessarily QStringListModel. FontLab placement is QtGui.QStringListModel, despite Qt C++ documentation placing it in QtCore. Parent and retain the model; its Qt view does not own it by setModel alone.

**Existing coverage.** Covered: QListView; new glyph filter adds observable replacement.

- `_reference/exp111_pyTSon-Scripts/include/ts3widgets/filetransfer.py:660` — source licence **unresolved**; manifest evidence: no licence file recorded.

### 3. Read-only QAbstractTableModel callbacks

Category: Models and views. Example: `metrics-table`.

**What and FontLab value.** Expose immutable glyph advance/left-bearing rows through table-model callbacks. Numeric data remains numeric, headers are supplied separately, and invalid indexes or roles return no data. Sample values avoid reading or changing a font.

**PythonQt gotcha.** Use QtGui.QAbstractTableModel in this host. rowCount/columnCount return zero for valid parents; data checks bounds and role. Native virtual dispatch is an acceptance gate: Python method calls in doubles cannot establish that C++ calls reach them.

**Existing coverage.** Covered: QAbstractTableModel; new example applies it to synthetic metrics.

- `_reference/exp111_pyTSon-Scripts/include/ts3widgets/filetransfer.py:240` — source licence **unresolved**; manifest evidence: no licence file recorded.

### 4. QTimer-driven bounded GUI work

Category: Scheduling. Example: `timer-batch`.

**What and FontLab value.** Process one sample glyph per timer tick and stop at completion. This keeps the GUI event loop responsive and the build well below the run_python deadline without sleep or processEvents loops.

**PythonQt gotcha.** Parent the QTimer, track timeout connection, stop before disconnect/delete. Prefer an instance to static singleShot: Slicer documents a property/static-name collision. Work itself must be short; a timer cannot make a long callback asynchronous.

**Existing coverage.** Covered: PyQt Widgets timer and three chat examples; new example bounds local work without workers.

- `_reference/RobotLocomotion_director/src/python/director/timercallback.py:25` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.
- `_reference/Slicer_SlicerGitSVNArchive/Base/Python/slicer/slicerqt.py:158` — source licence **unresolved**; manifest evidence: `License.txt`.

### 5. Custom painting with genuine QPainterPath

Category: Rendering. Example: `contour-canvas`.

**What and FontLab value.** Construct a genuine QPainterPath from an original synthetic outline and paint it in an owned canvas. This is the basis of contour previews and overlays without altering glyph data.

**PythonQt gotcha.** TypeRig warns that an FL-internal closedPath can wrap as void* and be rejected by QPainter. Build real Qt paths. Call the native base paintEvent explicitly, never super().paintEvent; end the painter in finally. Coordinates here are screen coordinates; font-space previews need a Y flip.

**Existing coverage.** Partly covered: QPainter pixmap overlay; genuine vector contour construction is new.

- `_reference/kateliev_TypeRig/Scripts/TypeRig Tools/TR-DeltaPreview.py:21` — source licence **unresolved**; manifest evidence: `LICENSE`.

### 6. QObject event filter scoped to owned widget

Category: Input. Example: `owned-key-filter`.

**What and FontLab value.** Install a retained observer on a single owned line edit. Record a bounded history of key text and return False so normal editing continues. Useful for diagnosing shortcut/input behavior without intercepting FontLab globally.

**PythonQt gotcha.** Director relies on compiled ddPythonEventFilter; pyTSon also describes a host-specific bridge. Neither is a FontLab API. The original example uses qt.private.QObject and eventFilter; verify native override delivery. Remove the filter before teardown; do not retain event objects. Identity comparison to the one target must be verified in native dispatch.

**Existing coverage.** New; no existing port has an owned event filter.

- `_reference/RobotLocomotion_director/docs/sphinx/tutorials/robot/normalSelectionWidget.py:28` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.
- `_reference/exp111_pyTSon-Scripts/include/pythonqtpytson.py:5` — source licence **unresolved**; manifest evidence: no licence file recorded.

### 7. Signal blocking to avoid control feedback

Category: Signals and state. Example: `metric-controls`.

**What and FontLab value.** Mirror an advance value between a spin box and slider. Block only the destination while setting its value, preventing recursive signal feedback and repeated expensive previews.

**PythonQt gotcha.** blockSignals returns the previous state: restore it in finally rather than unconditionally unblock. Read value as an attribute. Track both valueChanged connections and disconnect each exact lambda.

**Existing coverage.** Partly covered: gallery controls; explicit feedback prevention is new.

- `_reference/kateliev_TypeRig/Lib/typerig/proxy/fl/gui/widgets.py:327` — source licence **unresolved**; manifest evidence: `LICENSE`.

### 8. Qt attributes and dynamic QObject properties

Category: Signals and state. Example: `glyph-properties`.

**What and FontLab value.** Read/write ordinary Qt properties as attributes and attach a dynamic glyphRole tag to an owned label. Toggle its role and displayed caption together; metadata can drive panel behavior.

**PythonQt gotcha.** QObject.setProperty may return False when successfully adding a new dynamic property. Read it back with property(name). Do not confuse QObject properties with Director's application-level setProperty API. Avoid putting native pointers in dynamic values; removal may need host-specific QVariant conversion, as Naali notes.

**Existing coverage.** Attributes covered across existing ports; dynamic QObject metadata is new.

- `_reference/Belsepubi_naali/bin/pymodules/core/componentpropertyadder.py:53` — source licence **unresolved**; manifest evidence: `license.txt`.

### 9. QSettings persistence in an isolated namespace

Category: Persistence. Example: `sandbox-settings`.

**What and FontLab value.** Persist a proof sample explicitly in an example-owned organisation/application. Build reads only; Save writes one key, Reset removes that key. Relaunch demonstrates persistence without changing FontLab preferences.

**PythonQt gotcha.** Never use QSettings() defaults, never set application-wide names. Use FontLabPythonExamples/InsightsSandbox, disable fallbacks, parent the object, sync on explicit action and inspect status. Preserve Unicode as a string; do not assume persisted QVariant values have the original Python type.

**Existing coverage.** New; no existing port persists settings.

- `_reference/RobotLocomotion_director/src/python/director/robotposegui.py:610` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.

### 10. Narrow callback error handling in owned UI

Category: Callback boundaries. Example: `callback-errors`.

**What and FontLab value.** Parse an advance at the click boundary; rejected input preserves the previous valid value and displays an error inside the owned panel. Successful input clears it. Font designers can test numbers safely before any real operation.

**PythonQt gotcha.** Callbacks execute after build has returned. Catch only expected conversion/range errors inside the callback; launcher error handling does not cover later signals. Do not print to or clear FontLab Output. Build failures still require owned rollback.

**Existing coverage.** Partly covered: editor I/O errors and chat worker errors; owned numeric parsing is new.

- `_reference/RobotLocomotion_director/src/python/director/asynctaskqueue.py:72` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.

### 11. Dock/panel composition without host UI mutation

Category: Panel composition. Example: `owned-dock`.

**What and FontLab value.** Compose an owned QMainWindow, central control and QDockWidget containing sample metrics. A dock can float/redock or be hidden while its native parent maintains ownership.

**PythonQt gotcha.** Widgets live in QtGui, not QtWidgets. Director's getMainWindow/addWidgetToViewMenu are host-specific. The example never discovers or reparents FontLab windows, never saves host dock state, and attaches nothing to FontLab's menu. Verify floating windows are also destroyed on named close.

**Existing coverage.** Partly covered: editors use QMainWindow; dock composition is new.

- `_reference/RobotLocomotion_director/src/python/director/applogic.py:78` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.

### 12. QGraphicsScene ownership and view navigation

Category: Rendering. Example: `contour-scene`.

**What and FontLab value.** Put a synthetic contour and two metric guides into an owned QGraphicsScene and display it in QGraphicsView with drag navigation. This separates reusable vector content from view transforms.

**PythonQt gotcha.** Scene owns items; view.setScene does not transfer scene ownership. Parent scene and view to the owned root. Do not separately delete scene-owned items. Value-type QPainterPath needs no QObject deleteLater. Corpus graphics examples include broken constructors/base calls; use them as technique evidence, not recipes.

**Existing coverage.** New; existing QPainter does not use a graphics scene.

- `_reference/knossos-project_knossos/python/examples/graphics_view.py:6` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.

### 13. QUiLoader and object-name lookup

Category: Forms and discovery. Example: `loaded-glyph-form`; native acceptance unexecuted.

**What and FontLab value.** Load an owned .ui and retrieve controls by objectName; this is valuable for larger FontLab panels designed visually.

**PythonQt gotcha.** PythonQt is not PyQt uic: compiled-resource paths in Director do not exist here. QFile open, loader construction and load can each fail. Close/delete temporaries in finally, parent the result and track runtime wiring. Slicer warns text can name a Qt slot rather than a property.

**Existing coverage.** Covered: Qt Designer, exact resource with temporary cleanup.

- `_reference/RobotLocomotion_director/src/python/director/affordancepanel.py:39` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.
- `_reference/Slicer_SlicerGitSVNArchive/Base/Python/slicer/util.py:244` — source licence **unresolved**; manifest evidence: `License.txt`.

### 14. Worker-to-GUI queue hand-off

Category: Scheduling. Example: `worker-glyph-queue`; native acceptance unexecuted.

**What and FontLab value.** Send plain data from a Python worker into a queue, then drain bounded amounts in a GUI timer. Useful for future file or network tasks that genuinely block.

**PythonQt gotcha.** Never call Qt on workers, even QSettings here. Timeout/cancel blocking I/O, join the worker before disconnect and deletion. Naali uses Python 2 Queue; use the standard Python 3 queue module. Do not transplant its remote scene operations.

**Existing coverage.** Covered: multithreaded chat and threadutil ports; worker-glyph-queue now provides a bounded local demonstration.

- `_reference/Belsepubi_naali/bin/pymodules/localscene/localscene.py:40` — source licence **unresolved**; manifest evidence: `license.txt`.
- `_reference/Belsepubi_naali/bin/pymodules/localscene/localscene.py:234` — source licence **unresolved**; manifest evidence: `license.txt`.

### 15. Owned console/REPL widgets

Category: Console integration. Example: `owned-repl`; native acceptance unexecuted.

**What and FontLab value.** Expose an interactive scripting surface inside an owned panel for inspecting sample data. Director and Naali retain consoles and reshow them rather than construct duplicates.

**PythonQt gotcha.** Embedded consoles are host extensions, not a portable PythonQt QtGui class. Their globals and side effects belong to their host. A future example should use its own namespace and text buffer; do not redirect stdout or alter FontLab Output. Evaluation can block and should not be introduced casually.

**Existing coverage.** The new owned-repl supports sample expressions/statements; Qt Text Editor remains an editor.

- `_reference/RobotLocomotion_director/src/python/director/mainwindowapp.py:37` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.
- `_reference/Belsepubi_naali/bin/pymodules/usr/command.py:1510` — source licence **unresolved**; manifest evidence: `license.txt`.

### 16. Registration and explicit unload

Category: Plugin lifecycle. Example: `plugin-tokens`; native acceptance unexecuted.

**What and FontLab value.** Keep callback/plugin objects in a registry and give them an unload hook that reverses every subscription. This mirrors named launch/get/close and supports reshowing one panel.

**PythonQt gotcha.** Slicer module-manager and pyTSon callback proxies are private host APIs. Persistent Python modules can outlive native windows. Retain exact instances, unregister before native deletion, make close repeatable; do not register plugins into FontLab in these examples.

**Existing coverage.** Covered locally by module-retained launcher handles; plugin-tokens now adds explicit install/unload inside an owned menu, with no FontLab registration.

- `_reference/Slicer_SlicerGitSVNArchive/Base/Python/slicer/ScriptedLoadableModule.py:99` — source licence **unresolved**; manifest evidence: `License.txt`.
- `_reference/exp111_pyTSon-Scripts/include/pluginhost.py:420` — source licence **unresolved**; manifest evidence: no licence file recorded.

### 17. Undo integration

Category: Document edits. Example: `metrics-undo`; native acceptance unexecuted.

**What and FontLab value.** Pair real document edits with a deliberate undo/history record. Qt QUndoStack/QUndoView demonstrates UI history; TypeRig documents FontLab object updates and undo messages.

**PythonQt gotcha.** A Qt undo stack does not create FontLab undo history. TypeRig has historical workarounds; verify current FontLab APIs before any document mutation. These examples use synthetic data only and deliberately perform no real undoable font edits.

**Existing coverage.** metrics-undo now uses QUndoStack on owned sample data. FontLab document undo remains outside scope.

- `_reference/RobotLocomotion_director/src/python/director/mainwindowapp.py:444` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.
- `_reference/kateliev_TypeRig/Lib/typerig/proxy/fl/objects/glyph.py:772` — source licence **unresolved**; manifest evidence: `LICENSE`.

### 18. C++ decorators, slots and metaobject exposure

Category: Binding extensions. Example: `compiled-slot-exposure`; native acceptance unexecuted.

**What and FontLab value.** Compiled PythonQt decorators expose additional native methods/constructors; Python callable slots need no PyQt decorator for ordinary signal connections. Wrapper generators show why exported APIs differ between hosts.

**PythonQt gotcha.** PythonQt decorators are not PyQt @pyqtSlot or PySide @Slot. The corpus generator emits C++ adapters; it is not something to run in FontLab. No portable Python Slot decorator was established by the scan. Do not invent one or assume a class available in Slicer/Director is wrapped in FontLab.

**Existing coverage.** compiled-slot-exposure now exercises existing constructors, a wrapped QWidget non-slot method and native QLineEdit.clear(). Compiling new decorators remains outside the runtime build.

- `_reference/RobotLocomotion_director/src/app/WrapPythonQt.py:71` — source licence **unresolved**; manifest evidence: `LICENSE.txt`.
- `_reference/esmaeilinia_VeloView/VelodyneHDL/WrapPythonQt.py:137` — source licence **unresolved**; manifest evidence: `LICENSE`.

## Native acceptance checklist

Boundary tests establish Python contracts, not C++ virtual dispatch or safe native
deferred deletion. Controller should launch each slug in FontLab, exercise the
check below, inspect between actions, close twice, relaunch and close again.
Verify the host stays alive and its fonts/preferences/Output remain unchanged;
settings persistence is limited to the owned namespace. All builds should return
within the 5-second deadline. Record acceptance separately in insights.json.

| Rank / launch name | Native interaction to verify |
| --- | --- |
| 1. `signal-lifetime` | Click twice: advance 600 → 610 → 620; reshow retains identity; close/relaunch resets safely. |
| 2. `glyph-list` | Apply A, empty and missing filters; verify visible list matches inspect(), then close/relaunch. |
| 3. `metrics-table` | Verify three rows, glyph/advance/LSB headers and numeric cells; no edits to user font. |
| 4. `timer-batch` | Watch four names process one per tick, timer stop, FontLab remain responsive; close mid-batch. |
| 5. `contour-canvas` | Resize/repaint: closed curved outline remains visible; paint_count increases; close/relaunch without errors. |
| 6. `owned-key-filter` | Type in owned input: log updates without consuming keys; type elsewhere: log unchanged; remove filter on close. |
| 7. `metric-controls` | Change spin and slider both directions; values agree, one update per change, no recursive callbacks. |
| 8. `glyph-properties` | Toggle default/alternate; label text attribute and dynamic glyphRole match inspect(). |
| 9. `sandbox-settings` | Save Unicode sample; close/relaunch restores it; Reset removes only proof/sample in FontLabPythonExamples/InsightsSandbox. |
| 10. `callback-errors` | Apply bad, negative, huge and valid advances; errors stay in owned label, previous valid value survives; valid input clears error. |
| 11. `owned-dock` | Toggle, float and redock the panel within its own window; FontLab panels unchanged; named close cleans all. |
| 12. `contour-scene` | Verify contour plus baseline and advance guides; drag/scroll owned view; scene/view disappear on close. |

| 13. `loaded-glyph-form` | Set glyph_name.text and advance.value, click apply; result and inspection agree; load from another working directory; close/relaunch. |
| 14. `worker-glyph-queue` | Click start twice: one worker; wait for four GUI-delivered results; restart then stop or close immediately; worker joined, no Qt calls from worker. |
| 15. `owned-repl` | Run advance, assignment advance = 720, print(advance), and invalid syntax; all output stays in the owned console; reset restores the namespace. |
| 16. `plugin-tokens` | Install twice: one menu/action token pair; trigger plugin_action; unload twice: zero tokens and detached menu; reinstall works; FontLab menus unchanged. |
| 17. `metrics-undo` | Apply two advances, undo/redo; undo then apply a new value clears redo branch; native command overrides and label update work; close safely. |
| 18. `compiled-slot-exposure` | Click move: compiled non-slot move(QPoint) repositions preview; clear invokes native clear() slot; inspect its metaobject slot index; no custom C++ compilation. |

## Source read ledger and broad sampling

All counts are full-file scanner reads. Each row also gives a contextual source
sample and its lesson; additional focused reads supply the ranked citations.
Source licence grants remain unresolved unless a particular file notice is stated.

| Source | Files read | Licence evidence in manifest | Context sample and lesson |
| --- | ---: | --- | --- |
| `jcfr_PythonQt` | 6 | Unresolved; `COPYING` | `_reference/jcfr_PythonQt/examples/PyGettingStarted/GettingStarted.py:21` — property attributes plus string-signature connections |
| `kateliev_TypeRig` | 78 | Unresolved; `LICENSE` | `_reference/kateliev_TypeRig/Lib/typerig/proxy/fl/gui/dialogs.py:60` — metrics controls, vector paths and native FontLab undo boundaries |
| `RobotLocomotion_director` | 104 | Unresolved; `LICENSE.txt` | `_reference/RobotLocomotion_director/docs/sphinx/tutorials/robot/normalSelectionWidget.py:28` — timer stop/disconnect, generators, own settings and docks |
| `Slicer_SlicerGitSVNArchive` | 50 | Unresolved; `License.txt` | `_reference/Slicer_SlicerGitSVNArchive/Base/Python/slicer/ScriptedLoadableModule.py:75` — unload disconnect and parented deferred timers |
| `Belsepubi_naali` | 30 | Unresolved; `license.txt` | `_reference/Belsepubi_naali/bin/pymodules/apitest/animsync.py:5` — component registration and remote state are host-specific |
| `CsoundQt_CsoundQt` | 14 | Unresolved; `COPYING` | `_reference/CsoundQt_CsoundQt/src/Scripts/Color Organ/color-controller.py:21` — colour callbacks; reject host document/playback side effects |
| `Atarity_Prismatik-plugins` | 4 | Unresolved; none recorded | `_reference/Atarity_Prismatik-plugins/Animate/Animate.py:11` — timer disposal; explicit disconnect still needed |
| `Bluscream_pyTSon_plugins` | 90 | Unresolved; `LICENSE.txt` | `_reference/Bluscream_pyTSon_plugins/include/autorun.py:27` — network reply callbacks and exception boundaries |
| `DAIRLab_dairlib` | 3 | Unresolved; `LICENSE` | `_reference/DAIRLab_dairlib/director/scripts/VisualizationGUI.py:52` — JSON-driven visualization; keep expensive startup outside build |
| `HopeFOAM_HopeFOAM` | 2 | Unresolved; `LICENSE` | `_reference/HopeFOAM_HopeFOAM/ThirdParty-0.1/ParaView-5.0.1/Plugins/PythonQtPlugin/WrapPythonQt.py:117` — vendored compiled-wrapper generator |
| `ParadigmHyperloop_Dynamic_Controls` | 66 | Unresolved; none recorded | `_reference/ParadigmHyperloop_Dynamic_Controls/drake/build/lib/python2.7/dist-packages/ddapp/actionhandlers.py:126` — vendored ddapp action wiring |
| `StructuralNeurobiologyLab_SyConn` | 1 | Unresolved; `LICENSE.txt` | `_reference/StructuralNeurobiologyLab_SyConn/syconn/analysis/syconn_knossos_viewer.py:325` — viewer buttons wired through native connect signatures |
| `carthurs_CRIMSONPythonModules` | 35 | Unresolved; `LICENSE` | `_reference/carthurs_CRIMSONPythonModules/CRIMSONSolver/BoundaryConditions/NetlistEditor.py:29` — connections accumulate; retain exact slot identity |
| `cvetan5_naali` | 36 | Unresolved; `LICENSE` | `_reference/cvetan5_naali/bin/pyplugins/websocketserver/websocketserver.py:50` — C++ typed signatures depend on compiled host exports |
| `douzhongqiang_EasyCanvas` | 1 | Unresolved; none recorded | `_reference/douzhongqiang_EasyCanvas/bin/Script/SetColorAlphaScript.py:82` — slider/combobox typed signals for colour controls |
| `dsikka_spinal_destination` | 5 | Unresolved; none recorded | `_reference/dsikka_spinal_destination/displayer/displayer.py:119` — start/stop buttons; retain timers rather than anonymous deferred callbacks |
| `eryar_PipeCAD` | 37 | Unresolved; `LICENSE.md` | `_reference/eryar_PipeCAD/lib/omp/library.py:57` — search/filter panels and graphics items |
| `esmaeilinia_VeloView` | 4 | Unresolved; `LICENSE` | `_reference/esmaeilinia_VeloView/VelodyneHDL/WrapPythonQt.py:137` — compiled wrapper registration; file-specific Apache-2.0 notice |
| `exp111_pyTSon-Scripts` | 25 | Unresolved; none recorded | `_reference/exp111_pyTSon-Scripts/include/autorun.py:27` — owned UI discovery, model/proxy callbacks and filter bridge |
| `gaoyi_iGynePy` | 9 | Unresolved; none recorded | `_reference/gaoyi_iGynePy/Misc/.slicerrc.py:146` — shortcut ownership and ambiguous activation signals |
| `googlefonts_science-gothic` | 12 | Unresolved; none recorded | `_reference/googlefonts_science-gothic/scripts/FontLab/SG-Audit.py:440` — checkable glyph audit models; avoid automatic host actions |
| `hlolli_CsoundQt` | 18 | Unresolved; `COPYING` | `_reference/hlolli_CsoundQt/src/Scripts/Color Organ/color-controller.py:21` — duplicate editor/colour patterns; host playback is not portable |
| `jmirabel_gepetto-viewer` | 2 | Unresolved; `LICENSE` | `_reference/jmirabel_gepetto-viewer/pyplugins/gepetto/gui/blenderexport.py:89` — named plugin dock and host shortcut registration |
| `jonnenauha_naali` | 30 | Unresolved; `license.txt` | `_reference/jonnenauha_naali/bin/pymodules/apitest/animsync.py:5` — Naali component/GUI duplication |
| `knossos-project_knossos` | 6 | Unresolved; `LICENSE.txt` | `_reference/knossos-project_knossos/python/examples/graphics_view.py:6` — scene/view ownership and navigation |
| `meltycriss_uav` | 65 | Unresolved; none recorded | `_reference/meltycriss_uav/lib/drake/python2.7/dist-packages/director/actionhandlers.py:147` — vendored Director action wiring |
| `openhumanoids_director` | 90 | Unresolved; `LICENSE.txt` | `_reference/openhumanoids_director/docs/sphinx/tutorials/robot/normalSelectionWidget.py:28` — Director event-filter bridge and panel pattern |
| `realXtend_TundraAddons` | 36 | Unresolved; none recorded | `_reference/realXtend_TundraAddons/PythonScriptModule/pymodules_old/apitest/animsync.py:5` — Naali/Tundra component lifecycle duplication |
| `tapiocaTakeshi_cad_ai` | 36 | Unresolved; `LICENSE.md` | `_reference/tapiocaTakeshi_cad_ai/lib/omp/library.py:57` — PipeCAD-derived filtering and dynamic library reload |

These historical samples include Python 2 syntax, unavailable VTK/MRML/TS3/Naali
objects, processEvents loops, missing disconnects, unparented timers and faulty
base-class calls. Their repetition identifies useful concepts, not safe code to
transplant. The 12 implementations use owned synthetic data and measured host
placements. No corpus licence grant or native acceptance is inferred from tests.
