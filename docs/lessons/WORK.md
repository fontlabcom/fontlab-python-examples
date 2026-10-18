---
this_file: docs/lessons/WORK.md
---

# Lesson package integration

The three lessons use real font names and metrics. Their distinct
fontlab_python_lessons namespace preserves the historical catalogue API.
The eight runtime modules, three menus and UI resource match the previously
reviewed and natively verified candidate. No old tracked file changes.

The new package uses its own full Apache license in provenance. A standalone
build without the archived root LICENSE succeeded but omitted the license;
the artifact audit correctly rejected it. The corrected standalone wheel
contains the complete license bytes and passes the scoped private-path audit.
Build success alone is insufficient evidence.

Fresh baseline: 1,886 legacy tests pass. Three actual-menu tests fail before
the menu files are added, then pass. All 40 lesson tests pass. The project
quality gate runs both full suites in separate processes under one appended
coverage data set: all 11 changed production modules exceed 80% statement,
branch and aggregate coverage; total 97.77%. The three menus each have 100%.
All legacy runtime/tests remain unchanged. The canonical owner's archive moves
and deletions remain untouched.

Commands use explicit EXAMPLES_APP_SOURCE pointing at the reviewed App package.
Run from the workspace:

```sh
sh .metaswarm/quality.sh coverage .worktrees/issue111-lessons-package fontlab-python-examples
```

From this checkout:

```sh
QT_QPA_PLATFORM=offscreen PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python cpython-3.11-macos-aarch64-none --with PySide6 --with pytest python -m pytest -q --confcutdir candidate_tests/models_candidate candidate_tests/models_candidate
uv build --no-sources
```

The standalone source copy also passes all 40 tests with an explicit retained
legacy checkout. Exact commands and durable artifact/native receipts are kept
in the workspace work log. Normal dependency installation, final installed
native checks, canonical integration and release verification are still pending
for this integration layout. No broader catalogue/archive completion is claimed.
