# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a59dae9770bfbefb.md
# this_file: ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py

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

from xml.dom import minidom
from xml.parsers.expat import ExpatError

XML = '<?xml version="1.0"?><?sample review?><shelf topic="craft"><!--A quiet corner--><book>Paper shapes</book></shelf>'


def build(qt):
    with S.Session(qt, "XML node browser") as s:
        s.vertical()
        c = s.c
        document = [minidom.parseString(XML)]
        nodes = {0: document[0]}
        identities = {id(document[0]): 0}
        parents = {0: None}
        next_id = [1]

        def identify(node, parent):
            key = id(node)
            if key not in identities:
                identity = next_id[0]
                next_id[0] += 1
                identities[key] = identity
                nodes[identity] = node
                parents[identity] = parent
            return identities[key]

        class Dom(c.QAbstractItemModel):
            def columnCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 3

            def rowCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                if parent.isValid() and parent.column() != 0:
                    return 0
                node = nodes.get(int(parent.internalId()) if parent.isValid() else 0)
                return len(node.childNodes) if node else 0

            def index(self, row, col, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                pid = int(parent.internalId()) if parent.isValid() else 0
                node = nodes.get(pid)
                if (
                    node is None
                    or not 0 <= col < 3
                    or not 0 <= row < len(node.childNodes)
                    or (parent.isValid() and parent.column() != 0)
                ):
                    return c.QModelIndex()
                return self.createIndex(row, col, identify(node.childNodes[row], pid))

            def parent(self, index):
                if not index.isValid():
                    return c.QModelIndex()
                identity = int(index.internalId())
                pid = parents.get(identity)
                if not pid:
                    return c.QModelIndex()
                parent = nodes[pid]
                grand = nodes[parents[pid]]
                return self.createIndex(list(grand.childNodes).index(parent), 0, pid)

            def data(self, index, role=c.Qt.DisplayRole):
                if not index.isValid() or role != c.Qt.DisplayRole:
                    return None
                node = nodes.get(int(index.internalId()))
                if node is None:
                    return None
                if index.column() == 0:
                    return node.nodeName
                if index.column() == 1:
                    return (
                        " ".join(
                            f'{node.attributes.item(i).name}="{node.attributes.item(i).value}"'
                            for i in range(node.attributes.length)
                        )
                        if node.attributes
                        else ""
                    )
                return node.nodeValue or ""

            def headerData(self, section, orientation, role=c.Qt.DisplayRole):
                return (
                    ["Node", "Attributes", "Value"][section]
                    if role == c.Qt.DisplayRole
                    and orientation == c.Qt.Horizontal
                    and 0 <= section < 3
                    else None
                )

        model = s.keep("model", Dom(s.window))
        s.h.model = model
        s.view("tree", model, "QTreeView")

        def load(path):
            try:
                raw = Path(path).read_bytes()
                if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
                    raise ValueError("External document declarations are not supported")
                replacement = minidom.parseString(raw)
            except (ExpatError, OSError, ValueError) as error:
                s.state["error"] = str(error)
                return False
            model.beginResetModel()
            document[0].unlink()
            document[0] = replacement
            nodes.clear()
            nodes[0] = replacement
            identities.clear()
            identities[id(replacement)] = 0
            parents.clear()
            parents[0] = None
            next_id[0] = 1
            model.endResetModel()
            s.state["error"] = ""
            return True

        s.menu("File", [("Open", lambda: s.choose(load)), ("Exit", s.h.close)])
        s.keep("load", load)
        s.h.after_close.append(lambda: document[0].unlink())
        return s.h
