# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/321f8e535facafde.md
# this_file: ports/itemviews/pyqt-official/simpletreemodel-321f8e535facafde.py

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

OUTLINE = "Reading\tTopics for an afternoon\n  Letters\tShapes and spacing\n    Curves\tSmooth joins\n  Numbers\tCounts and measures\nMaking\tSmall practical projects\n  Paper\tFolds and cuts"


def parse_outline(text):
    nodes = {0: {"parent": None, "cells": ["Title", "Summary"], "children": []}}
    stack = [(-1, 0)]
    for raw in text.splitlines():
        if not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        cells = raw.strip().split("\t")
        cells = (cells + [""])[:2]
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        identity = len(nodes)
        nodes[identity] = {"parent": parent, "cells": cells, "children": []}
        nodes[parent]["children"].append(identity)
        stack.append((indent, identity))
    return nodes


def tree_model(qt, parent, text=OUTLINE, editable=False):
    nodes = parse_outline(text)
    headers = ["Title", "Description" if editable else "Summary"]
    next_id = [len(nodes)]
    c = qt.QtCore

    class Outline(c.QAbstractItemModel):
        def columnCount(self, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            return len(headers)

        def rowCount(self, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            if parent.isValid() and parent.column() != 0:
                return 0
            node = int(parent.internalId()) if parent.isValid() else 0
            return len(nodes.get(node, {}).get("children", []))

        def index(self, row, col, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            node = int(parent.internalId()) if parent.isValid() else 0
            children = nodes.get(node, {}).get("children", [])
            if (
                row < 0
                or col < 0
                or col >= len(headers)
                or row >= len(children)
                or (parent.isValid() and parent.column() != 0)
            ):
                return c.QModelIndex()
            return self.createIndex(row, col, children[row])

        def parent(self, index):
            if not index.isValid():
                return c.QModelIndex()
            node = nodes.get(int(index.internalId()))
            pid = node["parent"] if node else 0
            if not pid:
                return c.QModelIndex()
            grand = nodes[pid]["parent"]
            return self.createIndex(nodes[grand]["children"].index(pid), 0, pid)

        def data(self, index, role=c.Qt.DisplayRole):
            if not index.isValid() or role not in [c.Qt.DisplayRole, c.Qt.EditRole]:
                return None
            cells = nodes.get(int(index.internalId()), {}).get("cells", [])
            return cells[index.column()] if 0 <= index.column() < len(cells) else None

        def headerData(self, section, orientation, role=c.Qt.DisplayRole):
            if (
                role == c.Qt.DisplayRole
                and orientation == c.Qt.Horizontal
                and 0 <= section < len(headers)
            ):
                return headers[section]
            return None

        def flags(self, index):
            if not index.isValid():
                return c.Qt.NoItemFlags
            return (
                c.Qt.ItemIsEnabled
                | c.Qt.ItemIsSelectable
                | (c.Qt.ItemIsEditable if editable else 0)
            )

        def setData(self, index, new, role=c.Qt.EditRole):
            if (
                not editable
                or role != c.Qt.EditRole
                or not index.isValid()
                or int(index.internalId()) not in nodes
            ):
                return False
            nodes[int(index.internalId())]["cells"][index.column()] = str(new)
            self.dataChanged(index, index, [])
            return True

        def setHeaderData(self, section, orientation, new, role=c.Qt.EditRole):
            if (
                not editable
                or orientation != c.Qt.Horizontal
                or not 0 <= section < len(headers)
            ):
                return False
            headers[section] = str(new)
            self.headerDataChanged(orientation, section, section)
            return True

        def insertRows(self, row, count, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            pid = int(parent.internalId()) if parent.isValid() else 0
            if (
                not editable
                or pid not in nodes
                or count < 1
                or not 0 <= row <= len(nodes[pid]["children"])
            ):
                return False
            self.beginInsertRows(parent, row, row + count - 1)
            for i in range(count):
                identity = next_id[0]
                next_id[0] += 1
                nodes[identity] = {
                    "parent": pid,
                    "cells": ["New entry"] + [""] * (len(headers) - 1),
                    "children": [],
                }
                nodes[pid]["children"].insert(row + i, identity)
            self.endInsertRows()
            return True

        def removeRows(self, row, count, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            pid = int(parent.internalId()) if parent.isValid() else 0
            if (
                not editable
                or pid not in nodes
                or count < 1
                or row < 0
                or row + count > len(nodes[pid]["children"])
            ):
                return False
            self.beginRemoveRows(parent, row, row + count - 1)
            pending = nodes[pid]["children"][row : row + count]
            del nodes[pid]["children"][row : row + count]
            while pending:
                node = nodes.pop(pending.pop())
                pending.extend(node["children"])
            self.endRemoveRows()
            return True

        def insertColumns(self, col, count, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            if not editable or count < 1 or not 0 <= col <= len(headers):
                return False
            self.beginInsertColumns(c.QModelIndex(), col, col + count - 1)
            headers[col:col] = ["Column"] * count
            for node in nodes.values():
                node["cells"][col:col] = [""] * count
            self.endInsertColumns()
            return True

        def removeColumns(self, col, count, parent=None):
            if parent is None:
                parent = c.QModelIndex()
            if not editable or count < 1 or col < 0 or col + count > len(headers):
                return False
            self.beginRemoveColumns(c.QModelIndex(), col, col + count - 1)
            del headers[col : col + count]
            for node in nodes.values():
                del node["cells"][col : col + count]
            self.endRemoveColumns()
            return True

    model = Outline(parent)
    return model, nodes


def outline(qt, editable=False):
    with S.Session(qt, "Editable outline" if editable else "Read-only outline") as s:
        s.vertical()
        model, nodes = tree_model(qt, s.window, editable=editable)
        s.keep("model", model)
        s.h.model = model
        view = s.view("tree", model, "QTreeView")
        status = s.keep("status", s.label("Select an entry"))

        def current():
            return view.currentIndex()

        def change(kind):
            index = current()
            parent = model.parent(index) if index.isValid() else s.c.QModelIndex()
            row = index.row() if index.isValid() else model.rowCount()
            if kind == "sibling":
                model.insertRows(row, 1, parent)
            elif kind == "child":
                model.insertRows(model.rowCount(index), 1, index)
            elif kind == "remove" and index.isValid():
                model.removeRows(index.row(), 1, parent)
            elif kind == "column":
                model.insertColumns(model.columnCount(), 1)
            elif kind == "remove_column" and model.columnCount() > 1:
                model.removeColumns(model.columnCount() - 1, 1)

        if editable:
            s.menu(
                "Actions",
                [
                    (label, lambda k=key: change(k))
                    for label, key in [
                        ("Add row", "sibling"),
                        ("Add child", "child"),
                        ("Remove row", "remove"),
                        ("Add column", "column"),
                        ("Remove column", "remove_column"),
                    ]
                ],
            )
        s.menu("File", [("Exit", s.h.close)])
        selection = view.selectionModel()
        s.link(
            selection,
            "currentChanged(QModelIndex,QModelIndex)",
            lambda index, old: status.setText(
                f"Row {index.row() + 1}, column {index.column() + 1}"
                if index.isValid()
                else "No selection"
            ),
        )
        s.keep("nodes", nodes)
        return s.h


def build(qt):
    return outline(qt)
