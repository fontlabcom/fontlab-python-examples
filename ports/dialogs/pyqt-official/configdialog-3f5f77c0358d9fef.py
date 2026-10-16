# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/3f5f77c0358d9fef.md
# this_file: ports/dialogs/pyqt-official/configdialog-3f5f77c0358d9fef.py

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
    with S.Session(qt, "Configuration pages", qt.QtGui.QDialog()) as s:
        s.vertical()
        row = s.g.QHBoxLayout()
        s.layout.addLayout(row)
        nav = s.keep("navigation", s.g.QListWidget(s.window))
        row.addWidget(nav)
        stack = s.keep("pages", s.g.QStackedWidget(s.window))
        row.addWidget(stack)
        for i, (title, color) in enumerate(
            [("Configuration", "#437f99"), ("Update", "#bd8741"), ("Query", "#658f5d")]
        ):
            item = s.g.QListWidgetItem(s.g.QIcon(S.pictogram(s, color)), title)
            nav.addItem(item)
            page = s.g.QWidget(stack)
            layout = s.vertical(page)
            stack.addWidget(page)
            if i == 0:
                s.combo(
                    "server",
                    ["Local test server", "North mirror", "South mirror"],
                    layout,
                )
            elif i == 1:
                for key in ["Applications", "Documentation", "Libraries"]:
                    s.check(key, key, layout=layout)
                packages = s.g.QListWidget(page)
                packages.addItems(
                    ["Example tools", "Reference pages", "Sample components"]
                )
                layout.addWidget(packages)
                s.button("update", "Update", layout=layout)
            else:
                s.line("name", layout=layout)
                s.add(s.g.QDateEdit(page), layout)
                s.combo("release", ["All releases", "Current release"], layout)
                s.check("upgrade", "Upgrades only", layout=layout)
                limit = s.spin("limit", 1, 100, 10, layout)
                limit.setSuffix(" results")
                limit.setSpecialValueText("One result")
                s.button("query", "Query", layout=layout)
        s.link(nav, "currentRowChanged(int)", lambda row: stack.setCurrentIndex(row))
        nav.setCurrentRow(0)
        s.button("close", "Close", s.h.close)
        return s.h
