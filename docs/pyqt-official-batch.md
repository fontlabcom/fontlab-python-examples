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
