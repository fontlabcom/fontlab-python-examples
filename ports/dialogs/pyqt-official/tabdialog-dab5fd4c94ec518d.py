# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/dab5fd4c94ec518d.md
# this_file: ports/dialogs/pyqt-official/tabdialog-dab5fd4c94ec518d.py

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
from datetime import datetime


def build(qt):
    with S.Session(qt, "Sample file information", qt.QtGui.QDialog()) as s:
        s.vertical()
        path = s.temp() / "sample.txt"
        path.write_text("An independently written file for this example.\n")
        info = path.stat()
        s.state.update(size=info.st_size, mode=info.st_mode, fixture=str(path))
        tabs = s.keep("tabs", s.g.QTabWidget(s.window))
        s.add(tabs)
        for title in ["General", "Permissions", "Applications"]:
            page = s.g.QWidget(tabs)
            layout = s.vertical(page)
            tabs.addTab(page, title)
            if title == "General":
                s.line("filename", path.name, layout)
                for text in [
                    str(path.parent),
                    f"{info.st_size} bytes",
                    "Modified " + datetime.fromtimestamp(info.st_mtime).isoformat(),
                    "Created " + datetime.fromtimestamp(info.st_ctime).isoformat(),
                ]:
                    s.label(text, layout)
            elif title == "Permissions":
                for key, flag in [
                    ("read", os.R_OK),
                    ("write", os.W_OK),
                    ("execute", os.X_OK),
                ]:
                    s.check(key, key.title(), os.access(path, flag), layout)
                s.label(f"Owner {info.st_uid}; group {info.st_gid}", layout)
            else:
                apps = s.g.QListWidget(page)
                apps.addItems(["Plain notes", "Text studio", "Document shelf"])
                layout.addWidget(apps)
                s.check("associate", "Use for this type", layout=layout)
        s.button("ok", "OK", s.h.close)
        s.button("cancel", "Cancel", s.h.close)
        return s.h
