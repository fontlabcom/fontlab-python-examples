# this_file: ports/database/eyllanesc/main-5b93264cdefad0d7.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/sql/drilldown/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt does not export QtSql; required native APIs: QSqlDatabase, QSqlQuery, QSqlRelation, QSqlRelationalDelegate, QSqlRelationalTableModel. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied. A sqlite3 substitution would replace QtSql model/delegate semantics and is not performed."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("5b93264cdefad0d7")
