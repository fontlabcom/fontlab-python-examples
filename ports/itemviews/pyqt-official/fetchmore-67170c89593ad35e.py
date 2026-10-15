# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/67170c89593ad35e.md
# this_file: ports/itemviews/pyqt-official/fetchmore-67170c89593ad35e.py

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

import os


def build(qt):
    with S.Session(qt, "Incremental directory listing") as s:
        s.vertical()
        directory = s.line("directory")
        log = s.keep("log", s.g.QPlainTextEdit(s.window))
        log.setReadOnly(True)
        files = []
        shown = [0]
        made = [0]
        c = s.c

        class Listing(c.QAbstractListModel):
            def rowCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() else shown[0]

            def data(self, index, role=c.Qt.DisplayRole):
                if not index.isValid() or not 0 <= index.row() < shown[0]:
                    return None
                if role == c.Qt.DisplayRole:
                    return files[index.row()]
                if role == c.Qt.BackgroundRole:
                    return s.g.QBrush(
                        s.g.QColor(
                            "#f0f4fa" if (index.row() // 100) % 2 == 0 else "#ffffff"
                        )
                    )
                return None

            def canFetchMore(self, parent):
                return not parent.isValid() and shown[0] < len(files)

            def fetchMore(self, parent):
                if parent.isValid() or shown[0] >= len(files):
                    return
                first = shown[0]
                count = min(100, len(files) - first)
                self.beginInsertRows(c.QModelIndex(), first, first + count - 1)
                shown[0] += count
                self.endInsertRows()
                log.appendPlainText(f"Exposed {first} through {shown[0] - 1}")
                s.state["shown"] = shown[0]

        model = s.keep("model", Listing(s.window))
        s.h.model = model
        s.view("list", model, "QListView")
        s.add(log)
        s.state.update(loading=True, shown=0)

        def enumerate_path(*args):
            try:
                with os.scandir(str(S.value(directory, "text"))) as entries:
                    values = sorted(entry.name for entry in entries)
            except OSError as error:
                s.state["error"] = str(error)
                return
            model.beginResetModel()
            files[:] = values
            shown[0] = 0
            model.endResetModel()
            s.state.update(loading=False, shown=0, total=len(files))
            model.fetchMore(c.QModelIndex())

        def prepare():
            root = s.temp()
            for i in range(made[0], min(205, made[0] + 20)):
                (root / f"entry-{i:03d}.txt").write_text(f"Sample entry {i}\n")
            made[0] = min(205, made[0] + 20)
            if made[0] == 205:
                timer.stop()
                directory.setText(str(root))
                enumerate_path()

        timer = s.timer("prepare_timer", 0, prepare)
        s.link(directory, "returnPressed()", enumerate_path)
        s.keep("prepare", prepare)
        s.keep("enumerate", enumerate_path)
        return s.h
