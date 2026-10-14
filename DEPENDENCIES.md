---
this_file: DEPENDENCIES.md
---

# Dependencies

The inventory CLI uses Python 3.12's standard library: `ast` for source structure,
`tokenize` for Python encoding detection, `xml.etree.ElementTree` for UI/qrc
structure, `hashlib` for exact original hashes, and `argparse`/`json`/`pathlib`
for explicit local inputs and portable output. It has no Qt runtime dependencies.
Official [AST](https://docs.python.org/3/library/ast.html),
[tokenize](https://docs.python.org/3/library/tokenize.html) and
[ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html)
documentation were checked before implementation.

`pytest` supplies owned-fixture tests and committed-catalog acceptance checks;
`pytest-cov` is optional coverage tooling. Ruff provides scoped lint and formatting.
Use `uv run --no-project --with pytest` and `uvx ruff` to run them without adding
dependencies to FontLab's embedded interpreter. Upstream dependency imports and
requirements declarations are inventory evidence, not packages installed here.

The first four ports require FontLab's own PythonQt and existing QApplication.
`fontlab-fontlabapp` supplies `fontlabapp.widgets.OwnedWidget`; the launcher
imports that dependency only for launch, so catalog/help work outside the host.
No PyQt/PySide, Qt.py or second Qt runtime is required. Standard-library importlib
loads the four catalog-mapped port paths; pathlib resolves the exact UI resource.
`fontlab-remopy` is optional on the external controller only, used by
`examples/remopy.py` to execute ordinary Python in an already configured FontLab.

Consumer calls were checked against the current local `fontlabapp/widgets.py`
and Remopy `control.py`/`execution.py`, and official
[PythonQt documentation](https://mevislab.github.io/pythonqt/),
[QUiLoader](https://doc.qt.io/qt-6/quiloader.html),
[QDialog open/modality](https://doc.qt.io/qt-6/qdialog.html) and
[QApplication](https://doc.qt.io/qt-6/qapplication.html) documentation.
Native prerequisite receipts confirm FontLab's actual clicked callback and
original Designer load/connections. Port interaction acceptance remains separate.


Second-batch chat ports use Python 3.11 standard-library urllib.request/parse,
queue and threading in place of requests and the PyQt-only threadutil helper.
Workers carry Python data only; GUI-owned QTimer handles delivery. No additional
FontLab dependency is installed. All implemented ports retain PythonQt and
fontlab-fontlabapp ownership requirements. QSoundEffect, QtQml, QtQuick, QtSql
and the standalone fbs/PyQt6 freezer are recorded host capability gaps.
