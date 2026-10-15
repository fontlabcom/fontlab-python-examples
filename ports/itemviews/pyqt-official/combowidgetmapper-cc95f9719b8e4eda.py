# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/cc95f9719b8e4eda.md
# this_file: ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py

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
    with S.Session(qt, "Mapped address records") as s:
        s.vertical()
        model = s.model(
            ["Name", "Address", "Type" if True else "Age"],
            [
                [name, f"{i + 1} Example Lane", i % 3 if True else 20 + i * 7]
                for i, name in enumerate(["Mira", "Rowan", "Ellis", "Sage", "Aster"])
            ],
        )
        name = s.line("name")
        address = s.keep("address", s.g.QTextEdit(s.window))
        s.add(address)
        third = (
            s.combo("type", ["Residential", "Work", "Other"])
            if True
            else s.spin("age", 0, 150, 20)
        )
        mapper = s.keep("mapper", s.g.QDataWidgetMapper(s.window))
        mapper.setModel(model)
        mapper.addMapping(name, 0)
        mapper.addMapping(address, 1, s.c.QByteArray(b"plainText"))
        if True:
            mapper.addMapping(third, 2, s.c.QByteArray(b"currentIndex"))
        else:
            mapper.addMapping(third, 2)
        previous = s.button("previous", "Previous", mapper.toPrevious)
        next_button = s.button("next", "Next", mapper.toNext)

        def buttons(index):
            previous.setEnabled(index > 0)
            next_button.setEnabled(index < 4)
            s.state["record"] = index

        s.link(mapper, "currentIndexChanged(int)", buttons)
        mapper.toFirst()
        buttons(0)
        s.h.release.append(
            lambda: mapper.setModel(None) if not s.h.owner.closed else None
        )
        return s.h
