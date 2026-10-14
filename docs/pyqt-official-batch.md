---
this_file: docs/pyqt-official-batch.md
---

# Official PythonQt batches: controller acceptance

The first 23 entries are implemented; **the current fixes await native reacceptance**.
The controller reported that the prior build passed launch/inspect/close only for
trivialwizard and stylesheet; other ports failed or crashed. No commit was made. This is a source-checkout delivery, not wheel-installation evidence.
The immutable source catalog is unchanged. Actual targets use the requested
`ports/<category>/pyqt-official/` namespace, recorded in `catalog/ports.json`.

Launch by the IDs below or names such as `Official basiclayouts`:

```python
import fontlab_python_examples as examples
h = examples.launch('2f94fe07de765888')
c = h.controls
state = examples.inspect('2f94fe07de765888')
examples.close('2f94fe07de765888')
```

`controls` retains original source control names (e.g. `moreButton`, `textEdit`,
`newAct`); `window` is always the root. Repeated local variable names refer to the
last constructed control; arrays of captures, shapes and windows are also on
the corresponding Python subclass. Dynamic dialogs appear as `active_dialog`.
Inspection has `title`, `width`, `height`, scalar `controls` state and `error`,
plus the per-demo state below. No native objects enter JSON.

## Common acceptance for every row

1. Launch from a clean source checkout in FontLab 9.0.9780. Record Python/Qt
   versions, screenshot, title, inspect JSON, resource rendering and console
   exceptions. Repeated launch must reshow the same owned root.
2. Drive the controls below with native signals, clicks, key events and resizing;
   use temporary files for every read/write exercise. Inspection itself must
   leave files, clipboard, FontLab settings, fonts and global Qt styles unchanged.
3. Exercise native X/hide/reshow, then named close while a dialog, completion
   popup, movie, search or settings timer is active where applicable. Track
   QObject destruction, including dynamically created windows, actions and
   dialogs. All connections must disconnect before any `deleteLater`; process
   the host's event loop externally after close. Confirm no callback exceptions,
   no surviving owned UI/timers and FontLab still responsive. Repeat close, then
   relaunch and confirm fresh state. Never run a nested event loop in the port.
4. Verify that fonts, host windows, preferences, translators and global styles
   match the baseline. Clipboard changes are intentional only after explicitly
   driving Cut/Copy/Paste; restore the controller's clipboard fixture afterward.
5. Mark each manifest row passed only after retaining native evidence. If a
   required native wrapper/codec/virtual dispatch fails, record the precise API
   and block that row; doubles are not native acceptance.

## Per-port adaptations and checks

### classwizard

`035f3fbd2b81479a` — `ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py`.
Five original wizard pages, fields and generated C++ skeletons retained. PNGs
load from files; output defaults to a temporary directory owned by the example.
Finish uses UTF-8 file writes and an asynchronous owned error message.

Native: confirm five `page_ids`, initial title `Class Wizard`, mandatory class
name prevents Next; enter `Sample`, toggle QObject/QWidget/default/copy
constructors, comments, include guard and base include. Navigate Back/Next to
exercise native `initializePage` dispatch and field registration. On Output
Files select a controller-owned temporary directory; Finish must produce the
selected `.h`/`.cpp` content. Missing output directory must show an owned error
without closing the wizard. Check all banner/logo/watermark images.

### configdialog

`3f5f77c0358d9fef` — original three-page configuration dialog and three PNG icons.
No update/network implementation is added: upstream Start Update/Query buttons
are illustrative and unconnected.

Native: `contentsWidget.setCurrentRow(0/1/2)` must show Configuration/Update/Query
and change `current_page`; `page_count` is 3. Check five servers, three packages,
date/query controls, query spinbox 1–100, icons and Close.

### extension

`a1c26dbf9f995edb` — original optional search extension and fixed-size layout;
vertical button-box orientation is set after construction, without keywords. Associated rc files are not runtime
dependencies of this source and are not copied.

Native: title `Extension`; `moreButton.click()` reveals `extension` and enlarges
the dialog; second click hides it and restores size. Check all five checkboxes,
Find field and default button. Upstream Find has no search callback.

### findfiles

`63f2eeefd052f701` — asynchronous directory selection; GUI timer scans 64 KiB
chunks with cross-chunk text matching and a cancellable progress window. Starts
in an owned sample directory. No QApplication.processEvents/reentrant loop.

Native: choose a temporary directory containing two `.txt` files and a symlink;
set `fileComboBox` to `*.txt`, `textComboBox` to a unique Unicode substring, click
`findButton`. Expect exactly the matching non-symlink filename and size in
`filesTable`, `results`, `row_count`. Repeat with empty pattern/text; cancel a
large-file search through `progress`, check `searching` false and closed stream.
Missing directory reports `error`. Browse cancel preserves selection. Double
click opens a file only when deliberately driven; URL uses `fromLocalFile`.

### standarddialogs

`e1a0a829f8f2e311` — all 15 original dialog buttons retained; input/color/font/file
and message choices use instances, open and callbacks, including custom warning
buttons. Native file-dialog option remains selectable.

Native: integer 42 → `integerLabel` `42%`; double 12.5 → `$12.5`; season Winter;
Unicode user name; color swatch/text and selected font update after acceptance.
Cancel each and verify previous labels. Test directory, one/multiple input files
and save-path selection (no file is written by this demo). Verify Abort/Retry/
Ignore, OK, Yes/No/Cancel and Save Again/Continue labels; Error Message suppression
checkbox still works. Close with each kind of child dialog open.

### tabdialog

`dab5fd4c94ec518d` — original General/Permissions/Applications tabs inspect an
owned sample file instead of the process working directory. Permissions and
application associations remain illustrative, as upstream.

Native: 3 tabs, 30 application names, sample filename/path/size/timestamps and
permissions; select tabs and entries, toggle association checkbox; OK/Cancel
hide the dialog and named close releases the sample directory.

### trivialwizard

`c0d4a173b261a3e5` — original three-page wizard, no QApplication.

Native: Introduction → Registration → Conclusion, Back and Finish/Cancel.
Check `page_ids` length 3, `current_id`, name/email editing and original text.
The original trivial wizard does not enforce required fields.

### basiclayouts

`2f94fe07de765888` — original horizontal, grid and form groups and text editors.

Native: four buttons, three labelled grid rows, 3 form rows; edit both text
editors, resize and verify grid stretch and remaining-space behavior. OK,
Cancel and File/Exit affect only this dialog. Inspect original editor texts.

### borderlayout

`f48955d43ed6196c` — original custom QLayout algorithm and item wrappers; native
base geometry calls are explicit. Negative item indexes now return None.

Native: six items (North, South, West, East 1, East 2, center). Resize root wide
and tall; verify `items` geometry and label positions, center fills remainder.
Exercise native virtual `count/itemAt/takeAt/sizeHint/setGeometry` dispatch;
track layout/item teardown as well as child widgets.

### flowlayout

`675c9f79650d7507` — original flow layout; contentsMargins replaces unavailable
getContentsMargins and flag construction uses native integer enums. Minimum size
uses numeric components, never QSize arithmetic.

Native: five original button texts. Resize narrow/wide; verify wrapping,
`heightForWidth`, spacing and `items` geometry. `item_count` stays 5; no missing
or double-deleted layout items during close/relaunch.

### application

`7da7020aa7e2732b` — original menus, toolbars, status and editor; UTF-8 I/O,
asynchronous file/unsaved-change prompts; geometry settings use an owned INI.

Native: New/Open/Save/Save As using Unicode fixture; change text, try New/Open/X,
exercise Save, Discard and Cancel (including cancelling the save file dialog).
Failed I/O preserves text and modified state. Check title, toolbar icons,
selection-based Cut/Copy enablement, clipboard actions and About. Inspect
`text`, `file`, `modified`; host windows/preferences remain unchanged.

### mdi

`1415facde30a25cf` — original MDI actions and document classes; asynchronous close
sequence for root and Close All; child X closes its enclosing subwindow after
approval; no application-wide layout-direction change. Document-modified
signals connect once, and closed/failed documents are excluded from reopen lookup. Dynamic Window-menu
callbacks disconnect before their actions are removed/deleted. Hidden children
remain owned until named cleanup; no DeleteOnClose Python-slot hazard.

Native: create two documents; edit/save each, reopen an existing path and confirm
activation rather than duplication. Tile/Cascade/Next/Previous; Window menu
selects each document, and repeated rebuilding leaves no duplicate callbacks.
Close/Close All/root X must honor each Save/Discard/Cancel, prompting one document
at a time. Reopen a discarded document and confirm disk contents are loaded. Switch layout
direction affects only this window. Check `documents` and owned INI cleanup.

### sdi

`eba98690c141a070` — original separate document windows; all retained by the same
handle. Exit closes only this example's windows. Asynchronous prompts and owned
INI settings; no enumeration or closure of host windows.

Native: New twice creates three independent windows; Open in empty versus
modified windows and reopen existing path. Save/Save As Unicode fixtures;
Cancel one unsaved close and ensure it stays open. Exit affects all owned SDI
windows while preserving FontLab. Named close destroys all retained windows and
clears the per-build window list; relaunch starts numbering afresh.

### basicdrawing

`907f39d8bf387501` — all 13 original shapes, pen/brush modes, gradients, texture,
antialiasing and transformations. Explicit QColor/brush constructor types;
QPainter ends in finally; original logo/brick assets are files.

Native: render every `shapeComboBox` option; change width (including cosmetic
zero), style/cap/join, every brush including 3 gradients/texture, antialiasing and
transformations. Check `shape/antialiased/transformed`, resize repeated tiles,
text/logo appearance and absence of active-painter warnings on close.

### codecs

`19571722ed96aa9c` — native QTextCodec list and original codec ranking; async file
selection and encoding preview; direct native codec conversion replaces stream
shift operators. Supplied sample encodings copied unchanged.

Native: use supplied UTF-8, UTF-16, UTF-16BE/LE and ISO samples, switch
`encodingComboBox`, cancel then accept preview; main `text` changes only on
accept. Save As menu hides codecs unable to encode the current text. Save and
reopen each supported encoding, compare Unicode text and output bytes; failed
I/O stays owned. Record `codec_count` and actual available codecs.

### customcompleter

`10ef4dacb4db4080` — exact wordlist loaded with pathlib into QtGui.QStringListModel;
QString activation overload; replacing a completer disconnects its old slot;
explicit native QTextEdit key/focus handlers.

Native: verify `word_count`, type 3+ characters, Ctrl+E, arrows/Enter/Tab/Escape,
case-insensitive matches, completion inserted at the text cursor. Select an
exact match and a longer completion. Exercise focus changes and close while
popup is visible; Exit leaves FontLab open.

### i18n

`eca1cd9ef1528607` — 15 exact QM resources; translation is per-window through its
owned QTranslator, never installed globally. Original language chooser, colored
windows and close filter retained; integer grid coordinates corrected. Temporary
language-name translators are released without entering the controls registry;
`window` continues to name the root after language windows open.

Native: 15 checkboxes; Show All/Hide All, individual toggles and X synchronize
window visibility and checks. Verify at least English, German and Arabic text
and RTL layout against the selected QM; host UI language/direction must not
change. Inspect `languages/windows`; close removes all event filters and children.

### regexp

`626fd0acec74fd91` — original QRegExp syntax/case/minimal/capture controls. Fixed
discarded string.replace results in the escaped-pattern display.

Native: `(A)(\d+)` against `xxA123yy` → index 2, length 4, captures A123/A/123;
check escaped backslashes/quotes, invalid pattern coloring, case toggle,
minimal matching, wildcard and fixed-string modes. Six capture edits stay
read-only; refresh signals must not produce argument-count exceptions.

### settingseditor

`9e41e71c41b116a8` — original tree, type delegate, location dialog and refresh
controls. Every application/scope preview uses owned temporary INIs; selected
INI/plist files are copied/imported. Fallbacks remain disabled. Windows registry
access is explicitly unavailable on this macOS host. Fixed false-string boolean
conversion and accommodated native validator result shapes. Timer is parented;
transient delegate editors leave controls before native destruction.

Native: Open Application Settings location dialog (Native/INI, User/System,
organization/application) must list only owned temp paths. Open copies of the
supplied INIs, edit bool/int/string/list/date/color/point/size values, verify type
and invalid-input rejection; original files stay byte-identical. Test plist
copy, Refresh and Auto-Refresh, no duplicate itemChanged callbacks. Close with
timer and location dialog open; verify owned INI directory removed.

### icons

`505d60a757bbc177` — original 8-cell mode/state preview, image table, persistent
editors, inferred modes and size/style choices. Style changes visit only owned
widgets; explicit QTableWidgetItem signal signature; previewSize avoids native
QWidget.size name collision. Asynchronous multi-file chooser; delegate editor
callbacks disconnect before destroyEditor, and transient items are not retained
as controls.

Native: add supplied monkey on/off and find normal/disabled images, verify
inferred mode/state and each preview cell, toggle rows, edit delegate combos,
change 8–128 custom size and every standard metric size; Remove All empties
preview. Switch styles without changing FontLab. Close while persistent editors
are active; `image_count`, `preview_cells` and `icon_size` remain accurate.

### movie

`a3b3cbe51c1506c6` — original animated-image player with async chooser, frame/speed/
fit/play/pause/stop. Frame slider blocks feedback while following the movie;
stop precedes callback disconnection and deletion. Original MNG copied unchanged.

Native: inspect supported `formats`, explicitly open supplied animation.mng;
verify `valid`, frame changes/count, Pause/Resume/Stop, frame seek, speed 1–9999%,
Fit to Window and resize. Unsupported MNG/plugin behavior must be recorded as a
capability blocker, not a successful playback. Closing during playback leaves
no frame callbacks or movie activity.

### stylesheet

`876eab33b6a99e31` — exact original two UI XML files loaded by QUiLoader; explicit
tracked wiring replaces generated Python UI/autoconnect and pyqtSlot. Coffee,
Pagefold and Default QSS/images retained. Resource URLs rewrite only in memory;
style and QSS apply only to the owned root/editor, never QApplication. QFile and
QUiLoader cleanup also covers loader-constructor failure.

Native: original sample form/control texts, Coffee initial rendering; open
editor, select all three sheets and styles, edit CSS and Apply, save a temporary
QSS and compare text. Check all image-backed widget states and form interactions;
`sheet/applied/editor_visible` update. Cancel save, close root while editor open;
no global style changes or retained editor window.

### tooltips

`e62ce3eb648cfb4c` — original shape paths, hit testing, dragging, tooltips and three
creation buttons; integer QPoint coordinates and small-window random bounds;
explicit native event delegation and painter finally cleanup. Painter save/restore
avoids wrapper negation; hit testing and dragging use numeric components.

Native: initially Circle/Square/Triangle; create each type, hover correct tooltip,
drag overlapping shapes and verify topmost hit testing, release then drag again.
Resize small/large; buttons remain positioned. `shapes` records tooltips and
positions; close during hover/drag without painter or callback warnings.

## Licence and evidence limits

The source headers grant BSD-3-Clause while the collection README and LICENSE
say GPLv3. Both notices are preserved, GPL-appropriate SPDX metadata is present,
and review remains unresolved; see [the complete notice](../ports/pyqt-official-LICENSE.md).
All 107 copied resources have source identities and SHA-256 records. Associated
rc modules for extension/findfiles/standarddialogs/tabdialog/trivialwizard/regexp
are conservative inventory associations, not imports in those files.

Local checks use exported-name contracts extracted from the sibling echopy
stubs and sealed native doubles. They establish build/control/ownership contracts
and source/resource integrity, not rendering, overload conversion, shell virtual
dispatch or destruction in FontLab. No Qt runtime/dependency was installed.

## 2026-10-14 native failure follow-up

The previous 215-test pass did not model PythonQt properties in `__dict__`,
keyword-rejecting constructors, unsafe wrapper operators or opaque QByteArray
values. The updated doubles reproduce those boundaries. Release now visits only
explicitly declared Python fields, never the synthetic native dictionary.

All 23 ports and the shared helper were audited: 332 binary/augmented operations
are strings, Python containers/path operations, numeric components or integer
flags; all 18 remaining unary +/- expressions have plain numeric literals.
The two native constructor keyword calls were removed. The stub constructor
signatures are generic `*args, **kwargs`, which does not establish keyword
support; these ports use simple positional construction and documented setters.
QByteArray.data() byte behavior comes from the controller's native observation.

| Port | Fix / audit result |
| --- | --- |
| classwizard | Declare only port-created page fields for release; native geometry is untouched. |
| configdialog | Declare the Python-owned page and list references for release. |
| extension | Use default QDialogButtonBox construction followed by setOrientation(Qt.Vertical); shared cleanup leaves native properties untouched. |
| findfiles | Declare all Python-owned UI/search state, including externally assigned timer/progress fields; use a nonnegative overlap slice instead of unary minus. |
| standarddialogs | Declare Python-owned labels/buttons/dialog references for release. |
| tabdialog | Shared release no longer enumerates synthetic native dictionaries; subclasses with no Python fields require no field cleanup. |
| trivialwizard | Audited; no port-source change needed. Controller reported the prior version passed launch/inspect/close. |
| basiclayouts | Declare Python-owned group/menu/editor references for release. |
| borderlayout | Release only the declared Python item list, keeping it empty for native virtual teardown. |
| flowlayout | Compute minimum QSize from numeric width/height components instead of wrapper addition; release only itemList. |
| application | Declare Python-owned editor/action/menu references for release. |
| mdi | Declare Python-owned subwindow/menu/document references, including _subwindow and _windowActions. |
| sdi | Declare Python-owned editor/action/menu references for release. |
| basicdrawing | Declare Python-owned painter values and controls for release. |
| codecs | Decode native codec-name QByteArray.data() as ASCII and write encoded QByteArray.data() bytes; declare Python-owned UI/codec references. |
| customcompleter | Declare completer/editor references for release; use a nonnegative suffix slice instead of unary minus. |
| i18n | Use positional parent-only QDialog construction and setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint); declare translator/window-map references. |
| regexp | Declare Python-owned capture/control references for release. |
| settingseditor | Declare Python-owned tree/delegate/dialog references; decode QByteArray.data() as Latin-1 for lossless byte editing. |
| icons | Declare Python-owned preview/table/action references; rollback no longer masks construction errors with a geometry=None error. |
| movie | Decode supported-format QByteArray.data() bytes as ASCII; declare Python-owned movie/control references. |
| stylesheet | Audited; no port-source change needed. Controller reported the prior version passed launch/inspect/close. |
| tooltips | Use QPainter.save/restore instead of unary QPoint negation; use coordinate arithmetic for hit testing and dragging; declare Python-owned shape/control references. |

Rerun the common acceptance checklist and each port-specific check above,
especially repeated paint/drag/resize for tooltips, minimum-size queries for
flowlayout, all closes and partial-build cleanup, extension/i18n launch, icons
launch, movie inspection and Unicode codec export. Licence scope remains open.

## 2026-10-14 slot-shadowing follow-up

Controller rerun: 22/23 ports passed launch/inspect/close without a crash; icons
failed because a Python field overwrote QMainWindow.centralWidget. The same
collision was found in i18n's lazily created language windows. Both now retain
`_central_widget`, call native setCentralWidget()/centralWidget(), and preserve
the `centralWidget` control key. Audit of all 23 ports and official.py against
native stubs found no other method/slot assignments. Doubles now reject slot
shadowing, including inherited QWidget methods; the AST guard checks subclass
assignments, external instance assignments and declared release fields.

Native follow-up: launch/inspect/close icons and exercise its image controls;
launch i18n, Show All, inspect all 15 language windows, Hide All and close.
Verify centralWidget() remains callable and all owned UI is destroyed. The
new changes have local test coverage; native reacceptance is still pending.


## Batch 4: 18 further ports (2026-10-14)

All 18 are implemented; **native acceptance is unexecuted**. These additions reuse
Demo, ExampleHandle, the official doubles/contract and this document. No commits
or native FontLab calls were made. PLAN.md/TODO.md and the immutable source catalog
are unchanged. There are 15 new exact resource copies and no compiled rc modules.
Names are unique: `Official draganddrop puzzle`, `Official itemviews puzzle`, and
`Official addressbook part1` through `part7`; source IDs remain canonical.

Apply the common five-step acceptance above to every row, then the specific
checks below. Record actual virtual dispatch, overload acceptance, screenshots,
input/output files, JSON state, QObject destruction and host survival separately.
Default states below are derived from original resources and boundary tests,
not FontLab evidence. In particular, confirm QVariant pixmap/point round-trips,
integer model index IDs and native model signal calls in the host.

QDrag.exec is the single deliberate non-dialog exec call, centralized in
Demo.drag: the host stub exports it, and [Qt documents that macOS drag operations
keep the event loop responsive](https://doc.qt.io/qt-6/qdrag.html#exec).
No QApplication or modal QDialog exec is used. If named close is requested during
a drag, it raises before disconnect/delete; finish or Escape the drag and retry.
The cleanup queue retains its guard on failure. Custom MIME payload names use a
fontlab prefix because explicit QVariant serialization differs from upstream's
stream operators. Both puzzle ports use the same payload format. The item-view puzzle overrides startDrag to route its native model MIME through
the same tracked drag boundary, including removal of moved source rows.

Controls retain original field names plus the named callables listed below.
Drag boards expose their labels through native children(); hidden moved labels
remain owned until named teardown and inspection includes their visibility.
All native connections are tracked. Subclass references are released only by
explicit declarations; native properties/slots are never nulled or shadowed.
Views detach after all Python signal disconnections and before subclass reference
release. Painters end in finally, timers stop before deletion, and no Qt wrapper arithmetic
is used. Address-book directories are created during build, never by inspection.
The licence remains BSD-3-Clause AND GPL-3.0-only with unresolved scope; the actual
Riverbank/Nokia and Jansen/Qt Company notices are retained verbatim.

### Batch 4 5781fa4ba55c884f

**Draggable icons** — `ports/draganddrop/pyqt-official/draggableicons-5781fa4ba55c884f.py`.

Two original icon panels and three PNGs retained. QDataStream shift operators become explicit QVariant serialization through an owned QBuffer; MIME is application/x-fontlab-dnditemdata. Numeric hotspot subtraction replaces QPoint arithmetic. Moved labels hide until owned teardown; painters end in finally.

Native acceptance: Expect title Draggable Icons and 3 visible icons in each of controls left/right. Natively drag boat/car/house between panels: default Copy keeps the source; Move hides it; Escape restores its original pixmap. Drag within a panel, confirm hotspot and inspect panels coordinates. Reject unrelated MIME; repeatedly copy/move and close after cancelling an active drag.

### Batch 4 700e96dec485e7a8

**Draggable text** — `ports/draganddrop/pyqt-official/draggabletext-700e96dec485e7a8.py`.

Exact 41-word file replaces compiled resources/QTextStream. Plain text and ASCII hotspot bytes use QByteArray.data(); invalid hotspots fall back to zero. All positions use components; Python label subclasses and native drag sources remain owned.

Native acceptance: Expect Draggable Text, label_count 41, first word Qt. Use controls board.children() to drag a real label internally (Move) and between two separately owned port instances (Copy); drop external Unicode multiword text. Inspect labels text/positions/visibility. Escape keeps the source; malformed hotspot bytes do not raise. Close/relaunch restores 41 words.

### Batch 4 da76600eaea7a121

**Fridge magnets** — `ports/draganddrop/pyqt-official/fridgemagnets-da76600eaea7a121.py`.

Exact 48-word file, rounded painted magnet labels and external plain-text drop retained. Native QVariant text/point payload replaces stream shifts under application/x-fontlab-fridgemagnet. Explicit brush/color types, integer transparent image fill, component offsets and guaranteed painter end.

Native acceptance: Expect Fridge Magnets, label_count 48, first word Colorless. Check rounded label rendering and transparency. Drag a magnet internally and copy it externally; cancel a hidden-source drag and confirm it reappears. Drop Unicode plain text and inspect individual words/coordinates. Reject malformed custom payload without losing the window.

### Batch 4 c5b4e385cc921da4

**Drag-and-drop puzzle** — `ports/draganddrop/pyqt-official/puzzle-c5b4e385cc921da4.py`.

Original QListWidget pieces and 5x5 board retained with the exact JPEG. Integer crops/grid coordinates, component hotspot arithmetic, local random.Random, corrected highlightedRect typo and native QVariant MIME. pyqtSignal becomes an owned single-shot completion timer; file and completion dialogs are asynchronous.

Native acceptance: Expect Puzzle, piece_count 25, placed/in_place 0. Drive piecesList and puzzleWidget with native drag events: correct cell increments in_place; wrong cell does not; occupied cell rejects; drag back to list and Escape restore counts. Solve all 25: completion appears after drop returns and OK resets. Use restart/openImage, cancel chooser, reject bad image, and close with completion dialog open.

### Batch 4 b823a76f79197d84

**Lighting** — `ports/effects/pyqt-official/lighting-b823a76f79197d84.py`.

Original 25-item light/shadow scene and 30 ms GUI timer retained. Scene is parented; QPoint division becomes floating coordinate division, explicit QColor/QBrush overloads are used, timer stops before disconnect and painter ends in finally.

Native acceptance: Expect Lighting and Shadows, 640x480, item_count 25, timer_active true. Let the native timer run; angle, light coordinates and 25 offsets must change while the halo and shadows render. Resize and pan/inspect scene. Close during animation, process events, and prove the timer and scene/effects are destroyed.

### Batch 4 306c12d5cc1db46c

**Chart** — `ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py`.

Original custom PieView, legend, editable table, shared selection and both .cht files retained. Async file dialogs, UTF-8 CSV parsing before model replacement, numeric quantity validation and quoted CSV export replace Qt streams. Explicit base handlers, component geometry, QRegion.united and guaranteed painter end.

Native acceptance: Expect Chart, 14 rows/2 columns, valid_items 14, total 188, first label Scientific Research. Edit quantities/labels in controls table/model; pie sectors and totals must follow, invalid/NaN quantities must not break painting. Select table cells and sectors/legend both ways; rubber-band, arrows, scrolling and resize must synchronize. openFile/writeFile round-trip Unicode/quoted labels in a controller temporary file; failed/cancelled load preserves data. Close with chooser or selection active.

### Batch 4 227efef76ed4ac74

**Editable tree model** — `ports/itemviews/pyqt-official/editabletreemodel-227efef76ed4ac74.py`.

Original hierarchy and generated form behavior retained; UI widgets/menus/shortcuts are explicitly reconstructed from the copied exact mainwindow.ui, without generated Python/autoconnect. UTF-8 default text, str.strip, integer QModelIndex IDs mapped to retained nodes, native dataChanged/headerDataChanged calls and bounds checks replace PyQt assumptions. View detaches before model-reference release.

Native acceptance: Expect Editable Tree Model with 6 top-level rows and 2 columns. Compare against copied mainwindow.ui. Expand hierarchy, edit values, and drive insertChildAction/insertRowAction/insertColumnAction/removeRowAction/removeColumnAction at root and nested levels. Check [No data]/[No header], status position, action enablement and actual model notifications. Reject invalid ranges without mutation. Exercise remove-last-column then rebuild, and close during editing.

### Batch 4 c98ae8ac71886586

**Frozen column** — `ports/itemviews/pyqt-official/frozencolumn-c98ae8ac71886586.py`.

Exact grades.txt populates QStandardItemModel through pathlib. Original overlay and shared selection/scroll bars retained. Fix upstream self.logicalIndex/self.current typos; explicit native resize/moveCursor/scrollTo dispatch and tracked bidirectional signals.

Native acceptance: Expect Frozen Column Example, 31 rows/10 columns. Scroll horizontally: green first column stays fixed; both vertical bars remain synchronized. Resize column 0 and rows via native headers, resize window and inspect frozen_geometry/frozen_width. Use Left-key navigation across the hidden boundary, select cells in both views, and close after scroll/resize.

### Batch 4 090c76a87351e771

**Interview** — `ports/itemviews/pyqt-official/interview-090c76a87351e771.py`.

Original lazy 1000x10 hierarchical model, three views, shared QItemSelectionModel, movable headers and both PNG icons retained. Numeric QModelIndex ID lookup replaces Python internal pointers; reject children under nonzero columns. Views detach before releasing model references.

Native acceptance: Expect Interview, row_count 1000, column_count 10, first_item Item 0:0 and shared_selection true. Select through controls table/tree/listView and verify synchronized indexes and current item. Expand multiple lazy levels, move table headers, switch list selection and check folder/file/header icons. Close after repeated expansion without stale model callbacks.

### Batch 4 878fe9f714df3b5e

**Item-view puzzle** — `ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py`.

Original QAbstractListModel/QListView variant and exact JPEG retained. Shared QVariant MIME with the drag-and-drop puzzle; integer coordinates, local RNG, timer completion and async dialogs. Correct removal inPlace arithmetic, highlightedRect typo, empty-model reset notifications and row bounds; detach view on cleanup. A QListView
subclass routes startDrag through the tracked drag boundary and removes source
rows only after Move.

Native acceptance: Expect 25 model pieces and an empty board. Exercise all puzzle checks above using native QListView/model drag/drop, including moving a correct piece away and cancelled drag rollback. Check model.mimeData/dropMimeData for multiple pieces and transfers to the other puzzle port. Restart repeatedly: exactly 25 rows, no invalid remove-row notifications. Solve/acknowledge and close while completion is pending.

### Batch 4 321f8e535facafde

**Simple tree model** — `ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py`.

Exact default.txt parsed as UTF-8 with str.strip. Original TreeItem/TreeModel hierarchy retained; integer QModelIndex identity map replaces Python-object internalPointer, index bounds are checked and the view detaches before release.

Native acceptance: Expect Simple Tree Model with 6 top-level rows and 2 columns Title/Summary. Expand every branch, verify original resource text and nested parent/index relationships. Resize columns, navigate by keyboard, select child rows and close while a deep branch is expanded. Relaunch must restore the original hierarchy.

### Batch 4 e1f313d96e43adff

**Address book part 1** — `ports/tutorials/pyqt-official/part1-e1f313d96e43adff.py`.

Original editable Name and Address form only; no persistence or later-stage controls added. Native property reads and explicit Python-reference release.

Native acceptance: Expect Simple Address Book; controls nameLine/addressText are editable and there is no Add button. Enter Unicode name and multiline literal <text>; inspect name/address exactly. Resize, hide/reshow and named close/relaunch: the new form is empty.

### Batch 4 55bcde890cd77ed7

**Address book part 2** — `ports/tutorials/pyqt-official/part2-55bcde890cd77ed7.py`.

Original add/submit/cancel stages and sorted contacts retained. Messages are owned asynchronous dialogs; addresses always use literal plain text.

Native acceptance: Initially fields are read-only. Add enables editing; empty Submit opens Empty Field, a valid name/address increments contact_count, and a duplicate is rejected. Cancel restores old fields. Inspect contacts, button visibility and read-only state. Close with an information dialog open; relaunch has no contacts.

### Batch 4 f4d9e2927469223c

**Address book part 3** — `ports/tutorials/pyqt-official/part3-f4d9e2927469223c.py`.

Part 2 adaptations plus original sorted Next/Previous navigation and wraparound; no later-stage edit/find/save controls.

Native acceptance: Add Zoë, Ada and Łukasz; Next and Previous follow sorted names and wrap at each end. Check button enablement with 0, 1 and multiple contacts; Cancel retains selection. Confirm duplicate/empty handling and literal multiline addresses, then close/relaunch.

### Batch 4 4d19e62d93dd761c

**Address book part 4** — `ports/tutorials/pyqt-official/part4-4d19e62d93dd761c.py`.

Original navigation/add/edit modes retained. Remove confirmation becomes an owned asynchronous Yes/No callback; rename collisions preserve both contacts and literal addresses are retained.

Native acceptance: Add two contacts, Edit a name/address, reject a duplicate rename, and Cancel an edit. Remove/No keeps both; Remove/Yes selects the previous contact and reduces contact_count. Remove the last entry: empty read-only fields and appropriate disabled controls. Close with confirmation open and verify no later callback.

### Batch 4 94ab271d023d1ca3

**Address book part 5** — `ports/tutorials/pyqt-official/part5-94ab271d023d1ca3.py`.

Part 4 plus parented reusable FindDialog with one tracked accepted callback. Empty Find stays open instead of accepting stale text; missing-name notice is asynchronous. Preserve upstream Find enablement threshold (>2 contacts).

Native acceptance: Add three contacts to enable findButton. Open Find: empty findSubmit keeps findDialog visible; findLine=Zoë selects its exact address; unknown name reports Contact Not Found. Cancel and repeated searches preserve state and never multiply callbacks. Close while Find or removal confirmation is open.

### Batch 4 2719ebb336f3a29e

**Address book part 6** — `ports/tutorials/pyqt-official/part6-2719ebb336f3a29e.py`.

Part 5 plus asynchronous file choosers confined to a build-owned temporary directory. Pickle stores a plain string dictionary; load denies global/class construction and validates shape before replacing contacts. Outside/symlink paths are rejected; the sandbox exists before inspection and is removed on close.

Native acceptance: Use inspect directory as the only save/load location. Save through saveButton, verify .abk bytes, edit contacts, then loadButton restores Unicode/literal addresses. Cancel dialogs, load empty/corrupt/wrong-shape data and try outside/symlink paths: errors preserve existing contacts and external files. Inspection writes nothing. Close removes the directory; relaunch creates an empty book/new directory.

### Batch 4 bb1c114d38fb756a

**Address book part 7** — `ports/tutorials/pyqt-official/part7-bb1c114d38fb756a.py`.

Part 6 plus asynchronous vCard export confined to the same owned directory. UTF-8 pathlib output replaces QTextStream operators; retain vCard 2.1 layout, fix discarded address replace results and escape backslashes/semicolons.

Native acceptance: Repeat part 6 checks. Select Zoë Example with a multiline address containing semicolon/comma/backslash; exportButton opens an owned chooser, acceptance writes the expected BEGIN/END, VERSION:2.1, N/FN and escaped ADR lines. Cancel writes nothing; external path is rejected. Close with chooser open, then confirm all export/pickle artifacts disappear with the owned directory.


## Batch 5: animation, graphics view, desktop, threads and IPC

**15 implemented, one blocked; every native acceptance state is unexecuted.**
Source originals remain pinned/read-only; the preceding batches and TODO items
are unchanged. This batch adds 45 exact asset copies and no packages. QState,
QStateMachine, QPropertyAnimation, QGraphicsObject, QTimeLine, QScreen and
QSystemTrayIcon exist in the checked host stubs. QThread and
qRegisterResourceData are absent; QSharedMemory has no detach export. The same
captured contract/doubles now cover the additional classes and reject Qt calls
from a worker. These checks do not prove PythonQt virtual dispatch or overloads.

Graphics demos embed their original view in a flush QWidget owner; controls
view retains the graphics view for native interaction. The launcher shows
only the completed owned root. Native transitions owned by a QStateMachine use native QObject signal relays;
all Python slot targets go through ExampleHandle’s connection inventory. Close
stops workers (with bounded join), timers, machines and animations before
Python callback release and native destruction. A failed join/active drag keeps
the owner alive and requires a later close retry. Hidden relay buttons must
remain invisible when the root is shown. Inspect never performs capture, tray
activation, a notification, file selection, a worker start or an IPC action.

The two commercial/LGPL/GPL headers explicitly offer GPLv3; that alternative is
selected and the original alternatives remain verbatim. Fourteen entrypoints
retain BSD-3-Clause source grants alongside the collection GPLv3 evidence,
with scope unresolved, consistently with earlier batches. Copied asset grants
remain unresolved where no individual notice exists.

For each implemented row apply **all common acceptance steps above**: launch by
ID, inspect and native screenshot, drive the specific interactions below,
native X/reshow, named close twice, process host events externally, retain a
complete owned-object destruction inventory, relaunch, and verify FontLab and
unrelated fonts/windows/settings/clipboard are unchanged. Screenshot files and
tray changes require explicit control actions. Never mark a row passed from
these doubles. Shared memory has a blocker check instead of a fake UI.

<a id="batch-5-0578c17977b471f1"></a>

### Embedded dialogs — `0578c17977b471f1`

Target: `ports/graphicsview/pyqt-official/embeddeddialogs-0578c17977b471f1.py`. Status: **implemented**, native **unexecuted**. Licence: `GPL-3.0-only`.

Adaptation: 100 proxy dialogs and original form controls/background retained. Generated PyQt UI becomes explicit QFormLayout controls; styles parent to the owned dialog. Native QTimeLine callbacks are tracked/stopped; currentValue uses the actual getter; native protected handlers are dispatched explicitly.

Native acceptance: Expect title Embedded Dialogs Demo, dialog_count 100 and spacing 6. Use controls proxies to hover into/out of several dialogs; verify zoom, rotations, popup focus and cache changes. On controls dialog.ui change spacing (12), directionPicker (RTL/LTR), fontComboBox and stylePicker; verify only that dialog changes. Inspect remains inert. Close while a timeline and a combo popup are active; verify all 100 timelines and embedded dialogs are destroyed.

<a id="batch-5-0788354954c8e613"></a>

### Mandelbrot — `0788354954c8e613`

Target: `ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: QThread/QMutex/QWaitCondition become a cancellable Python worker and bounded GUI timer drain. All eight refinement passes, original centre/scale and 512-entry spectral colormap are retained. Workers emit integer scanlines; only the GUI constructs/writes QImage. Zoom/scroll cancels and joins stale work; mouse release applies numeric deltas; the original cached drag preview is replaced by progressive row repainting.

Native acceptance: Expect Mandelbrot, initial render_size 550x400 after kickoff, centre [-0.647011,-0.0395159], scale 0.00403897, pass progressing to 7. Exercise controls zoom(0.8), scroll(20,-20), start and stop plus native wheel, +/- and arrow keys, drag/release, resize and repaint. Verify detailed fractal rendering and host responsiveness. Stop/restart repeatedly; close during calculation and with an undrained queue, proving worker join and timer destruction.

<a id="batch-5-1ca857d797199ecf"></a>

### Diagram scene — `1ca857d797199ecf`

Target: `ports/graphicsview/pyqt-official/diagramscene-1ca857d797199ecf.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original flowchart shapes, arrows, text editor, menus, toolbars and 15 PNGs retained. Custom PyQt signals become explicitly released Python callbacks; Qt signals still use the handle inventory. QPoint arithmetic and undocumented QLineF reference-output conversion become numeric geometry; zero-length arrows are guarded. Qt4 QString operations become Python strings; menus use popup and About uses asynchronous message. Removed items move to a hidden owned scene, avoiding deletion of connected Python targets; nonempty text is retained.

Native acceptance: Expect Diagramscene, item_count 0, mode MoveItem. Use scene, buttonGroup, pointerTypeGroup, sceneScaleCombo and native mouse events to insert Conditional/Process/Input-Output, draw a real arrow between two shapes, move endpoints and verify the arrow follows. Edit text, font/colour/bold/italic/underline; keep nonempty text and remove empty text on focus loss. Test backgrounds, 50–150% scale, Bring/Send/Delete and asynchronous About. Delete shapes with arrows, then close with text focus and an open popup; verify discarded-scene and action destruction.

<a id="batch-5-1cf57c0f2ac8880a"></a>

### Animated tiles — `1cf57c0f2ac8880a`

Target: `ports/animation/pyqt-official/animatedtiles-1cf57c0f2ac8880a.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original 64 tiles, five layouts, staggered durations, background and button images retained. PyQt QObject/pyqtProperty proxy becomes painted QGraphicsObject with native pos. Invisible owned QPushButtons relay item clicks into real QState transitions; no custom Qt signal registration. All timers, state machines and animations stop before disconnect; pixmaps are centred by paint coordinates.

Native acceptance: Expect Animated Tiles and item_count 64. Use controls ellipse/figure8/random/tiled/centered via native clicks; inspect positions and verify every arrangement plus InOutBack interpolation/stagger. Resize view and check fitting and resource rendering. Close during transition and during the initial timer; confirm animations/state machine/timer destruction and a clean relaunch.

<a id="batch-5-243ae486f9528e8c"></a>

### Stickman — `243ae486f9528e8c`

Target: `ports/animation/pyqt-official/stickman-243ae486f9528e8c.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: 16 original nodes/bones, drawing/stabilisation and four byte-identical animation files retained. Native xChanged/yChanged replace positionChanged; native pos properties animate original frames. Original QDataStream binary layout is decoded into checked Python data using struct (including null QString); save uses explicit numeric stream writes. Native button relays implement J/D/C activity transitions; an owned timer implements random lightning and the 100 ms flash. Colour/death changes use entered callbacks rather than unregistered Python properties. Zero-length bones and all wrapper arithmetic are guarded.

Native acceptance: Expect Stickman, node_count 16; frames jumping=5, dancing=9, chilling=25, dead=1. Focus controls view and send J, D, C; verify complete repeating motion and dragging nodes in stick mode via controls stickMan.setDrawSticks(True). Call strike.click(), verify white flash and dead face/pose after flash timer, then confirm activity keys do not resurrect it. Exercise coincident nodes and repaint. Close while moving/flashing; verify node/animation/timer destruction.

<a id="batch-5-27709a02d37b9ba9"></a>

### Wait conditions — `27709a02d37b9ba9`

Target: `ports/threads/pyqt-official/waitconditions-27709a02d37b9ba9.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: QThread/QMutex/QWaitCondition become Python producer/consumer workers using a real threading.Condition, an 8192-character ring and bounded GUI timer delivery. Preserve the 100000-character ACGT transfer; deterministic ACGT order replaces global qrand. An owned read-only log and Start/Stop controls replace process stderr output; timed waits and publish backpressure permit stop/join.

Native acceptance: Expect Waitconditions, phase idle, received 0, data_size 100000 and buffer_size 8192. Click start and drain native events until phase done: received 100000 and prefix/suffix ACGT repeated 20 times. Stop midway, restart to a fresh result, start without draining until backpressure, then named close; verify both workers joined, no Qt calls off the GUI thread and no stderr/global app loop.

<a id="batch-5-29f6a7d0a3bb6813"></a>

### States — `29f6a7d0a3bb6813`

Target: `ports/animation/pyqt-official/states-29f6a7d0a3bb6813.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original text editor, radio options, six icons, state property assignments and animations retained. Uses native QGraphicsObject pos/rotation/opacity and real QState/QPropertyAnimation. Each scene, state machine, group and animation is owned; copied PNGs replace compiled resources.

Native acceptance: Expect States with button_text Switch to state 2 and six rendered icons. Click controls button through 2→3→1 repeatedly; verify widget geometry, icons, rotations, opacities and Options appearance. Edit controls edit and select Herring/Blue Parrot/Petunias. Close mid-animation; confirm state machine/animations/proxy widgets are destroyed without callbacks.

<a id="batch-5-2cd6ffc2b2ed65bb"></a>

### Drag/drop robot — `2cd6ffc2b2ed65bb`

Target: `ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original ten-colour palette, articulated robot and looping native rotation/scale animations retained with exact head PNG. Image MIME converts using QPixmap.fromImage. QDrag uses the existing responsive drag boundary/close guard; painters end in finally. Local RNG replaces global qrand/qsrand; all native animations are stopped and owned.

Native acceptance: Expect Drag and Drop Robot, palette_count 10 and an animated articulated robot. Natively drag colours from controls palette to each robot part; test rejected MIME and drag leave highlighting. After repeated drags verify the original occasional head image path, plus explicit image MIME to the head. Escape cancels a drag; attempt named close during drag and confirm safe refusal, finish/cancel and retry. Verify part colours, head_image, animation destruction and unchanged clipboard.

<a id="batch-5-65d15d1fbc1b15e9"></a>

### Screenshot — `65d15d1fbc1b15e9`

Target: `ports/desktop/pyqt-official/screenshot-65d15d1fbc1b15e9.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original options/preview controls retained. Startup and inspect do not capture or beep. New Screenshot schedules one owned cancellable timer; only its explicit callback calls primaryScreen.grabWindow. Save uses an asynchronous dialog and permits only this build’s temporary directory. No host settings or clipboard changes; timers stop before teardown.

Native acceptance: Expect Screenshot, has_capture false, delay 5 and capture_pending false. Inspect twice and confirm no OS screen capture. Explicitly click newScreenshotButton (macOS may require capture permission); test 0/positive delay, Hide This Window, preview resize and cancellation by closing before timeout. Save using saveScreenshotButton inside the dialog’s owned directory; verify the PNG opens with the captured dimensions. Reject an outside path through saveTo. Close destroys timer/dialog and removes temporary files.

<a id="batch-5-b7283d74afb78218"></a>

### Move blocks — `b7283d74afb78218`

Target: `ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original four blocks, seven geometries, 1250 ms timer, elastic animations and sequential pauses retained. Custom QEvent/QAbstractTransition payload routing becomes a tracked GUI callback choosing a different state and clicking an invisible native button relay into QState transitions. Uses QRectF for native graphics geometry. Broad inventory dependencies are unused upstream imports/resources and are not copied.

Native acceptance: Expect Move Blocks, block_count 4 and seven possible state_index values. Observe automatic changes, then call controls advance ten times: no adjacent repeated index and all four geometries change together. Verify elastic easing and the three original pauses; resize/repaint. Close while timer and animations are active; confirm destruction and no queued callback after close.

<a id="batch-5-b95b687bbc541207"></a>

### Semaphores — `b95b687bbc541207`

Target: `ports/threads/pyqt-official/semaphores-b95b687bbc541207.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: QThread/QSemaphore become two Python workers and actual threading.Semaphore synchronization around the original 8192-character ring; preserve the 100000-character transfer with deterministic ACGT data. Bounded GUI timer delivery replaces stderr; Start/Stop controls and timed semaphore acquisition permit clean cancellation/join even under backpressure.

Native acceptance: Expect Semaphores, phase idle and received 0. Start, wait for done and verify received 100000, buffer_size 8192, matching deterministic prefix/suffix and stopped timer. Stop with producer/consumer blocked; restart, then close with a full delivery queue. Verify both workers joined, native destruction and FontLab responsiveness.

<a id="batch-5-bd6c8feb783ba845"></a>

### Easing — `bd6c8feb783ba845`

Target: `ports/animation/pyqt-official/easing-bd6c8feb783ba845.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original 47 easing choices, tunable period/amplitude/overshoot, line/circle paths and Qt logo retained. Generated UI is reconstructed with original control names; curve names come from the checked Qt enum list rather than PyQt enum reflection. Native QGraphicsObject.pos replaces pyqtProperty; circle updates assign native pos without emitting a fabricated signal. Curve icon painters end in finally.

Native acceptance: Expect Easing curves, curve_count 47, curve OutBounce and path line. Use easingCurvePicker to choose Linear, InElastic, Back, Bounce and both splines; verify icon plots and enabled parameter controls. Change period/amplitude/overshoot, switch lineRadio/circleRadio, and observe actual interpolation and looping movement. Close during animation; confirm timer-free animation and scene/item destruction.

<a id="batch-5-c1b878b63f80e733"></a>

### System tray — `c1b878b63f80e733`

Target: `ports/desktop/pyqt-official/systray-c1b878b63f80e733.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original icons, menu, message fields and notification actions retained. Tray starts hidden and Show icon unchecked; inspect never shows it or sends a notification. Quit closes this handle, with no QApplication quit or global quit-policy change. Native X hides the owned tray; message feedback is asynchronous. Tray hides before callback disconnection/native deletion.

Native acceptance: Expect Systray, tray_visible false, icon_index 1 and original message text. Explicitly toggle showIconCheckBox; verify only this demo’s menu-bar/tray icon appears. Change all icons, minimize/restore with owned menu actions, explicitly send a message and exercise messageClicked feedback where supported. Native X must remove the icon; named close/quitAction must destroy tray/menu/dialog/actions while FontLab remains running. Record platform tray availability/notification restrictions.

<a id="batch-5-de30d23621025fe6"></a>

### Application chooser — `de30d23621025fe6`

Target: `ports/animation/pyqt-official/appchooser-de30d23621025fe6.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original four corner icons, selected centre geometry, restore-properties policy and default geometry animations retained. Invisible owned QPushButtons relay graphics-item clicks into real QState transitions; native QGraphicsWidget geometry replaces custom PyQt signals. Exact images replace compiled resources.

Native acceptance: Expect Application Chooser, item_count 4 and four 64x64 corner geometries. Natively click each controls items entry: selected geometry becomes [86,86,128,128], previously selected icon returns to its original corner and native geometry interpolates. Check up/down image scaling, alignment and no visible relay buttons. Close mid-transition and verify scene/item/state-machine/animation destruction.

<a id="batch-5-de35a965dfcfd678"></a>

### Shared memory (blocked) — `de35a965dfcfd678`

Target: `ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py`. Status: **blocked**, native **unexecuted**. Licence: `GPL-3.0-only`.

Adaptation: QSharedMemory exists, but the host exports no detach() and data/constData have no documented Python byte-buffer signature. The build reports the precise blocker without allocating an IPC key/segment. No in-process substitute is presented as IPC.

Native acceptance: Confirm launcher/build raises the recorded NotImplementedError before any UI or IPC mutation. Recheck the actual host QSharedMemory.detach/data/constData exports; keep blocked unless safe byte access and explicit detach are proved. If exported in a future binding, native acceptance must include an owned unique key, two independent peers, image transfer, failure paths and destruction/unlink of the segment.

<a id="batch-5-fcfaf9667206bbd6"></a>

### Colliding mice — `fcfaf9667206bbd6`

Target: `ports/graphicsview/pyqt-official/collidingmice-fcfaf9667206bbd6.py`. Status: **implemented**, native **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`.

Adaptation: Original seven mice, collision-aware steering/drawing and cheese background retained. Timers have an owned parent, integer 30 ms intervals and tracked slots; each stops before close. Local RNG avoids host-global seeding; coincident mice guard zero-length acos calculations. Positions use components and native mapping methods, never wrapper operators.

Native acceptance: Expect Colliding Mice, mouse_count 7, original cheese background and animated mice. Observe movement, collision ear colours and steering away from the edge; pan/resize the view. Put two controls mice at the same position and confirm no divide-by-zero or paint exception. Close while all seven timers run; verify timer/scene/item destruction and a clean relaunch.

## Batch 6: widgets, main windows, painting and rich text

All **29 requested identities** are accounted for: **28 implemented**, one blocked
because native `QTextObjectInterface` is absent. The batch adds **48 exact resource
copies**, never compiled resource modules. Source provenance and licence notices
are retained; 28 BSD headers retain the existing unresolved collection GPL scope,
and textedit selects the explicit GPLv3 alternative in its original header.
No native acceptance or commit is claimed. The controller owns those gates.

For every implemented entry: launch by ID; inspect twice without interacting;
drive its controls and the checks below; close while timers/dialogs are active;
process deferred deletes, verify root/children/dialogs/scene items are destroyed,
all Python signal targets are disconnected, the launcher registry is empty and
FontLab remains alive. Relaunch and repeat close. Record paint/virtual-dispatch,
overload errors and output artefacts separately from launch/inspect/close evidence.
Only explicitly accepted file, print and clipboard actions may touch user state;
use controller-owned temporary fixtures/destinations and restore clipboard after
the explicit clipboard check. Print/Preview start with owned PDF output and never
run during inspect; PDF acceptance must verify the selected native destination.
Verify host application style/palette/settings before and after the batch.

`controls` keeps source widget names plus useful root methods, and `window` is the
root. Array views/controls live on the retained Python subclass (for example
`h.widget.renderAreas`, `h.widget.operationComboBoxes`, `h.widget.digitButtons`).
Dynamic dialogs are `h.controls['active_dialog']`; selecting/cancelling/accepting
them runs retained continuations. File dialogs use `selectedFiles()` only on
accept; no static blocking chooser or dialog `exec` is used.

The exported Qt5 APIs and asynchronous dialog semantics were checked against
the native Echopy stubs and the [QDialog reference](https://doc.qt.io/archives/qt-5.15/qdialog.html).
Highlighting follows the exported virtuals and [QSyntaxHighlighter reference](https://doc.qt.io/archives/qt-5.15/qsyntaxhighlighter.html).

### Batch 6 4efac54bae01fc62

`Official dockwidgets` — `ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original letter, customer/paragraph docks, undo and toolbars retained. HTML save uses an owned asynchronous file dialog and UTF-8 stdlib I/O; printing uses a dialog-owned PDF-configured QPrinter. Four exact icon files replace compiled resources.

Native: Verify initial NAME/ADDRESS placeholders and company letter; select a customer and two standard paragraphs, edit and Undo. Float/re-dock each dock and toggle View actions. Save HTML to an owned temporary file, reopen and inspect text. Open/cancel Print, then explicitly accept an owned PDF destination and validate the PDF.

### Batch 6 60d40ce5671653cf

`Official menus` — `ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original menu actions, checkable formatting and alignment action group retained. Context menu uses popup instead of exec; About/Qt information is owned and asynchronous. Print remains the original informational menu action.

Native: Trigger New/Open/Save/Print/Undo/Redo/Cut/Copy/Paste and verify their infoLabel text. Toggle Bold/Italic and all four exclusive alignments. Right-click, dismiss and reopen the context menu; About/Qt remain responsive. Close with the popup visible.

### Batch 6 09afeea11be83f4f

`Official recentfiles` — `ports/mainwindows/pyqt-official/recentfiles-09afeea11be83f4f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: One shared owned temporary INI supplies all example windows; no Trolltech/user settings are read or written. UTF-8 stdlib file I/O replaces stream operators. New/Exit operate on owned windows only; the five recent actions share settings and the retained window list is cleared on close.

Native: Save six uniquely named owned files across two New windows; verify the five-entry order and labels synchronize, re-save one to move it to the front, and open a recent item. Cancel Open/Save As. Trigger Exit and confirm FontLab windows remain. Named close destroys both example windows and removes the owned INI; a new launch starts with no recent files.

### Batch 6 2d36e0fe43f5d49a

`Official separations` — `ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original CMY per-pixel extraction, recolouring, inversion, brightness recombination and image drag retained. qRed/qGreen/qBlue use integer channel extraction; custom imageChanged signals become released subclass callbacks. Colour/open/save dialogs are asynchronous; drag geometry uses components and QBuffer data remains QByteArray.

Native: Load an owned small RGB image with red/green/blue/white/black pixels. Verify Cyan/Magenta/Yellow and final composites, invert each plane, choose/cancel an ink colour and exercise all five brightness levels. Save/reopen PNG and verify pixels. Drag the final image to an owned target, cancel a drag and then close; no source is destroyed during drag.

### Batch 6 912e5c751b20ce97

`Official concentriccircles` — `ports/painting/pyqt-official/concentriccircles-912e5c751b20ce97.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: All four float/int and aliased/antialiased views retained. Integer QRect/QColor channels and alpha are explicit; four tracked timer targets stop before deletion, and painters end in finally.

Native: Verify the 2x2 labels/views and growing frames inspect list. Observe differences in float/int placement and antialiasing; resize while animated. Close with the 100 ms timer active, process deferred deletes and relaunch with frames reset.

### Batch 6 13a6bb9a9d2b9037

`Official painterpaths` — `ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Nine original paths, fill-rule/gradient colours, pen width/colour and rotation controls retained. Numeric enum casts become integers, brushes/colours are explicit value objects and painter cleanup is guaranteed.

Native: Verify nine rendered paths including text, cubic curve and star. Drive both fill rules, both gradient colours, pen colour, width 0/7/20 and rotation 0/45/360. Resize; check all nine views change consistently and close during repaint.

### Batch 6 b2d717e4d43806d2

`Official svgviewer` — `ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original bubbles SVG default plus cubic/spheres resources retained byte-for-byte. Native/Image/OpenGL renderers remain; QGL.SampleBuffers is replaced by QGLFormat.setSampleBuffers. The unavailable OpenGL branch is guarded. File dialogs are asynchronous, viewport callbacks are forgotten before replacement, and geometry uses components.

Native: Verify bubbles SVG appears on launch. Open cubic.svg and spheres.svg from copied assets; toggle Background/Outline, wheel zoom and pan. Switch Native/Image and, if hasOpenGL returns true, OpenGL and high-quality antialiasing repeatedly. Try missing/invalid SVG, cancel file selection, close after viewport replacement and confirm all scene/items/viewports are destroyed.

### Batch 6 c12a2071adbab88b

`Official transformations` — `ports/painting/pyqt-official/transformations-c12a2071adbab88b.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original clock/house/Qt/truck paths and cumulative translation/scaling/rotation retained. Text centring subtracts plain coordinates instead of negating QPointF; pen styles and fill brushes use verified native overloads.

Native: Choose each of four shapes. Set each of three operation combos to Translate/Scale/Rotate in different orders and compare cumulative transformed views with original. Resize and render axes/outlines/text. Close and relaunch after all transformations.

### Batch 6 c56cf1699b07b350

`Official calendar` — `ports/richtext/pyqt-official/calendar-c56cf1699b07b350.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original seven-column QTextTable calendar, month/year and font-size controls retained, including 640x256 startup size. Background highlighting uses explicit brush/colour values; cursor/table operations remain native.

Native: Select February 2024 and verify all 29 days, Monday-first headings and row boundaries. Select another month/year, font sizes 1/18/64, and the current month with today highlighted. Inspect month/year/font_size and title; close after repeated document replacement.

### Batch 6 c997677a2bdb4f34

`Official orderform` — `ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original sample Mr Smith letter, editable quantities/privacy choice and tabbed documents retained. Details validation and discard confirmation are asynchronous; malformed quantities leave the dialog open with an inspectable error. Printing uses a dialog-owned printer configured for owned PDF output.

Native: Verify the initial sample letter and four products. New details: accept customer/address, quantities 0/2/negative and both offers choices; inspect added tabs/document tables. Enter nonnumeric quantity and verify no accept; leave details blank and test Yes/No discard. Cancel and explicitly accept PDF printing to an owned path; validate text and page layout.

### Batch 6 428c50abcef7adfe

`Official syntaxhighlighter` — `ports/richtext/pyqt-official/syntaxhighlighter-428c50abcef7adfe.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original C++ keyword/class/function/string/comment rules and multiline block state retained. File reads use UTF-8 stdlib I/O, dialogs and menus use tracked callbacks; native QSyntaxHighlighter virtuals/setFormat remain.

Native: Open an owned C++ fixture containing keywords, Qt classes, calls, strings, // comments and a multiline /* */ comment. Verify colours/styles and subsequent block recovery after edits; New clears the document. Cancel Open and select a missing file; inspect the error without losing the document. Close after repeated rehighlighting.

### Batch 6 b34b2f696a977e74

`Official textedit` — `ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py` — **implemented**, native acceptance **unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Adaptation: Original rich-text formatting, lists, alignment, undo/redo, clipboard actions, document writer, sample HTML and platform icons retained. Save/New/Open/Close prompts use continuations. The sample resource is never a save target and its owned document image cache resolves original :/ URLs and its base URL resolves relative images. Print/Preview use dialog-owned PDF-configured printers; Export PDF uses an explicit asynchronous destination. All clipboard and preview connections are tracked.

Native: Verify sample HTML/logo and original 700x800 window. Format selected words with bold/italic/underline, family/size/colour, all alignment and list styles; test undo/redo, cut/copy/paste only on owned text. Save/reopen HTML and ODT; never overwrite copied example.html. Test Save/Discard/Cancel for New/Open/Close, including Save As cancellation. Preview and explicitly export an owned PDF, validate pages/text/images, close while clipboard/preview callbacks are live and verify disconnection.

### Batch 6 806fd814a2ea4d46

`Official textobject` — `ports/richtext/pyqt-official/textobject-806fd814a2ea4d46.py` — **blocked**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Blocked: QTextObjectInterface is absent from native QtGui stubs. A replacement image or HTML display would lose the inline custom SVG object-handler behavior; no fake interface, alternate Qt binding or resource module is supplied.

Native: Confirm launch reports the manifest blocker, does not create UI and leaves the host alive. Revisit only after the host exports QTextObjectInterface and supports native QTextDocument object handler registration/virtual callbacks.

### Batch 6 d6dc56a5318ffe71

`Official analogclock` — `ports/widgets/pyqt-official/analogclock-d6dc56a5318ffe71.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original hour/minute polygons, colours and minute/hour marks retained; the tracked one-second timer stops before deletion. Brush values and guaranteed painter end replace implicit conversion/destruction.

Native: Observe moving hands and marks over a minute, resize to rectangular and square shapes and verify aspect ratio/centering. Inspect title/geometry, close with the timer active, confirm native timer/widget destruction and relaunch.

### Batch 6 356e4e807f1e789f

`Official calculator` — `ports/widgets/pyqt-official/calculator-356e4e807f1e789f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original precedence, unary operators, memory and error display retained. Integer grid rows fix Python 3 division; all button callbacks are tracked and the native Button.sizeHint handler is called explicitly.

Native: Drive 2+3*4=14, 9/0=####, Sqrt of a negative number, reciprocal of zero, decimal/sign/backspace/Clear/Clear All, and MC/MS/M+/MR. Verify size hints, display_text and memory. Close after an error and relaunch at zero.

### Batch 6 b91effc45f81fbb0

`Official calendarwidget` — `ports/widgets/pyqt-official/calendarwidget-b91effc45f81fbb0.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original locale, first day, selection mode, navigation/grid, headers, date limits and formatting controls retained. Enum values are passed as integers and text-format colours as explicit brushes; locale iteration uses enumerate.

Native: Switch locale/first weekday/selection mode, grid/navigation and both header styles. Set min/max/selected date within and outside limits. Change weekday/weekend colours, header format, First Friday and May First; navigate months and inspect selected_date. Close after dateChanged/selectionChanged round trips.

### Batch 6 499e965d86347920

`Official charactermap` — `ports/widgets/pyqt-official/charactermap-499e965d86347920.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original BMP grid, fonts/styles/sizes, tooltip, selected text and explicit clipboard action retained. Python int replaces QString.toInt; indexes use integer division. characterSelected becomes a released callback and font-merging toggles are wired. Clipboard writes happen only on explicit To clipboard.

Native: Select A and a non-ASCII BMP character, verify tooltip/codepoint and appended lineEdit text. Change font/style/size and toggle automatic font merging; try invalid size. Verify inspection leaves clipboard unchanged, then explicitly copy owned sample text and restore the controller clipboard fixture. Scroll/repaint the grid and close.

### Batch 6 3040b9f6b267a196

`Official digitalclock` — `ports/widgets/pyqt-official/digitalclock-3040b9f6b267a196.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original one-second timer, LCD filled segments and blinking colon retained. The rendered display string is retained as declared Python state for meaningful inspection; timer callbacks disconnect and stop on close.

Native: Verify hh:mm with a blinking colon and inspect display_text. Wait for at least two ticks and a minute transition, resize, close with the timer active and relaunch without duplicate updates.

### Batch 6 f702b62aa47629ad

`Official groupbox` — `ports/widgets/pyqt-official/groupbox-f702b62aa47629ad.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original exclusive radios, checkable/flat groups, independent/tristate checkboxes, toggle/flat/default buttons and nested popup menu retained with native widget ownership.

Native: Test both exclusive radio groups, disabled checkable group, all checkboxes/tristate values, flat/normal/toggle buttons, popup menu and submenu. Verify group enabling and exclusivity; close with a popup visible and relaunch.

### Batch 6 16456ba02f4b79cc

`Official imageviewer` — `ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original scroll area, image label, zoom/normal/fit behavior and image printing retained. Opening and printing are asynchronous; zoom multiplies plain width/height integers rather than QSize wrappers. An unused default host printer is excluded from construction.

Native: Open an owned PNG/JPEG and an invalid file, cancel selection, zoom to both limits, Normal Size and Fit to Window, resize and verify scrollbar centering/action enablement. Cancel Print, then explicitly write an owned PDF and verify image scaling; close with a dialog open.

### Batch 6 84cb59e07adfae2c

`Official lineedits` — `ports/widgets/pyqt-official/lineedits-84cb59e07adfae2c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original echo modes, validators, alignments, input masks and read-only controls retained. Removing a validator uses the native null pointer None via setValidator, without assigning None to a native property.

Native: Drive all four echo modes, integer/double/no validator, each alignment, phone/date/license/no mask and both read-only states. Type valid and invalid values and inspect text/control state. Close after validator replacement.

### Batch 6 8e5aa13798c2763c

`Official scribble` — `ports/widgets/pyqt-official/scribble-8e5aa13798c2763c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original drawing, pen width/colour, image open/save/clear and printing retained. resizeImage now returns the resized copy to preserve the intended image rather than rebinding the wrong instance. Coordinates/radii are integers; painters end reliably and save/open/close confirmations are asynchronous. Image format names decode QByteArray.data; printing starts with owned PDF output.

Native: Draw with mouse press/move/release, resize larger/smaller without losing strokes, change/cancel pen colour and width 1/5/50. Save/reopen each available PNG/JPEG format in owned files, Clear, and test Save/Discard/Cancel on Open/Close including cancelled Save As. Explicitly validate owned PDF print output, then close while dirty.

### Batch 6 248e64416b9b218c

`Official shapedclock` — `ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original frameless masked clock, drag behavior and context Exit retained. Global position arithmetic subtracts components, QRegion geometry is integer, Exit closes only owned windows and the timer stops before deletion.

Native: Verify circular mask at several sizes and both hand polygons. Drag by the left button and confirm the offset remains stable; open context menu and Exit without quitting FontLab. Close during a drag/timer tick, verify mask/timer/widget destruction and relaunch.

### Batch 6 36805750b888fba6

`Official sliders` — `ports/widgets/pyqt-official/sliders-36805750b888fba6.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original horizontal/vertical slider-scrollbar-dial synchronization, min/max/value, inversion and orientation controls retained. Custom PyQt group valueChanged relays use each native dial signal; all native connections are tracked.

Native: Change value in each slider/scrollbar/dial and spinbox; verify horizontal=vertical. Change min/max, invert appearance and key bindings, switch orientation and exercise keyboard/page steps. Close during changes and relaunch with range 0..20/value 5.

### Batch 6 468179092748a72e

`Official spinboxes` — `ports/widgets/pyqt-official/spinboxes-468179092748a72e.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original integer, percent/currency, date/time, meeting-format and floating precision controls retained; native overloaded signals use explicit QString/int signatures and date/time properties use read.

Native: Test integer -20/20, zoom Automatic/1000%, currency, date/time limits, every meeting format including time-only. Drive decimals 0/2/4/100 across the three double boxes, test step/wrapping limits and inspect values. Close after repeated format changes.

### Batch 6 9e21c6536fda7a23

`Official styles` — `ports/widgets/pyqt-official/styles-9e21c6536fda7a23.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original gallery and progress timer retained. Style and palette changes are scoped to the owned root and the created style is parented; FontLab application style/palette remain unchanged. Integer progress updates advance by at least one until maximum, fixing truncation stall.

Native: Record FontLab application style/palette before launch. Change every available style and standard/original palette, disable/re-enable groups, exercise tabs and widgets, and observe progress reaching maximum. Verify host style/palette unchanged and timer stopped after close/relaunch.

### Batch 6 e63bffc17abf2fde

`Official tetrix` — `ports/widgets/pyqt-official/tetrix-e63bffc17abf2fde.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original board, pieces, key controls, next preview, scoring/levels and timer retained. Custom score/level/line signals become released LCD callbacks; timer intervals/grid dimensions are integer and native base virtuals are explicit. Exit is owned; the demo does not reseed the host RNG.

Native: Start, move/rotate/drop and pause/resume; verify next preview/LCDs/inspect board, score and level. Fill/clear a line, test wall/floor collisions and game-over restart. Verify both rotation directions for nonsquare pieces. Close while QBasicTimer is active and verify released LCD callbacks/timer destruction.

### Batch 6 509e781f1267967f

`Official wiggly` — `ports/widgets/pyqt-official/wiggly-509e781f1267967f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original animated text, sine-table offsets, hues and line-edit control retained. QBasicTimer uses the exported three-argument start(interval, timerType, receiver), integer text coordinates and explicit QWidget.timerEvent fallback.

Native: Change lineEdit text including empty/non-ASCII input and inspect text/step. Observe each character moving/colouring over multiple timer events; resize and close while active. Confirm timer stops and no stale callback on relaunch.

### Batch 6 136c45cc9f97c218

`Official windowflags` — `ports/widgets/pyqt-official/windowflags-136c45cc9f97c218.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original type/hint radio/checkbox controls and owned preview retained. Zero starts the integer flags mask instead of calling an enum type; setWindowFlags invokes QWidget explicitly and preview geometry uses coordinate components.

Native: Exercise each Window/Dialog/Sheet/Drawer/Popup/Tool/ToolTip/Splash type and every hint, checking preview text and geometry. Drag and close/reopen the preview; verify parent remains responsive even for Popup. Named close destroys root/preview and all button callbacks; host windows remain.

## Batch 7: item views, graphics, drag/drop and owned network

All 27 entries are implemented; every new native acceptance state is **unexecuted**.
The common acceptance steps above apply to every row. Tests use strict doubles and
real owned localhost transport; they do not prove PythonQt virtual dispatch or rendering.
Network decision D4 permits only each port's numerical 127.0.0.1/free-port peer; there
is no DNS, internet, system broadcast, host settings/cache or global cursor change.
Native TCP/UDP clients and HTTP manager explicitly disable proxies.

### Batch 7 43c6c2f6f5f036d3

`Official delayedencoding` — `ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original SVG view/Export and lazy PNG drag retained. pyqtSignal becomes the native retrieveData virtual callback with a per-drag encoded flag; file assets, component-safe values, balanced painters and owned buffer replace resource registration.

Native: Check SVG and Export icon; inspect encoding_count=0. Start a real native drag, cancel once (no requested PNG), then drop into Drop Site or a controller-owned file target. Confirm retrieveData dispatch, valid PNG bytes/size, one encoding per drag and responsive FontLab. Finish/cancel any drag before named close; verify no MIME producer/slot survives.

### Batch 7 fa6823667fdb918f

`Official dropsite` — `ports/draganddrop/pyqt-official/dropsite-fa6823667fdb918f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original drop area, MIME/content table and Clear/Quit retained. Direct owned change callback replaces custom signal; raw bytes use QByteArray.data(), and QImage values use QPixmap.fromImage.

Native: Drive dropArea with native text, HTML, URL, image and binary drags; formats must show all MIME types and binary 00 FF correctly. Confirm displayed content changes on drop, drag-leave resets and clearButton empties rows. Close with a drag hovering; no stale Python callback.

### Batch 7 a96a7978c0b9f6ee

`Official anchorlayout` — `ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: All seven labelled proxy buttons and all 24 original anchors retained, with typed background brush and parent-owned scene; no wrapper arithmetic.

Native: Check labels A-G and each proxy geometry. Resize window and anchorWidget to narrow/wide/tall sizes; verify original horizontal/vertical centre relationships and min/preferred/max sizes. Click all buttons (upstream has no callback). Named close must destroy scene and seven proxies.

### Batch 7 fff97a435b73d548

`Official elasticnodes` — `ports/graphicsview/pyqt-official/elasticnodes-fff97a435b73d548.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original nine-node/twelve-edge force graph, arrows, drag, keyboard and zoom retained. Component point offsets replace wrapper operators; private RNG, integer timer interval, explicit native handlers and stopMotion own teardown.

Native: Expect node_count=9, edge_count=12. Drag centerNode and another node; confirm edges follow and timer settles. Arrow keys move the centre; space/enter shuffle; wheel/+/- zoom within source limits. Exercise step/scaleView, resize/background/shadows and arrow rendering; close during active motion, then relaunch.

### Batch 7 a58650b5461c0f48

`Official padnavigator` — `ports/graphicsview/pyqt-official/padnavigator-a58650b5461c0f48.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original 3x3 pad, native key/state transitions, history, flip/selection animations and optional OpenGL retained. Exact form.ui loads natively, PNGs load from files; entered callbacks set fill instead of a custom Qt meta-property. Typed easing values, component coordinates and explicit animation/state shutdown.

Native: Verify nine icons/background and hostName/form controls. Any key dismisses splash; arrows wrap selection in both directions. Return/Enter flips to the form, edits stay owned, and returns restore the selected history position. Check tilt, opacity, half-flip scale/fill and resize fit. Close midway through animation and confirm machine/animation shutdown. Exercise software viewport and OpenGL when available.

### Batch 7 9dab02b61cebbdb7

`Official basicsortfiltermodel` — `ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original ten mails, dual views, date-display filtering and case/syntax/column controls retained. Proxy model moves to QtGui, native properties use read(), parent ownership and explicit native fallback.

Native: Expect source_rows=10, initial proxy_rows=4. Set sender pattern Andy (2), no match (0), empty (10); exercise regexp/wildcard/fixed string, case toggles and all three filter columns including displayed date. Click headers to sort, check real proxy/view order. Close/relaunch without selection callbacks.

### Batch 7 0a3b15766909bdc3

`Official coloreditorfactory` — `ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original names/colours and colour-list factory retained. QMetaType.type("QColor") resolves the native type; a per-delegate factory/creator plus explicit QColor/index conversion replaces pyqtProperty and leaves the host default factory unchanged.

Native: Expect Alice/aliceblue, Neptun/aquamarine, Ferdinand/springgreen. Double-click a colour cell, confirm native creator virtual dispatch and colour swatches; choose a new colour and commit/cancel. Name editing must use the standard editor. Check a separate host table keeps its editor factory; close with an editor open and verify native factory/creator lifetime.

### Batch 7 cc95f9719b8e4eda

`Official combowidgetmapper` — `ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original five records, rich addresses, Home/Work/Other and mapper navigation retained. QStringListModel lives in QtGui; mapping property uses native QByteArray and a private model field.

Native: Next/Previous traverse Alice, Bob, Carol, Donald, Emma with original addresses/types 0,1,2,0,2; endpoint buttons disable correctly. Change name/address/type, leave the editor and navigate back; verify actual mapper commits. Inspect current_index and row_count=5; close with an editor focused.

### Batch 7 029ea0dabe87ae57

`Official customsortfiltermodel` — `ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original ten mails and text/date filters retained. QtGui proxy plus scalar Julian-day/ISO comparisons avoid Qt wrapper ordering; QDateTime values bypass email matching correctly.

Native: Expect initial proxy_rows=5; Sports gives 3, no match 0, empty 10 with original inclusive dates. Change fromDateEdit/toDateEdit to narrow/empty/inverted ranges. Exercise syntaxes/case and sender-email/date sorting; confirm actual native lessThan/filterAcceptsRow dispatch and visible order. Close/relaunch.

### Batch 7 4b8851287931abd0

`Official dirview` — `ports/itemviews/pyqt-official/dirview-4b8851287931abd0.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Build defers sample-file creation and QFileSystemModel.setRootPath/root-index setup to an owned tracked single-shot timer. Inspection reports deferred loading state; close cancels setup before filesystem work starts. Original read-only QFileSystemModel/tree retained; argv and host filesystem defaults become an owned temporary directory containing example.txt.

Native: Launch returns before sample-file creation or filesystem-root setup. Let loadTimer fire and wait for Qt directory loading. Close before that first tick and verify no sample/root setup occurs. Wait for model directory load; root_path must be owned and read_only true, column_count=4. Expand/select example.txt, resize/sort columns and confirm editing cannot write. Named close destroys watcher/model and removes the owned directory; host files stay unchanged.

### Batch 7 67170c89593ad35e

`Official fetchmore` — `ports/itemviews/pyqt-official/fetchmore-67170c89593ad35e.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Build defers the 205 owned fixture writes in batches of at most 32 per timer tick and directory enumeration to a separate owned single-shot timer. Native entryList tuples normalize to a list; inspection exposes loading without scanning, and close stops both timers. Original directory list, 100-row fetch batches, alternating backgrounds and population log retained. Starts with 205 owned files; custom signal becomes an owned callback set after log creation. Fix inclusive insertion range and reject child/empty fetches.

Native: Launch starts with an empty model/loading=true and no fixture writes. Let fixtureTimer create 205 files in batches of 32 and scanTimer list the directory, then exercise the fetch controls below. Close before loading or between fixture ticks; no writes/scans may follow close. Drive lineEdit to owned fixtures. Repeated fetchMore should insert 100,100,7 rows for 205 files plus dot entries; verify rowsInserted bounds, alternating backgrounds and log totals. Empty/missing directory must not crash or insert an invalid range. Scroll the real view to trigger native canFetchMore/fetchMore; close while fetching.

### Batch 7 d50ad6638357e669

`Official pixelator` — `ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original image table, grayscale circle delegate, pixel-size control and file/about/print actions retained. Exact qt.png, private model, asynchronous image/large-image/print dialogs; bounded GUI print timer and owned PDF printer replace modal loops/processEvents.

Native: Check original qt.png as circles, change pixelSizeSpinBox 4-32, load an owned PNG and cancel chooser. Trigger printAction: large-image Yes/No is async, printer defaults to an owned PDF, progress rows advance; cancel through progress and close during printing. Validate a completed PDF externally and painter/timer teardown.

### Batch 7 a59dae9770bfbefb

`Official simpledommodel` — `ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Stdlib minidom preserves element/text/comment/processing-instruction/attribute behaviour without absent QtXml. Native tree uses numeric internal IDs, async chooser and tracked model replacement; invalid XML retains the previous model.

Native: Initial root label=owned contains comment, processing instruction and child/text; headers Name/Attributes/Value. Use loadXml/openAction for a fixture with whitespace/comments/namespaces, expand all levels and verify native parent/index relationships. Malformed/missing XML sets error and retains the old tree. Replace twice, close and confirm retired/current models are destroyed.

### Batch 7 39de33366209402d

`Official simplewidgetmapper` — `ports/itemviews/pyqt-official/simplewidgetmapper-39de33366209402d.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original five records, rich addresses, age spinner and mapper navigation retained. QtGui mapper uses a private model field and tracked callbacks.

Native: Next/Previous traverse Alice/Bob/Carol/Donald/Emma with ages 20,31,32,19,26. Edit name/address/age, leave focus/navigate back and verify native mapper persistence. Endpoint buttons and current_index/row_count must match. Close with an editor focused.

### Batch 7 ddb20b1b68b18a91

`Official spinboxdelegate` — `ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original 4x2 multiplication values and 0-100 editor retained; QtGui styled delegate/model are parent-owned with explicit native editor geometry and retained controls.

Native: Initial rows [[1,2],[2,4],[3,6],[4,8]]. Double-click row 2 column 1, expect 6; commit 42 through the native editor and verify model/inspect. Test 0/100 bounds, cancellation and resizing editor geometry. Close while editing; model/delegate/editor must be destroyed.

### Batch 7 bf3b39a8c2df8e94

`Official spreadsheet` — `ports/itemviews/pyqt-official/spreadsheet-bf3b39a8c2df8e94.py` — **implemented**, native acceptance **unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Adaptation: Original 10x6 expense sheet, formula operations, date/completion delegate, menus and context actions retained, with all four companion notices. Explicit subclass clone/recursive cell evaluation, cycle guard, typed brushes/shortcuts and async arithmetic/colour/font/owned PDF preview replace unsafe/native-attribute and modal patterns.

Native: Initial total=21883; putFormula("C2","200") changes total to 21933. Drive formulaInput and all +,-,*,/,sum actions, division by zero and cyclic references; verify live cells, not just inspect. Test date formats/editor calendar/completion, colour/font/clear and context menu. Preview printer is dialog-owned and defaults to temporary PDF; validate PDF, then close with arithmetic/editor/preview open. Check native item data/clone virtual dispatch.

### Batch 7 dc59f268ee01e364

`Official stardelegate` — `ports/itemviews/pyqt-official/stardelegate-dc59f268ee01e364.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original four music rows, painted stars/diamonds and hover/release editor retained. Integer QVariant ratings replace Python objects; original rating objects remain inside the Python painter/editor. Component QSize and list polygons, explicit native fallback and balanced paint.

Native: Initial ratings [5,4,3,5]. Double-click a star cell, hover across centres including 0/5 boundaries, release to commit; cancel another editor. Verify integer model values, stars/diamonds, selection background and standard text-cell editing. Close with an editor active; no Python editing signal is left attached.

### Batch 7 cf15c3e91cdd8ded

`Official storageview` — `ports/itemviews/pyqt-official/storageview-cf15c3e91cdd8ded.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Build starts with an empty model and loading=true. An owned tracked single-shot GUI timer performs QStorageInfo.mountedVolumes(), normalizes the native tuple to a list and resets the model. Inspection reads only cached row_count/loading; close stops and disconnects the pending timer. Original ten-column mounted-volume model and size/tooltip formatting retained, with QtGui table model and QByteArray.data() decoding. Volume enumeration is read-only and deferred to an owned GUI timer; the model starts empty/loading, accepts the native tuple and caches it as a list.

Native: Launch must return before mounted-volume enumeration: inspect initially shows row_count=0/loading=true. Let the host timer fire; expect loading=false and the host count (11 reported by the controller). Repeat inspect without rescanning; close before the first tick and verify no scan occurs. Check headers and native mounted-volume count; compare root/name/device/filesystem/total/free/available/ready/read-only/valid with read-only host observations. Hover rows for all ten tooltip values and size units; expand/select/sort/resize. Repeated inspection must not refresh volumes or write to them; close model/view.

### Batch 7 79f3a23172968ad2

`Official blockingfortuneclient` — `ports/network/pyqt-official/blockingfortuneclient-79f3a23172968ad2.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original host/port/Get Fortune/status UI retained. Missing QThread/mutex/condition become WorkerDelivery with cancellable stdlib socket reads and GUI timer; owned loopback fixture sends the exact Qt_4_0 frame. Other host/port inputs are rejected before DNS/socket creation.

Native: Click getFortuneButton repeatedly; inspect fortune, statusLabel and button recovery. Change hostLineEdit/portLineEdit to foreign values and expect an owned error without network contact. Close during connect/read/drain; worker joins and listener port is released. Relaunch for fresh state; host GUI remains responsive.

### Batch 7 0bba8a80541ab04f

`Official broadcastreceiver` — `ports/network/pyqt-official/broadcastreceiver-0bba8a80541ab04f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original receiver/status/Quit retained. Native QUdpSocket writes to an owned localhost UDP socket; bounded GUI timer/stdlib recvfrom replaces the unavailable PyQt tuple readDatagram overload. No real broadcast or fixed global port.

Native: Invoke sendSample, then wait for pollTimer: expect Received datagram: "Broadcast message 1" and received list. Send multiple owned samples, verify ordering/bounded history. Inspect is inert. Close while draining, verify socket/free port and both timers released, then relaunch.

### Batch 7 90721289b8108c4f

`Official broadcastsender` — `ports/network/pyqt-official/broadcastsender-90721289b8108c4f.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original Start/Quit, one-second sender and message counter retained. Native QUdpSocket targets the port-owned localhost receiver; bounded stdlib receive drain replaces raw C-buffer readDatagram; no broadcast address or fixed port.

Native: Click startButton, observe messages 1,2,3 at one-second intervals; status/counter and received list agree. Invoke sendSample for an explicit extra datagram. No packet leaves 127.0.0.1. Close while active; sender, receiver and timers release the free port; relaunch resets message_no.

### Batch 7 fbb4e3c7288fed7c

`Official fortuneclient` — `ports/network/pyqt-official/fortuneclient-fbb4e3c7288fed7c.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original host/port/Get Fortune/status UI and asynchronous QTcpSocket retained. A WorkerDelivery-owned localhost server supplies framed UTF-16 fortunes; partial reads accumulate bytes. Numeric endpoint validation, NoProxy and no host network-session/settings writes.

Native: Click getFortuneButton repeatedly and verify distinct original fortunes/status/button recovery. Drive fragmented delivery/error via the owned peer; foreign hostCombo/portLineEdit values must fail before connection. Close with tcpSocket active and server queue pending; disconnect callbacks, abort socket, join server and release port.

### Batch 7 aad57160cfd51894

`Official fortuneserver` — `ports/network/pyqt-official/fortuneserver-aad57160cfd51894.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original server-status/Quit and seven fortunes retained. A plain-data WorkerDelivery listener binds only 127.0.0.1/free port; exact Qt_4_0 UInt16/QString wire format and owned probe replace network-session/global interface/settings behaviour.

Native: Run probe or connect a controller-owned localhost client to endpoint; decode the UInt16/QString packet and verify original fortunes/sent_count. Connect repeatedly, close during a request or full delivery queue, and confirm worker joined/free port released. No host network settings or global interfaces change.

### Batch 7 409f3d46a9555f23

`Official http` — `ports/network/pyqt-official/http-409f3d46a9555f23.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original URL/Download/Quit/progress/cancel behaviour retained with QNetworkAccessManager and NoProxy. Owned HTTP fixture/output, before-request numerical endpoint validation, exported FollowRedirectsAttribute=False, no external redirect/authentication/SSL flows; reply disconnect precedes abort/delete.

Native: Download default sample.txt, wait until downloading=false, check 38 bytes and exact owned file content. Cancel an active request and expect output removal/button recovery; /missing exercises failure. Foreign URL/port, credentials and redirects must not contact another peer. Close during active reply/progress; listener, reply callbacks and temporary files disappear. HTTPS/authentication are intentionally outside the D4 local fixture.

### Batch 7 d8803c2afaabf3d5

`Official lightmaps` — `ports/network/pyqt-official/lightmaps-d8803c2afaabf3d5.py` — **implemented**, native acceptance **unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Adaptation: Original city selection, slippy coordinates/panning, magnifier/feathered ring and night mode retained. Missing QtXml is irrelevant; QObject uses private, custom update signals become direct owned callbacks, all wrapper arithmetic is component-based. Owned HTTP PNG fixture/cache replaces internet tiles/global disk cache; replies and hold timer stop on close.

Native: Choose Oslo/Berlin/Jakarta, wait for tile_count, verify coordinates and the clearly labelled offline fixture. Pan by mouse/arrows, hold/Z magnifier and release, move lens, toggle night mode; check ring/clipping/tiling and repeated resize. Verify traffic only reaches endpoint and no host cache/browser is used. Close mid-download/hold/zoom; server joins and native replies/timers/owned tile file disappear. Geographic map imagery is not supplied.

### Batch 7 ebf87d5f5390b0fd

`Official loopback` — `ports/network/pyqt-official/loopback-ebf87d5f5390b0fd.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original 50 MiB transfer, 64 KiB payloads, Start/Quit and client/server progress retained. Native QTcpSocket sends to a WorkerDelivery-owned localhost receiver; bounded plain-data counts drain on GUI timer, NoProxy and no global cursor override.

Native: Click startButton for full 50 MiB; bytes_written/bytes_received equal total_bytes and both progress bars complete. Start again and close mid-transfer; client aborts, server worker joins, callbacks disconnect and port releases. For quick diagnostics only, set window.TotalBytes to 128 KiB; full acceptance still requires original 50 MiB. Host cursor/windows remain unchanged.

### Batch 7 98f207907001ce47

`Official threadedfortuneserver` — `ports/network/pyqt-official/threadedfortuneserver-98f207907001ce47.py` — **implemented**, native acceptance **unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Adaptation: Original threaded-server/status/Quit and seven fortunes retained. Unavailable QThread/socket-descriptor Qt worker becomes a cancellable plain Python listener/handler plus GUI timer drain; this bounded worker services accepted requests serially on an owned localhost/free port.

Native: Run probe and several controller-owned localhost clients; each must receive a complete valid Qt_4_0 fortune frame, without Qt access from a worker. Verify sent_count and close while a client is connected/queue is full; worker joins and port releases. Relaunch for fresh endpoint; host stays responsive.

## Batch 8: all 74 remaining official entrypoints

This batch implements **16** and precisely blocks **58** entrypoints. All native
acceptance states are **unexecuted**. Together with earlier batches, all **187**
catalogued `pyqt-official` entrypoints now have a disposition: **127 implemented,
60 blocked**. This accounts for the entrypoint denominator; it does not complete
native acceptance or either entire collection. Existing 128 port records and the
static source catalog are preserved. No commits or TODO changes are made here.

The eight supported Designer widgets are standalone only. Their plugin and
meta-object integration is separately blocked on missing QtDesigner. Launch by
source ID: the standalone clock is `4d24cd77c74a8801`, while the previous widget
clock keeps its name `Official analogclock`. The standalone name is
`Official designer analogclock`.

Blocker evidence comes from the exported modules/member names in the sibling
Echopy stubs, captured with SHA-256 in `tests/official_contract.json`. QtGui has
QOpenGLWidget/QOpenGLContext, but QOpenGLContext has no versionFunctions and the
QOpenGLFunctions_1_1/_2_0 wrappers are absent. No raw GL function or alternate
binding is invented. QtDBus, QtQml/QtQuick, QtRemoteObjects, QtSql, QtWebKit,
QtMultimedia, QtDesigner and QAxContainer are absent. SQLite substitution is
explicitly declined for QtSql model/delegate examples. qtdemo is blocked on its
full external launcher dependencies (including absent Quick/QML), not QWidget.

Qt API documentation was consulted through the Qt 5.15 reference embedded in
the stubs, including QUiLoader.load, QOpenGLWidget.setFormat,
QXmlSchema.load/Validator.validate and QAbstractMessageHandler.handleMessage;
also [QLocalServer's lifecycle](https://doc.qt.io/archives/qt-5.15/qlocalserver.html).
The Denviso grant matches [SPDX HPND](https://spdx.org/licenses/HPND.html).

All 14 copied assets are byte-identical originals: four UI copies for the
calculator/loaders and schema.ui plus three XSDs/six XML instances. No compiled
resource modules are copied or executed. UI XML stays unchanged on disk; its
connection section is omitted only from the in-memory load buffer so every
original connection can be recreated through the owned handle. Schema validation
uses native Qt classes, never a mock/std-lib validator at runtime. Tests inject
native response values and do not establish XSD correctness or native dispatch.

For every implemented row, apply the common five-step acceptance procedure above:
record native launch/inspect/controls/rendering under the 5 s deadline, hide/reshow,
disconnect-before-delete, deferred QObject destruction, repeated close/relaunch,
and unchanged FontLab/fonts/preferences/clipboard/global styles. Native virtual
callbacks, GL rendering and schema diagnostic dispatch remain open until tested.
For every blocked row, check actual host module/member absence, call launch(id)
and confirm the exact recorded NotImplementedError before any UI/network/process
creation; record unchanged handles/host state. Do not mark blockers passed as ports.

| Source ID | Target path | Implementation | Licence | Adaptation / blocker |
| --- | --- | --- | --- | --- |
| `a1273c8940d43221` | `ports/activeqt/pyqt-official/webbrowser-a1273c8940d43221.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QAxContainer; required native APIs: QAxWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `38465a8f4b1a229f` | `ports/dbus/pyqt-official/chat-38465a8f4b1a229f.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusAbstractAdaptor, QDBusAbstractInterface, QDBusConnection, QDBusMessage. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `ab719a6a5c3afe4a` | `ports/dbus/pyqt-official/listnames-ab719a6a5c3afe4a.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `30cfa75ad45b3447` | `ports/dbus/pyqt-official/ping-30cfa75ad45b3447.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface, QDBusReply. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `57a381bc8260c85d` | `ports/dbus/pyqt-official/pong-57a381bc8260c85d.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `54c7440bdcdc3dfc` | `ports/dbus/pyqt-official/car-54c7440bdcdc3dfc.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusAbstractAdaptor, QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `3cf5db95a691d200` | `ports/dbus/pyqt-official/controller-3cf5db95a691d200.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtDBus; required native APIs: QDBusAbstractInterface, QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `27bf65f8b059fd96` | `ports/designer/pyqt-official/calculatorform-27bf65f8b059fd96.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Original calculatorform.ui loaded with QUiLoader; both valueChanged(int) slots explicitly tracked; original spin ranges and sum display retained. |
| `960c701fa6221ac5` | `ports/designer/pyqt-official/plugins-960c701fa6221ac5.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt has no QtDesigner module or QPyDesignerCustomWidgetPlugin/QDesignerCustomWidgetInterface and no PyQt Designer Python plugin loader. plugins.py launches external Designer with PYQTDESIGNERPATH/PYTHONPATH; that integration cannot run in the host. Eight plain widgets have separate standalone ports; HelloGLWidget is separately blocked. |
| `4d24cd77c74a8801` | `ports/designer/pyqt-official/analogclock-4d24cd77c74a8801.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Standalone green clock, hour/minute hands and timezone offsets retained. Owned 1 s timer; native QTime notification converted to JSON text. Designer plugin/meta-properties/signals blocked separately. |
| `9941e3c752b3a3b7` | `ports/designer/pyqt-official/bubbleswidget-9941e3c752b3a3b7.py` | implemented | GPL-3.0-only | Standalone bubbles retain mouse creation/expansion, rising motion, random gradients, colour/count/author setters and start/stop. All point arithmetic uses components; QColor channels are integers and ellipse uses QRectF; two timers owned. No host-global RNG reseeding. Designer integration separately blocked. |
| `1321540b04f33117` | `ports/designer/pyqt-official/counterlabel-1321540b04f33117.py` | implemented | GPL-3.0-only | Standalone counter preserves range/offset/int-and-string notifications and scaled text. Original initial setValue(123) remains out of range so displays 1. QPointF text overload and scalar subtraction replace unsafe overload/negation; zero metrics dimensions guarded. Designer integration separately blocked. |
| `7ba49e67588b1329` | `ports/designer/pyqt-official/datetimeedit-7ba49e67588b1329.py` | implemented | HPND AND GPL-3.0-only | Both standalone date/time editor subclasses retain popup/calendar settings and resetters. Explicit native protected mousePressEvent; calendarWidget() replaces PyQt typed findChild. Python layout/calendar references have private names. Original Denviso HPND permission retained; collection GPL scope unresolved. Designer integration separately blocked. |
| `5941e31267112c98` | `ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py` | blocked | GPL-3.0-only | PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. |
| `de4979a99c6d0bed` | `ports/designer/pyqt-official/multipagewidget-de4979a99c6d0bed.py` | implemented | GPL-3.0-only | Original two pages, insertion/removal, combo selection, current-index and page-title setters retained. Private layout name avoids native layout slot shadowing. Python notifications replace unavailable PyQt signals; Designer integration blocked separately. |
| `773db5c24ae98ffb` | `ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py` | implemented | GPL-3.0-only | Original star/polygon path, angle/sides/radii/gradient setters retained. Repair upstream max(3, QColor) typo to copy QColor; minimum three sides and clamped angle retained. Designer integration separately blocked. |
| `bcfa5de0140286d5` | `ports/designer/pyqt-official/pydemo-bcfa5de0140286d5.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Original read-only HTML, author inheritance and relative text zoom retained; zoom changes exposed in inspect notifications. Designer integration separately blocked. |
| `5125860585e98b3a` | `ports/designer/pyqt-official/pythonconsolewidget-5125860585e98b3a.py` | implemented | GPL-3.0-only | Original explicit Python expression evaluation, qApp access and successful-command Up/Down history retained. Evaluation starts only on Return/control, never inspect; errors now visible in inspect. No process/global event loop construction. Designer integration separately blocked. |
| `0ad3432ccdca7ac0` | `ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py` | implemented | GPL-3.0-only | Original seven fortunes, Qt_4_0 UInt16/QString framing and duplicate retry retained. Create an owned QLocalServer peer; lock endpoint to a unique short temporary socket path. Fragmented payload validation and tracked retry/timeout timers; no request in inspect. Abort sockets, close server and remove temporary path on close. |
| `a14d08fe23965bec` | `ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py` | implemented | GPL-3.0-only | Original seven-fortune QLocalServer retained at an owned short unique socket path. Add an explicit owned-client test button; retain status/Quit. Reuse original Qt fortune wire framing. Accepted sockets remain owned by server, aborted before deletion; never remove another server endpoint. |
| `74af8d8d2d7774b8` | `ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtMultimedia; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `c391afd8516131e1` | `ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtMultimedia; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat, QAudioOutput. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `f6d352360ae9bdfb` | `ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudioEncoderSettings, QCamera, QCameraImageCapture, QCameraViewfinder, QImageEncoderSettings, QMediaMetaData, QMediaRecorder, QMultimedia, QVideoEncoderSettings. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `5eb4b9eaa2d5c9dc` | `ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAbstractVideoBuffer, QMediaContent, QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe, QVideoWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `a57a89e523c75b7f` | `ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QGraphicsVideoItem, QMediaContent, QMediaPlayer. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `481c128fba3a714b` | `ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QMediaContent, QMediaPlayer, QVideoWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `c82d1af7d1a7b0cf` | `ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Original native QWidget/OpenGL QOpenGLWidget 30-circle QPainter comparison and Qt text retained. Apply four-sample format only to owned GL widget; no global default-format mutation. Tracked 50 ms timer; both painter contexts always end. |
| `303ea3ee09c4677d` | `ports/opengl/pyqt-official/grabber-303ea3ee09c4677d.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. |
| `1ad60855ca28f3cc` | `ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. |
| `b383fecf912548bb` | `ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. |
| `fcada4fff6524fcf` | `ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. |
| `ed6d42d4faa7e0bb` | `ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted. |
| `5a8e48d2a1396cea` | `ports/pyuic/pyqt-official/compile-on-the-fly-5a8e48d2a1396cea.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Exact demo.ui loaded via QUiLoader instead of PyQt loadUiType code generation. Explicit tracked Add-items auto-slot, original Clear and OK wiring. Runtime UI behavior retained; Python code generation itself is unavailable. |
| `b7db02f540cc7559` | `ports/pyuic/pyqt-official/load-ui1-b7db02f540cc7559.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Exact demo.ui loaded via QUiLoader instead of PyQt loadUi. Track original Clear and OK wiring. Preserve original no-Python-slot behavior: Add items does nothing. |
| `b9660f4ee653ca01` | `ports/pyuic/pyqt-official/load-ui2-b9660f4ee653ca01.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Exact demo.ui loaded via QUiLoader, replacing PyQt loadUi(target). Track original Add-items auto-slot, Clear and OK. Root is loader-created owned QDialog; UI behavior retained without generated PyQt classes. |
| `8847cbce50b72500` | `ports/qml/pyqt-official/adding-8847cbce50b72500.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `dd226ba9fbb7b330` | `ports/qml/pyqt-official/attached-dd226ba9fbb7b330.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `eb7a89f07f63cca7` | `ports/qml/pyqt-official/binding-eb7a89f07f63cca7.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, QQmlProperty, QQmlPropertyValueSource, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `ad499afe23726248` | `ports/qml/pyqt-official/coercion-ad499afe23726248.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `6417cdcf1bfd1752` | `ports/qml/pyqt-official/default-6417cdcf1bfd1752.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `81a6f0d16c203608` | `ports/qml/pyqt-official/grouped-81a6f0d16c203608.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `75ca5ac77ecefd6d` | `ports/qml/pyqt-official/methods-75ca5ac77ecefd6d.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `d0a18273fa604bb6` | `ports/qml/pyqt-official/properties-d0a18273fa604bb6.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `0a13f60f5f0561db` | `ports/qml/pyqt-official/signal-0a13f60f5f0561db.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `738a22ef3062ed51` | `ports/qml/pyqt-official/valuesource-738a22ef3062ed51.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, QQmlProperty, QQmlPropertyValueSource, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `85a56a1f3c25ccca` | `ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py` | blocked | GPL-3.0-only | The full qtdemo launcher delegates to PyQt executables and qmlscene (menumanager.py launchExample/launchQmlExample), including QtQuick/QtQml examples. FontLab exports neither QtQuick nor QtQml and cannot load PyQt as a second Qt runtime. Qt Assistant remote control is an external dependency too. A reduced menu disabling these launch behaviors would not preserve the pinned launcher; blocked on these composite dependencies, not on QWidget. |
| `835281a1ab864833` | `ports/quick/pyqt-official/animation-835281a1ab864833.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `36246fcbffecdeba` | `ports/quick/pyqt-official/canvas-36246fcbffecdeba.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `e1316fee99c63555` | `ports/quick/pyqt-official/abstractitemmodel-e1316fee99c63555.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `68d664f95f48ce52` | `ports/quick/pyqt-official/objectlistmodel-68d664f95f48ce52.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `b64d66dbce7274fe` | `ports/quick/pyqt-official/stringlistmodel-b64d66dbce7274fe.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `34538a4e2600b918` | `ports/quick/pyqt-official/customgeometry-34538a4e2600b918.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickItem, QQuickView, QSGFlatColorMaterial, QSGGeometry, QSGGeometryNode, QSGNode, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `6b1f4f5590a5518a` | `ports/quick/pyqt-official/chapter1-basics-6b1f4f5590a5518a.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `8d1557cbfed9c7a0` | `ports/quick/pyqt-official/chapter2-methods-8d1557cbfed9c7a0.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `3cd3713a5dc9f6dc` | `ports/quick/pyqt-official/chapter3-bindings-3cd3713a5dc9f6dc.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `831ac8ea61da03f3` | `ports/quick/pyqt-official/chapter4-custompropertytypes-831ac8ea61da03f3.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQuickItem, QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `b88e7eb0fcb53264` | `ports/quick/pyqt-official/chapter5-listproperties-b88e7eb0fcb53264.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtQuick / QtQml; required native APIs: QQmlListProperty, QQuickItem, QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `4dbe92cd1e720dce` | `ports/remoteobjects/pyqt-official/modelviewclient-4dbe92cd1e720dce.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `781a3a959215eb81` | `ports/remoteobjects/pyqt-official/modelviewserver-781a3a959215eb81.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost, QRemoteObjectRegistryHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `54cbd9afababdf71` | `ports/remoteobjects/pyqt-official/directconnectdynamicclient-54cbd9afababdf71.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `2f1e2f679775d89e` | `ports/remoteobjects/pyqt-official/directconnectdynamicserver-2f1e2f679775d89e.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `333f0272885ca1b7` | `ports/remoteobjects/pyqt-official/registryconnecteddynamicclient-333f0272885ca1b7.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `b83377c9b48aec14` | `ports/remoteobjects/pyqt-official/registryconnecteddynamicserver-b83377c9b48aec14.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost, QRemoteObjectRegistryHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `0b0d8d2fae153e5e` | `ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `2c4c366f259d7d80` | `ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlQuery, QSqlQueryModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `9030a87a532b8d8f` | `ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel, QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `0677ebfd7fa2cc60` | `ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtSql; required native APIs: QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed. |
| `8d5ea81a74e30222` | `ports/webkit/pyqt-official/domtraversal-8d5ea81a74e30222.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `f4000cf8ca288375` | `ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `6ed36280660df7ea` | `ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `ca47b83fbf3f31b9` | `ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `47298251b3c83ecf` | `ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `ae16288fede27692` | `ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py` | blocked | BSD-3-Clause AND GPL-3.0-only | PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. |
| `1e5d0f7289e1b36e` | `ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py` | implemented | BSD-3-Clause AND GPL-3.0-only | Exact schema.ui, three XSDs and six XML instances copied. Preserve native QXmlSchema/Validator, native diagnostic callback, highlighter and error cursor/full-width selection. Defer initial validation to owned timer. Reject DTD/entities/schema locations/imports/includes before native evaluation; QByteArray plus explicit empty base QUrl prevents URL-loading overloads. No stdlib XSD substitute. |

### Batch 8 a1273c8940d43221

`Official webbrowser` — `ports/activeqt/pyqt-official/webbrowser-a1273c8940d43221.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QAxContainer; required native APIs: QAxWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 38465a8f4b1a229f

`Official chat` — `ports/dbus/pyqt-official/chat-38465a8f4b1a229f.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtDBus; required native APIs: QDBusAbstractAdaptor, QDBusAbstractInterface, QDBusConnection, QDBusMessage. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 ab719a6a5c3afe4a

`Official listnames` — `ports/dbus/pyqt-official/listnames-ab719a6a5c3afe4a.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 30cfa75ad45b3447

`Official ping` — `ports/dbus/pyqt-official/ping-30cfa75ad45b3447.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtDBus; required native APIs: QDBusConnection, QDBusInterface, QDBusReply. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 57a381bc8260c85d

`Official pong` — `ports/dbus/pyqt-official/pong-57a381bc8260c85d.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtDBus; required native APIs: QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 54c7440bdcdc3dfc

`Official car` — `ports/dbus/pyqt-official/car-54c7440bdcdc3dfc.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtDBus; required native APIs: QDBusAbstractAdaptor, QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 3cf5db95a691d200

`Official controller` — `ports/dbus/pyqt-official/controller-3cf5db95a691d200.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtDBus; required native APIs: QDBusAbstractInterface, QDBusConnection. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 27bf65f8b059fd96

`Official calculatorform` — `ports/designer/pyqt-official/calculatorform-27bf65f8b059fd96.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Original calculatorform.ui loaded with QUiLoader; both valueChanged(int) slots explicitly tracked; original spin ranges and sum display retained.

Native: Verify Calculator Form geometry/labels; set inputSpinBox1=7 and inputSpinBox2=8 then 0; inspect sums 15 then 8. Check spin ranges/keyboard input and both tracked signals.

### Batch 8 960c701fa6221ac5

`Official plugins` — `ports/designer/pyqt-official/plugins-960c701fa6221ac5.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt has no QtDesigner module or QPyDesignerCustomWidgetPlugin/QDesignerCustomWidgetInterface and no PyQt Designer Python plugin loader. plugins.py launches external Designer with PYQTDESIGNERPATH/PYTHONPATH; that integration cannot run in the host. Eight plain widgets have separate standalone ports; HelloGLWidget is separately blocked.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 4d24cd77c74a8801

`Official designer analogclock` — `ports/designer/pyqt-official/analogclock-4d24cd77c74a8801.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Standalone green clock, hour/minute hands and timezone offsets retained. Owned 1 s timer; native QTime notification converted to JSON text. Designer plugin/meta-properties/signals blocked separately.

Native: Verify green clock hands/ticks and live repaint at 1 s. controls[setTimeZone](-3), then resetTimeZone(); inspect offsets -3/0 and timezone/time notification values; resize and screenshot hands. Close during timer activity.

### Batch 8 9941e3c752b3a3b7

`Official bubbleswidget` — `ports/designer/pyqt-official/bubbleswidget-9941e3c752b3a3b7.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Standalone bubbles retain mouse creation/expansion, rising motion, random gradients, colour/count/author setters and start/stop. All point arithmetic uses components; QColor channels are integers and ellipse uses QRectF; two timers owned. No host-global RNG reseeding. Designer integration separately blocked.

Native: setBubbles(3); inspect three moving positions. Hold left mouse to expand, drag and release a fourth bubble; verify gradients, radii and removal above top. setBubbles(-1) gives zero; stop/start timers and setColor1/setColor2. Close while bubbleTimer and animation_timer are active.

### Batch 8 1321540b04f33117

`Official counterlabel` — `ports/designer/pyqt-official/counterlabel-1321540b04f33117.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Standalone counter preserves range/offset/int-and-string notifications and scaled text. Original initial setValue(123) remains out of range so displays 1. QPointF text overload and scalar subtraction replace unsafe overload/negation; zero metrics dimensions guarded. Designer integration separately blocked.

Native: Initial value/min/max are 1. setMaximum(200), setOffset(5), setValue(123); inspect 128 and "128" notifications while painted numeric value remains 123. stepDown, setMinimum(150), out-of-range setValue(-100), then setMaximum(10); verify clamping/range consistency and scaled text under resize.

### Batch 8 7ba49e67588b1329

`Official datetimeedit` — `ports/designer/pyqt-official/datetimeedit-7ba49e67588b1329.py`.

State: **implemented / native unexecuted**. Licence: `HPND AND GPL-3.0-only`; review `unresolved`.

Both standalone date/time editor subclasses retain popup/calendar settings and resetters. Explicit native protected mousePressEvent; calendarWidget() replaces PyQt typed findChild. Python layout/calendar references have private names. Original Denviso HPND permission retained; collection GPL scope unresolved. Designer integration separately blocked.

Native: Open both calendar popups via native mouse; exercise date and time edits. On dateEdit/dateTimeEdit drive set/reset FirstDayOfWeek, GridVisible, HorizontalHeaderFormat, VerticalHeaderFormat and NavigationBarVisible. Confirm popup values persist and calendarPopup stays true. Close with a calendar popup open.

### Batch 8 5941e31267112c98

`Official helloglwidget` — `ports/designer/pyqt-official/helloglwidget-5941e31267112c98.py`.

State: **blocked / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 de4979a99c6d0bed

`Official multipagewidget` — `ports/designer/pyqt-official/multipagewidget-de4979a99c6d0bed.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Original two pages, insertion/removal, combo selection, current-index and page-title setters retained. Private layout name avoids native layout slot shadowing. Python notifications replace unavailable PyQt signals; Designer integration blocked separately.

Native: Verify two original labels/Page 1/Page 2; select second combo item natively. setPageTitle("Second"), insertPage(0, owned QLabel), removePage(0); inspect counts/titles/current index and notifications. Confirm removed page remains owned until cleanup.

### Batch 8 773db5c24ae98ffb

`Official polygonwidget` — `ports/designer/pyqt-official/polygonwidget-773db5c24ae98ffb.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Original star/polygon path, angle/sides/radii/gradient setters retained. Repair upstream max(3, QColor) typo to copy QColor; minimum three sides and clamped angle retained. Designer integration separately blocked.

Native: Verify five-sided gradient star. setNumberOfSides(0) yields 3; setAngle(400) yields 360; setInnerRadius(12), setOuterRadius(80), setInnerColor/setOuterColor(QColor); screenshot changed path/colours and inspect sides/radii/path element count.

### Batch 8 bcfa5de0140286d5

`Official pydemo` — `ports/designer/pyqt-official/pydemo-bcfa5de0140286d5.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Original read-only HTML, author inheritance and relative text zoom retained; zoom changes exposed in inspect notifications. Designer integration separately blocked.

Native: Verify original read-only HTML and author David Boddie. setZoom(3), setZoom(-2), resetZoom(); inspect notifications and visual font sizes. setAuthor("Example Author"), resetAuthor(); verify author metadata only.

### Batch 8 5125860585e98b3a

`Official pythonconsolewidget` — `ports/designer/pyqt-official/pythonconsolewidget-5125860585e98b3a.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Original explicit Python expression evaluation, qApp access and successful-command Up/Down history retained. Evaluation starts only on Return/control, never inspect; errors now visible in inspect. No process/global event loop construction. Designer integration separately blocked.

Native: Confirm empty startup/history and no evaluation during inspect. Type 6 * 7 and press Return; inspect output 42/history. Type 1 / 0; retain input, report error, leave history unchanged. Native Up/Down recall/clear; evaluate qApp to confirm existing host application, without changing it.

### Batch 8 0ad3432ccdca7ac0

`Official localfortuneclient` — `ports/ipc/pyqt-official/localfortuneclient-0ad3432ccdca7ac0.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Original seven fortunes, Qt_4_0 UInt16/QString framing and duplicate retry retained. Create an owned QLocalServer peer; lock endpoint to a unique short temporary socket path. Fragmented payload validation and tracked retry/timeout timers; no request in inspect. Abort sockets, close server and remove temporary path on close.

Native: Verify initially listening/sent=0/received=0 and read-only owned endpoint. Click Get Fortune; await host event delivery, inspect one of seven fortunes and sent/received increment. Repeat to exercise duplicate retry; close while request/retry/timeout is pending. Retain evidence socket and temporary directory disappear.

### Batch 8 a14d08fe23965bec

`Official localfortuneserver` — `ports/ipc/pyqt-official/localfortuneserver-a14d08fe23965bec.py`.

State: **implemented / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

Original seven-fortune QLocalServer retained at an owned short unique socket path. Add an explicit owned-client test button; retain status/Quit. Reuse original Qt fortune wire framing. Accepted sockets remain owned by server, aborted before deletion; never remove another server endpoint.

Native: Verify listening status and no startup request. Click Test owned client; await native newConnection/readyRead and original seven-fortune payload; sent/received increment. Repeat, then Quit/hide/reshow; named close aborts accepted/client sockets and removes only this endpoint.

### Batch 8 74af8d8d2d7774b8

`Official audiodevices` — `ports/multimedia/pyqt-official/audiodevices-74af8d8d2d7774b8.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtMultimedia; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 c391afd8516131e1

`Official audiooutput` — `ports/multimedia/pyqt-official/audiooutput-c391afd8516131e1.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtMultimedia; required native APIs: QAudio, QAudioDeviceInfo, QAudioFormat, QAudioOutput. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 f6d352360ae9bdfb

`Official camera` — `ports/multimediawidgets/pyqt-official/camera-f6d352360ae9bdfb.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAudioEncoderSettings, QCamera, QCameraImageCapture, QCameraViewfinder, QImageEncoderSettings, QMediaMetaData, QMediaRecorder, QMultimedia, QVideoEncoderSettings. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 5eb4b9eaa2d5c9dc

`Official player` — `ports/multimediawidgets/pyqt-official/player-5eb4b9eaa2d5c9dc.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QAbstractVideoBuffer, QMediaContent, QMediaMetaData, QMediaPlayer, QMediaPlaylist, QVideoFrame, QVideoProbe, QVideoWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 a57a89e523c75b7f

`Official videographicsitem` — `ports/multimediawidgets/pyqt-official/videographicsitem-a57a89e523c75b7f.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QGraphicsVideoItem, QMediaContent, QMediaPlayer. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 481c128fba3a714b

`Official videowidget` — `ports/multimediawidgets/pyqt-official/videowidget-481c128fba3a714b.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtMultimedia / QtMultimediaWidgets; required native APIs: QMediaContent, QMediaPlayer, QVideoWidget. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 c82d1af7d1a7b0cf

`Official 2dpainting` — `ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Original native QWidget/OpenGL QOpenGLWidget 30-circle QPainter comparison and Qt text retained. Apply four-sample format only to owned GL widget; no global default-format mutation. Tracked 50 ms timer; both painter contexts always end.

Native: Verify title, Native/OpenGL labels, two 200x200 canvases, 30 animated gradient circles and Qt text. Await timer; inspect equal native_elapsed/opengl_elapsed, wrap at 1000. Retain screenshots of both real paint backends. Check host default surface format unchanged; close with timer active.

### Batch 8 303ea3ee09c4677d

`Official grabber` — `ports/opengl/pyqt-official/grabber-303ea3ee09c4677d.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 1ad60855ca28f3cc

`Official hellogl` — `ports/opengl/pyqt-official/hellogl-1ad60855ca28f3cc.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 b383fecf912548bb

`Official openglwindow` — `ports/opengl/pyqt-official/openglwindow-b383fecf912548bb.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 fcada4fff6524fcf

`Official overpainting` — `ports/opengl/pyqt-official/overpainting-fcada4fff6524fcf.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 ed6d42d4faa7e0bb

`Official textures` — `ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt.QtGui.QOpenGLContext lacks versionFunctions(); QOpenGLFunctions_1_1/QOpenGLFunctions_2_0 wrappers are not exported. The source uses versionFunctions(profile) for raw GL calls (glBegin/glGenLists/glCallList for fixed-function demos, glDrawArrays for shader demos). QOpenGLWidget exists but does not supply these missing entrypoints; no renderer rewrite or second GL binding is substituted.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 5a8e48d2a1396cea

`Official compile-on-the-fly` — `ports/pyuic/pyqt-official/compile-on-the-fly-5a8e48d2a1396cea.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Exact demo.ui loaded via QUiLoader instead of PyQt loadUiType code generation. Explicit tracked Add-items auto-slot, original Clear and OK wiring. Runtime UI behavior retained; Python code generation itself is unavailable.

Native: Click button1 twice: list contains This/is/a/demo twice, count 8. button2 clears. okButton accepts/hides asynchronously; reshow same root then named close. Confirm original demo.ui size/title/control texts and three tracked connections.

### Batch 8 b7db02f540cc7559

`Official load_ui1` — `ports/pyuic/pyqt-official/load-ui1-b7db02f540cc7559.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Exact demo.ui loaded via QUiLoader instead of PyQt loadUi. Track original Clear and OK wiring. Preserve original no-Python-slot behavior: Add items does nothing.

Native: Verify original demo.ui geometry/texts. button1 deliberately leaves list empty, matching original source without Python auto-slot. button2 clears, okButton accepts/hides; two tracked XML connections. Reshow and named close.

### Batch 8 b9660f4ee653ca01

`Official load_ui2` — `ports/pyuic/pyqt-official/load-ui2-b9660f4ee653ca01.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Exact demo.ui loaded via QUiLoader, replacing PyQt loadUi(target). Track original Add-items auto-slot, Clear and OK. Root is loader-created owned QDialog; UI behavior retained without generated PyQt classes.

Native: Click button1 twice: inspect eight items; button2 clears; okButton accepts/hides. Reshow and named close. Verify original geometry/texts and three tracked connections; no generated PyQt class or extra event loop.

### Batch 8 8847cbce50b72500

`Official adding` — `ports/qml/pyqt-official/adding-8847cbce50b72500.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 dd226ba9fbb7b330

`Official attached` — `ports/qml/pyqt-official/attached-dd226ba9fbb7b330.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 eb7a89f07f63cca7

`Official binding` — `ports/qml/pyqt-official/binding-eb7a89f07f63cca7.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, QQmlProperty, QQmlPropertyValueSource, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 ad499afe23726248

`Official coercion` — `ports/qml/pyqt-official/coercion-ad499afe23726248.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 6417cdcf1bfd1752

`Official default` — `ports/qml/pyqt-official/default-6417cdcf1bfd1752.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 81a6f0d16c203608

`Official grouped` — `ports/qml/pyqt-official/grouped-81a6f0d16c203608.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 75ca5ac77ecefd6d

`Official methods` — `ports/qml/pyqt-official/methods-75ca5ac77ecefd6d.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 d0a18273fa604bb6

`Official properties` — `ports/qml/pyqt-official/properties-d0a18273fa604bb6.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 0a13f60f5f0561db

`Official signal` — `ports/qml/pyqt-official/signal-0a13f60f5f0561db.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 738a22ef3062ed51

`Official valuesource` — `ports/qml/pyqt-official/valuesource-738a22ef3062ed51.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQml; required native APIs: QQmlComponent, QQmlEngine, QQmlListProperty, QQmlProperty, QQmlPropertyValueSource, qmlAttachedPropertiesObject, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 85a56a1f3c25ccca

`Official qtdemo` — `ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py`.

State: **blocked / native unexecuted**. Licence: `GPL-3.0-only`; review `reviewed`.

The full qtdemo launcher delegates to PyQt executables and qmlscene (menumanager.py launchExample/launchQmlExample), including QtQuick/QtQml examples. FontLab exports neither QtQuick nor QtQml and cannot load PyQt as a second Qt runtime. Qt Assistant remote control is an external dependency too. A reduced menu disabling these launch behaviors would not preserve the pinned launcher; blocked on these composite dependencies, not on QWidget.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 835281a1ab864833

`Official animation` — `ports/quick/pyqt-official/animation-835281a1ab864833.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 36246fcbffecdeba

`Official canvas` — `ports/quick/pyqt-official/canvas-36246fcbffecdeba.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 e1316fee99c63555

`Official abstractitemmodel` — `ports/quick/pyqt-official/abstractitemmodel-e1316fee99c63555.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 68d664f95f48ce52

`Official objectlistmodel` — `ports/quick/pyqt-official/objectlistmodel-68d664f95f48ce52.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 b64d66dbce7274fe

`Official stringlistmodel` — `ports/quick/pyqt-official/stringlistmodel-b64d66dbce7274fe.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 34538a4e2600b918

`Official customgeometry` — `ports/quick/pyqt-official/customgeometry-34538a4e2600b918.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickItem, QQuickView, QSGFlatColorMaterial, QSGGeometry, QSGGeometryNode, QSGNode, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 6b1f4f5590a5518a

`Official chapter1-basics` — `ports/quick/pyqt-official/chapter1-basics-6b1f4f5590a5518a.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 8d1557cbfed9c7a0

`Official chapter2-methods` — `ports/quick/pyqt-official/chapter2-methods-8d1557cbfed9c7a0.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 3cd3713a5dc9f6dc

`Official chapter3-bindings` — `ports/quick/pyqt-official/chapter3-bindings-3cd3713a5dc9f6dc.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 831ac8ea61da03f3

`Official chapter4-customPropertyTypes` — `ports/quick/pyqt-official/chapter4-custompropertytypes-831ac8ea61da03f3.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQuickItem, QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 b88e7eb0fcb53264

`Official chapter5-listproperties` — `ports/quick/pyqt-official/chapter5-listproperties-b88e7eb0fcb53264.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtQuick / QtQml; required native APIs: QQmlListProperty, QQuickItem, QQuickPaintedItem, QQuickView, qmlRegisterType. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 4dbe92cd1e720dce

`Official modelviewclient` — `ports/remoteobjects/pyqt-official/modelviewclient-4dbe92cd1e720dce.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 781a3a959215eb81

`Official modelviewserver` — `ports/remoteobjects/pyqt-official/modelviewserver-781a3a959215eb81.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost, QRemoteObjectRegistryHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 54cbd9afababdf71

`Official directconnectdynamicclient` — `ports/remoteobjects/pyqt-official/directconnectdynamicclient-54cbd9afababdf71.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 2f1e2f679775d89e

`Official directconnectdynamicserver` — `ports/remoteobjects/pyqt-official/directconnectdynamicserver-2f1e2f679775d89e.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 333f0272885ca1b7

`Official registryconnecteddynamicclient` — `ports/remoteobjects/pyqt-official/registryconnecteddynamicclient-333f0272885ca1b7.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectNode. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 b83377c9b48aec14

`Official registryconnecteddynamicserver` — `ports/remoteobjects/pyqt-official/registryconnecteddynamicserver-b83377c9b48aec14.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtRemoteObjects; required native APIs: QRemoteObjectHost, QRemoteObjectRegistryHost. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 0b0d8d2fae153e5e

`Official cachedtable` — `ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtSql; required native APIs: QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 2c4c366f259d7d80

`Official querymodel` — `ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtSql; required native APIs: QSqlQuery, QSqlQueryModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 9030a87a532b8d8f

`Official relationaltablemodel` — `ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtSql; required native APIs: QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel, QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 0677ebfd7fa2cc60

`Official tablemodel` — `ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtSql; required native APIs: QSqlTableModel. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 8d5ea81a74e30222

`Official domtraversal` — `ports/webkit/pyqt-official/domtraversal-8d5ea81a74e30222.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 f4000cf8ca288375

`Official fancybrowser` — `ports/webkit/pyqt-official/fancybrowser-f4000cf8ca288375.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 6ed36280660df7ea

`Official formextractor` — `ports/webkit/pyqt-official/formextractor-6ed36280660df7ea.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 ca47b83fbf3f31b9

`Official framecapture` — `ports/webkit/pyqt-official/framecapture-ca47b83fbf3f31b9.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 47298251b3c83ecf

`Official previewer` — `ports/webkit/pyqt-official/previewer-47298251b3c83ecf.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 ae16288fede27692

`Official simpleselector` — `ports/webkit/pyqt-official/simpleselector-ae16288fede27692.py`.

State: **blocked / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

PythonQt does not export QtWebKit / QtWebKitWidgets; required native APIs: QWebElement, QWebFrame, QWebPage, QWebView. The pinned behavior requires this module; no alternate Qt binding or replacement UI is supplied.

Native: Confirm the exact missing capabilities in the recorded blocker; launch by this ID must raise the recorded NotImplementedError before acquiring the host or creating any native object, resource, network request or external process. Registry and FontLab state remain unchanged.

### Batch 8 1e5d0f7289e1b36e

`Official schema` — `ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py`.

State: **implemented / native unexecuted**. Licence: `BSD-3-Clause AND GPL-3.0-only`; review `unresolved`.

Exact schema.ui, three XSDs and six XML instances copied. Preserve native QXmlSchema/Validator, native diagnostic callback, highlighter and error cursor/full-width selection. Defer initial validation to owned timer. Reject DTD/entities/schema locations/imports/includes before native evaluation; QByteArray plus explicit empty base QUrl prevents URL-loading overloads. No stdlib XSD substitute.

Native: Launch under 5 s with loading=true/valid=null. After owned initializeTimer, validate all six original instances across Contact/Recipe/Order: valid=true for three valid, false for three invalid, native diagnostic line/column and full-width red selection. Edit malformed XML then correct it; verify syntax colours and multi-line comments. Test DTD/external schemaLocation input: report rejection without outbound traffic. Close before initialization and after diagnostics; verify handler/highlighter/timer destruction.
