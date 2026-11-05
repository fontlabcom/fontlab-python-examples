---
this_file: lessons/WORK.md
---

## 2026-11-05 — separate released and expanded lesson scope

Inspected lessons/pyproject.toml and the current README. The package declares
App >=0.2.26.dev0 and Fly >=0.2.1; its candidate tests live under
candidate_tests/models_candidate. Historical v1.0.3 acceptance covers the original
three model/form workflows. All thirteen packaged GetGo runtime rows still need
native acceptance; no new tests or native actions were run here.

From the Examples repository root, set S230_PY to a prepared isolated arm64
Python 3.11 environment with genuine installed matching App, Fly, Qt test providers,
fontTools, pytest and pytest-cov. Then run:

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 QT_QPA_PLATFORM=offscreen \
  "$S230_PY" -B -m pytest -p pytest_cov \
  --confcutdir lessons/candidate_tests/models_candidate -q -p no:cacheprovider \
  lessons/candidate_tests/models_candidate \
  --cov=lessons/src/fontlab_python_lessons --cov-branch --cov-fail-under=80
```

This inspected recipe is unexecuted in this documentation pass. Root runtime and
documentation suites have separate prerequisites and denominators; this lesson
coverage command does not replace them. Do not use pretend version metadata.

# Lesson package integration

The three lessons use real font names and metrics. Their distinct
fontlab_python_lessons namespace preserves the historical catalogue API.
The eight runtime modules, three menus and UI resource preserve the previously
reviewed and natively verified candidate; relocation changes path headers only.
No old tracked file changes. The build metadata and package live under lessons/
to coexist with the owner's new root documentation project. Root Scripts keeps
the same three shallow entries; tests compare their packaged executable bodies.

The new package uses its own full Apache license in provenance. A standalone
build without the archived root LICENSE succeeded but omitted the license;
the artifact audit correctly rejected it. The corrected standalone wheel
contains the complete license bytes and passes the scoped private-path audit.
Build success alone is insufficient evidence.

Fresh baseline: 1,886 legacy tests pass. Three actual-menu tests fail before
the menu files are added, then pass. All 40 lesson tests pass. The project
quality gate runs both full suites in separate processes under one appended
coverage data set: all 14 changed production modules exceed 80% statement,
branch and aggregate coverage; total 97.85%. Both sets of menus have 100%.
All legacy runtime/tests remain unchanged. The canonical owner's archive moves
and deletions remain untouched.

Commands use explicit EXAMPLES_APP_SOURCE pointing at the reviewed App package.
Run from the workspace:

```sh
sh .metaswarm/quality.sh coverage .worktrees/issue111-lessons-final fontlab-python-examples
```

From this checkout's lessons/ directory:

```sh
QT_QPA_PLATFORM=offscreen PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 uv run --no-project --python cpython-3.11-macos-aarch64-none --with PySide6 --with pytest python -m pytest -q --confcutdir candidate_tests/models_candidate candidate_tests/models_candidate
uv build --no-sources
```

The standalone source copy also passes all 40 tests with an explicit retained
legacy checkout. Exact commands and durable artifact/native receipts are kept
in the workspace work log. Normal dependency installation, final installed
native checks now pass: normal installation resolves 23 compatible packages,
four namespace orders coexist, and actual installed menus pass all three
workflows plus twelve edge controls on FontLab 9.0.9784. Complete font/history,
Close and import-state preservation pass. Canonical integration and release
verification now pass at v1.0.3/8a35cb8aab447d662bcd9be8bb62733f255edc01.
Canonical integration preserves all 1,231 owner
status entries and every existing dirty-file hash/symlink exactly. Source
documentation lives in lessons/ to avoid the owner's generated docs/ output.
The package project also preserves the owner's root documentation metadata.
No broader archive completion is claimed.

Independent downloaded wheel/sdist/ZIP hashes match. Fresh tag40lesson and1886
legacy tests pass; downloaded native3workflows+12edges preserve complete font
and history, Close and import state. All six screenshots match the inspected
candidate byte-for-byte. The normal clean install contains23compatible packages.
Source input mappings are accepted without removing the four retained originals.
