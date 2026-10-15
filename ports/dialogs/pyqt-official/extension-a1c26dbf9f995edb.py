# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/a1c26dbf9f995edb.md
# this_file: ports/dialogs/pyqt-official/extension-a1c26dbf9f995edb.py

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
    with S.Session(qt, "Expandable search", qt.QtGui.QDialog()) as s:
        s.vertical()
        s.line("query")
        s.check("case", "Match case")
        s.check("start", "From beginning")
        s.button("find", "Find")
        more = s.button("more", "More")
        more.setCheckable(True)
        extension = s.keep("extension", s.g.QWidget(s.window))
        extra = s.vertical(extension)
        for key, text in [
            ("whole", "Whole words"),
            ("backward", "Search backward"),
            ("selection", "Selection only"),
        ]:
            s.check(key, text, layout=extra)
        s.add(extension)
        extension.hide()
        s.layout.setSizeConstraint(s.g.QLayout.SetFixedSize)

        def expand(checked):
            extension.setVisible(bool(checked))
            s.state["expanded"] = bool(checked)
            s.window.adjustSize()

        s.link(more, "toggled(bool)", expand)
        s.state["expanded"] = False
        return s.h
