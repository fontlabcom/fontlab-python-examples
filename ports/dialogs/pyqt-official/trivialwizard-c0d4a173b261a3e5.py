# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c0d4a173b261a3e5.md
# this_file: ports/dialogs/pyqt-official/trivialwizard-c0d4a173b261a3e5.py

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
    with S.Session(qt, "Registration walkthrough", qt.QtGui.QWizard()) as s:
        s.window.setOption(s.g.QWizard.IndependentPages, True)
        for i, title in enumerate(["Welcome", "Your details", "Ready"]):
            page = s.g.QWizardPage()
            page.setTitle(title)
            layout = s.vertical(page)
            if i == 1:
                layout.addWidget(s.g.QLabel("Name", page))
                s.line("name", layout=layout)
                layout.addWidget(s.g.QLabel("Email", page))
                s.line("email", layout=layout)
            else:
                s.label(
                    "Explore the pages; nothing is submitted."
                    if i == 0
                    else "You can now close the walkthrough.",
                    layout,
                )
            s.window.addPage(page)
        s.link(s.window, "accepted()", lambda *a: s.h.close())
        s.link(s.window, "rejected()", lambda *a: s.h.close())
        return s.h
