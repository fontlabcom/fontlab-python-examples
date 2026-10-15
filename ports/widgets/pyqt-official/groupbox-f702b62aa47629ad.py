# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/f702b62aa47629ad.md
# this_file: ports/widgets/pyqt-official/groupbox-f702b62aa47629ad.py

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
    with S.Session(qt, "Group boxes") as s:
        s.vertical()
        for i, title in enumerate(
            [
                "Radio choices",
                "Checkable choices",
                "Independent states",
                "Button styles",
            ]
        ):
            group = s.keep("group_" + str(i), s.g.QGroupBox(title, s.window))
            layout = s.vertical(group)
            s.add(group)
            if i < 2:
                if i == 1:
                    group.setCheckable(True)
                    group.setChecked(True)
                for n in range(3):
                    radio = s.g.QRadioButton("Choice " + str(n + 1), group)
                    layout.addWidget(radio)
                    if n == 0:
                        radio.setChecked(True)
                if i == 0:
                    s.check("independent", "Independent", layout=layout)
            elif i == 2:
                s.check("plain", "Ordinary checkbox", layout=layout)
                tri = s.check("tri", "Three states", layout=layout)
                tri.setTristate(True)
            else:
                s.button("normal", "Normal", layout=layout)
                toggle = s.button("toggle", "Toggle", layout=layout)
                toggle.setCheckable(True)
                flat = s.button("flat", "Flat", layout=layout)
                flat.setFlat(True)
                popup = s.button("popup", "Options", layout=layout)
                menu = s.g.QMenu(popup)
                menu.addAction("Example")
                menu.addMenu("More").addAction("Another choice")
                popup.setMenu(menu)
        return s.h
