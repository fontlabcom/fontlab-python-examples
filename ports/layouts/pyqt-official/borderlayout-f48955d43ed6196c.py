# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/f48955d43ed6196c.md
# this_file: ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py

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
    with S.Session(qt, "Border regions") as s:
        grid = s.g.QGridLayout(s.window)
        for text, r, c, rs, cs in [
            ("North", 0, 0, 1, 4),
            ("South", 2, 0, 1, 4),
            ("West", 1, 0, 1, 1),
            ("East one", 1, 2, 1, 1),
            ("East two", 1, 3, 1, 1),
        ]:
            label = s.keep(text, s.g.QLabel(text, s.window))
            label.setMinimumSize(40, 28)
            grid.addWidget(label, r, c, rs, cs)
        center = s.keep(
            "center",
            s.g.QTextEdit("The middle region grows with the window.", s.window),
        )
        grid.addWidget(center, 1, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(1, 1)
        s.keep("layout", grid)
        return s.h
