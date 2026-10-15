# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/9dab02b61cebbdb7.md
# this_file: ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py

import importlib.util
import sys
from pathlib import Path

_key = "fontlab_cleanroom_a_primitives"
if _key not in sys.modules:
    _path = (
        Path(__file__).resolve().parents[2]
        / "layouts/pyqt-official/basiclayouts-2f94fe07de765888.py"
    )
    _spec = importlib.util.spec_from_file_location(_key, _path)
    _module = importlib.util.module_from_spec(_spec)
    sys.modules[_key] = _module
    try:
        _spec.loader.exec_module(_module)
    except BaseException:
        sys.modules.pop(_key, None)
        raise
S = sys.modules[_key]

MAIL = [
    (
        f"Garden note {i + 1}",
        f"Writer {i + 1} <person{i}@example.invalid>",
        f"2026-{i % 3 + 1:02d}-{i + 1:02d}",
    )
    for i in range(10)
]


def mail_views(qt, custom=False):
    import fnmatch
    import re

    with S.Session(qt, "Mail sorting and filtering") as s:
        s.vertical()
        model = s.model(["Subject", "Sender", "Date"], MAIL)
        s.view("source", model, "QTreeView")
        pattern = s.line("pattern")
        syntax = s.combo("syntax", ["Regular expression", "Wildcard", "Fixed string"])
        column = s.combo("column", ["Subject", "Sender", "Date"])
        case = s.check("filter_case", "Case-sensitive filter")
        sort_case = s.check("sort_case", "Case-sensitive sorting")
        lower = upper = None
        if custom:
            lower = s.keep("lower", s.g.QDateEdit(s.window))
            upper = s.keep("upper", s.g.QDateEdit(s.window))
            s.add(lower)
            s.add(upper)
            lower.setDate(s.c.QDate(2026, 1, 1))
            upper.setDate(s.c.QDate(2026, 12, 31))

        def match(text):
            needle = str(S.value(pattern, "text"))
            mode = int(S.value(syntax, "currentIndex"))
            sensitive = bool(S.value(case, "checked"))
            if not sensitive:
                text = text.casefold()
                needle = needle.casefold()
            if mode == 1:
                return fnmatch.fnmatchcase(text, needle)
            if mode == 2:
                return needle in text
            try:
                return re.search(needle, text) is not None
            except re.error:
                return False

        class Custom(s.g.QSortFilterProxyModel):
            def filterAcceptsRow(self, row, parent):
                if not (
                    match(str(model.data(model.index(row, 0, parent))))
                    or match(str(model.data(model.index(row, 1, parent))))
                ):
                    return False
                date = str(model.data(model.index(row, 2, parent)))[:10]
                low = S.value(lower, "date")
                high = S.value(upper, "date")
                return (
                    not low.isValid() or date >= str(low.toString("yyyy-MM-dd"))
                ) and (not high.isValid() or date <= str(high.toString("yyyy-MM-dd")))

            def lessThan(self, left, right):
                a = str(model.data(left))
                b = str(model.data(right))
                if left.column() == 1:
                    a = a.split("<")[-1].rstrip(">")
                    b = b.split("<")[-1].rstrip(">")
                if not bool(S.value(sort_case, "checked")):
                    a = a.casefold()
                    b = b.casefold()
                return a < b

        proxy = s.keep(
            "proxy", (Custom if custom else s.g.QSortFilterProxyModel)(s.window)
        )
        proxy.setSourceModel(model)
        proxy.setDynamicSortFilter(True)
        view = s.view("proxy_view", proxy, "QTreeView")
        view.setSortingEnabled(True)

        def update(*args):
            proxy.setSortCaseSensitivity(
                s.c.Qt.CaseSensitive
                if bool(S.value(sort_case, "checked"))
                else s.c.Qt.CaseInsensitive
            )
            proxy.setFilterCaseSensitivity(
                s.c.Qt.CaseSensitive
                if bool(S.value(case, "checked"))
                else s.c.Qt.CaseInsensitive
            )
            if custom:
                proxy.invalidateFilter()
                return
            proxy.setFilterKeyColumn(int(S.value(column, "currentIndex")))
            text = str(S.value(pattern, "text"))
            mode = int(S.value(syntax, "currentIndex"))
            if mode == 0:
                proxy.setFilterRegExp(
                    s.c.QRegExp(
                        text,
                        s.c.Qt.CaseSensitive
                        if bool(S.value(case, "checked"))
                        else s.c.Qt.CaseInsensitive,
                    )
                )
            elif mode == 1:
                proxy.setFilterWildcard(text)
            else:
                proxy.setFilterFixedString(text)

        for obj, signal in [
            (pattern, "textChanged(QString)"),
            (syntax, "currentIndexChanged(int)"),
            (column, "currentIndexChanged(int)"),
            (case, "toggled(bool)"),
            (sort_case, "toggled(bool)"),
        ]:
            s.link(obj, signal, update)
        if custom:
            for obj in [lower, upper]:
                s.link(obj, "dateChanged(QDate)", update)
        s.h.release.append(
            lambda: proxy.setSourceModel(None) if not s.h.owner.closed else None
        )
        update()
        return s.h


def build(qt):
    return mail_views(qt)
