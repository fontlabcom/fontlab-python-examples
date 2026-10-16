# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/090c76a87351e771.md
# this_file: ports/itemviews/pyqt-official/interview-090c76a87351e771.py

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


def build(qt):
    with S.Session(qt, "Synchronized lazy views") as s:
        s.vertical()
        c = s.c
        nodes = {0: (None, None)}
        lookup = {}
        next_id = [1]

        class Lazy(c.QAbstractItemModel):
            def columnCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 10

            def rowCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() and parent.column() != 0 else 1000

            def index(self, row, col, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                if (
                    not 0 <= row < 1000
                    or not 0 <= col < 10
                    or (parent.isValid() and parent.column() != 0)
                ):
                    return c.QModelIndex()
                pid = int(parent.internalId()) if parent.isValid() else 0
                if pid not in nodes:
                    return c.QModelIndex()
                key = (pid, row)
                if key not in lookup:
                    identity = next_id[0]
                    next_id[0] += 1
                    lookup[key] = identity
                    nodes[identity] = (pid, row)
                return self.createIndex(row, col, lookup[key])

            def parent(self, index):
                if not index.isValid() or int(index.internalId()) not in nodes:
                    return c.QModelIndex()
                pid, _row = nodes[int(index.internalId())]
                if pid == 0:
                    return c.QModelIndex()
                return self.createIndex(nodes[pid][1], 0, pid)

            def data(self, index, role=c.Qt.DisplayRole):
                if index.isValid() and role == c.Qt.DisplayRole:
                    return f"Entry {index.row() + 1}, field {index.column() + 1}"
                if (
                    index.isValid()
                    and role == c.Qt.DecorationRole
                    and index.column() == 0
                ):
                    return icon
                return None

        icon = s.g.QIcon(S.pictogram(s))
        model = s.keep("model", Lazy(s.window))
        s.h.model = model
        selection = s.keep("selection", s.g.QItemSelectionModel(model, s.window))
        for key, kind in [
            ("tree", "QTreeView"),
            ("table", "QTableView"),
            ("list", "QListView"),
        ]:
            view = s.view(key, model, kind)
            view.setSelectionModel(selection)
            if key == "tree":
                view.header().setSectionsMovable(True)
            if key == "table":
                view.horizontalHeader().setSectionsMovable(True)
        s.keep("nodes", nodes)
        return s.h
