---
this_file: docs/second-numbered-batch.md
---

# Second numbered batch: controller native checks

All ten new modules use catalog-planned entrypoint paths and injected
`qt.QtCore`/`qt.QtGui`. No QtWidgets, PyQt, PySide, new QApplication or application
exec loop. Source headers, IDs and original hashes are in catalog/ports.json.
New acceptance states are `unexecuted`; no first-batch receipts changed.

| Example | Implementation | Controller checks / translation |
| --- | --- | --- |
| 02 Widgets | Ported; BSD review unresolved | All groups/tabs/text, 10×10 table, values 50/40/60/30, password, tri-state, disable toggle, timer progression, style selector; Qt5 unscoped enums, PythonQt value/count/palette properties, explicit activated(QString). Styles/palette stay inside gallery. |
| 06 QML | Blocked | QtQml/QQmlApplicationEngine and QtQuick not exposed in PythonQt. No resource copies. |
| 07 Text Editor | Ported | Open/Save/Save As, UTF-8 roundtrip, shortcuts, About icon, asynchronous Save/Discard/Cancel close prompt (including cancelled Save As), named cleanup with unsaved text. QAction in QtGui; filename strings instead of PyQt tuples. No host application-name mutation. |
| 08 exe | Blocked | fbs PyQt6 ApplicationContext creates standalone QApplication and requires freezer runtime, incompatible with embedded PythonQt ownership. |
| 09 Dark theme | Ported | Same editor actions; Fusion style and exact original palette colors only on owned subtree; FontLab style/palette unchanged. Qt5 QPalette/Qt enums unscoped. |
| 10 Painter | Ported with audio gap | Mouse callback, centered bullet PNG, repaint after multiple clicks, persistent hole positions, painter.end(), editor actions and About icon. QSoundEffect absent from permitted QtCore/QtGui: no shot playback; exact shot.wav retained. Confirm sound_supported=False. |
| 12 Tree view | Ported | QDirModel retained/parented to QTreeView, home-root path, filesystem navigation, root row/column counts and owned deletion. |
| 13 List view | Ported | QStringListModel retained/parented; exactly three original strings, row count, native selection/editing and live inspection. |
| 14 Table model | Ported | Native Python QAbstractTableModel callbacks render all scientist cells and headers; Qt5 DisplayRole/Horizontal, None for invalid variants, zero rows/columns for child parents. Model retained and parented. |
| 15 Database + initializer | Blocked | QtSql/QSqlDatabase/QSqlTableModel not exposed; initializer alone cannot provide view. No database created. |

Resources live beside their executable (resource category paths in the static
inventory remain unchanged). Five new copies: 07 icon.svg; 09 icon.svg; 10
bullet.png, icon.svg, shot.wav. Their manifest IDs and SHA-256 values come from
catalog/sources.json; copied bytes are unchanged.

Launch names and source IDs are listed in README and the manifest. blocked
records appear in available(); launch rejects them before host import with the
concrete reason. Named cleanup joins workers and suppresses editor close prompts;
user close retains Save/Discard/Cancel interaction. 

Official references consulted: [Qt5 model subclassing](https://doc.qt.io/qt-5/qabstracttablemodel.html),
[QTimer thread affinity](https://doc.qt.io/qt-5/qtimer.html),
[QWidget style scope](https://doc.qt.io/qt-5/qwidget.html#setStyle),
[PythonQt](https://mevislab.github.io/pythonqt/), and
[Python 3.11 urllib](https://docs.python.org/3.11/library/urllib.request.html).
Boundary doubles and compilation do not prove FontLab native acceptance.
