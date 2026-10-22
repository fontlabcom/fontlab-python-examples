# Examples: database

!!! note "Retained catalogue"

    This page comes from the retained catalogue. Its launch instructions and native
    results describe the earlier tree, archived externally with historical prefix `rescued/part2`, rather than the current
    launcher. The documentation build does not rerun these examples.

11 records: 2 implemented, 9 blocked.

| Example | Implementation | Native | Licence |
| --- | --- | --- | --- |
| [Official cachedtable](#official-cachedtable) | blocked | not run | Apache-2.0 |
| [Official charactermap](#official-charactermap) | implemented | passed | Apache-2.0 |
| [Official querymodel](#official-querymodel) | blocked | not run | Apache-2.0 |
| [Official relationaltablemodel](#official-relationaltablemodel) | blocked | not run | Apache-2.0 |
| [Official tablemodel](#official-tablemodel) | blocked | not run | Apache-2.0 |
| [Official textedit](#official-textedit) | implemented | passed | Apache-2.0 |
| [PyQt database](#pyqt-database) | blocked | not run | MIT |
| [PyQt database initializer](#pyqt-database-initializer) | blocked | not run | MIT |
| [QtExamples sql/cachedtable/main](#qtexamples-sqlcachedtablemain) | blocked | not run | GPL-3.0-only |
| [QtExamples sql/drilldown/main](#qtexamples-sqldrilldownmain) | blocked | not run | GPL-3.0-only |
| [QtExamples sql/sqlwidgetmapper/main](#qtexamples-sqlsqlwidgetmappermain) | blocked | not run | GPL-3.0-only |

### Official cachedtable

- Source: [pyqt/examples / src/pyqt-official/sql/cachedtable.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/sql/cachedtable.py)
- Port: [`ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/sql/pyqt-official/cachedtable-0b0d8d2fae153e5e.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtSql model and delegate bindings are unavailable in FontLab.

### Official charactermap

- Source: [pyqt/examples / src/pyqt-official/widgets/charactermap.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/widgets/charactermap.py)
- Port: [`ports/widgets/pyqt-official/charactermap-499e965d86347920.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/widgets/pyqt-official/charactermap-499e965d86347920.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("499e965d86347920")  # inside FontLab
examples.close("499e965d86347920")
```

### Official querymodel

- Source: [pyqt/examples / src/pyqt-official/sql/querymodel.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/sql/querymodel.py)
- Port: [`ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/sql/pyqt-official/querymodel-2c4c366f259d7d80.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtSql model and delegate bindings are unavailable in FontLab.

### Official relationaltablemodel

- Source: [pyqt/examples / src/pyqt-official/sql/relationaltablemodel.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/sql/relationaltablemodel.py)
- Port: [`ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtSql model and delegate bindings are unavailable in FontLab.

### Official tablemodel

- Source: [pyqt/examples / src/pyqt-official/sql/tablemodel.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/sql/tablemodel.py)
- Port: [`ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: Apache-2.0
- Blocked: QtSql model and delegate bindings are unavailable in FontLab.

### Official textedit

- Source: [pyqt/examples / src/pyqt-official/richtext/textedit/textedit.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/pyqt-official/richtext/textedit/textedit.py)
- Port: [`ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py)
- Implementation: **implemented**
- Native acceptance: passed (commit `f358589`; workspace evidence `examples-cleanroom/review/run02.jsonl`)
- Licence: Apache-2.0

```python
import fontlab_python_examples as examples

handle = examples.launch("b34b2f696a977e74")  # inside FontLab
examples.close("b34b2f696a977e74")
```

### PyQt database

- Source: [pyqt/examples / src/15 PyQt database example/main.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/15%20PyQt%20database%20example/main.py)
- Port: [`ports/database/pyqt-examples/main-5ab035c6e1d41d02.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/database/pyqt-examples/main-5ab035c6e1d41d02.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: MIT
- Blocked: PythonQt does not expose QtSql/QSqlDatabase/QSqlTableModel; the initializer alone cannot supply the database view.

### PyQt database initializer

- Source: [pyqt/examples / src/15 PyQt database example/initdb.py](https://github.com/pyqt/examples/blob/83eed0514582c8deb60d9e9e6bff31ceffe4eaeb/src/15%20PyQt%20database%20example/initdb.py)
- Port: [`ports/database/pyqt-examples/initdb-dc807e132a004218.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/database/pyqt-examples/initdb-dc807e132a004218.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: MIT
- Blocked: PythonQt does not expose QtSql/QSqlDatabase/QSqlTableModel; the initializer alone cannot supply the database view.

### QtExamples sql/cachedtable/main

- Source: [eyllanesc/QtExamples / official/sql/cachedtable/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/sql/cachedtable/main.py)
- Port: [`ports/database/eyllanesc/main-a3c7c0e56d0452cf.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/database/eyllanesc/main-a3c7c0e56d0452cf.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.

### QtExamples sql/drilldown/main

- Source: [eyllanesc/QtExamples / official/sql/drilldown/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/sql/drilldown/main.py)
- Port: [`ports/database/eyllanesc/main-5b93264cdefad0d7.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/database/eyllanesc/main-5b93264cdefad0d7.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.

### QtExamples sql/sqlwidgetmapper/main

- Source: [eyllanesc/QtExamples / official/sql/sqlwidgetmapper/main.py](https://github.com/eyllanesc/QtExamples/blob/a01fd7d10d45801b10876f94c07aaefb11bc2e12/official/sql/sqlwidgetmapper/main.py)
- Port: [`ports/database/eyllanesc/main-fd7c0bbed85eb2d4.py`](https://github.com/fontlabcom/fontlab-python-examples/blob/main/ports/database/eyllanesc/main-fd7c0bbed85eb2d4.py)
- Implementation: **blocked**
- Native acceptance: not run (blocked)
- Licence: GPL-3.0-only
- Blocked: PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel, QSqlTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed.
