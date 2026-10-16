# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/4b8851287931abd0.md
# this_file: ports/itemviews/pyqt-official/dirview-4b8851287931abd0.py

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
    with S.Session(qt, "Deferred sample directory") as s:
        s.vertical()
        s.state.update(loading=True, root=None)
        # Do not attach QFileSystemModel until the owned directory exists.
        tree = s.keep("tree", s.g.QTreeView(s.window))
        s.add(tree)

        def initialize():
            root = s.temp()
            (root / "notes.txt").write_text("One small directory fixture.\n")
            model = s.keep("model", s.g.QFileSystemModel(s.window))
            model.setReadOnly(True)
            index = model.setRootPath(str(root))
            tree.setModel(model)
            tree.setRootIndex(index)
            tree.setSortingEnabled(True)
            s.h.model = model
            s.state.update(loading=False, root=str(root))

        s.h.release.append(
            lambda: tree.setModel(None) if not s.h.owner.closed else None
        )
        s.timer("load_timer", 0, initialize, single=True)
        s.keep("initialize", initialize)
        return s.h
