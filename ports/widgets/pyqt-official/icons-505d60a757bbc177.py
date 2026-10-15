# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/505d60a757bbc177.md
# this_file: ports/widgets/pyqt-official/icons-505d60a757bbc177.py

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
    with S.Session(qt, "Icon mode and state preview") as s:
        s.vertical()
        images = []
        table = s.table("images", ["Image", "Mode", "State"], [])
        grid = s.g.QGridLayout()
        s.layout.addLayout(grid)
        previews = []
        modes = [
            s.g.QIcon.Normal,
            s.g.QIcon.Disabled,
            s.g.QIcon.Active,
            s.g.QIcon.Selected,
        ]
        states = [s.g.QIcon.Off, s.g.QIcon.On]
        for row in range(4):
            for col in range(2):
                label = s.g.QLabel(s.window)
                grid.addWidget(label, row, col)
                previews.append(label)
        size = s.spin("size", 8, 256, 32)
        choice = s.combo("style", list(s.g.QStyleFactory.keys()))
        infer = s.check("infer", "Infer mode and state from filename")
        busy = [False]

        def refresh(*args):
            if busy[0]:
                return
            icon = s.g.QIcon()
            for row, pixmap in enumerate(images):
                mode = str(S.value(table.item(row, 1), "text")).lower()
                state = str(S.value(table.item(row, 2), "text")).lower()
                mode_index = (
                    ["normal", "disabled", "active", "selected"].index(mode)
                    if mode in ["normal", "disabled", "active", "selected"]
                    else 0
                )
                icon.addPixmap(
                    pixmap,
                    modes[mode_index],
                    s.g.QIcon.On if state == "on" else s.g.QIcon.Off,
                )
            n = int(S.value(size, "value"))
            for i, label in enumerate(previews):
                label.setPixmap(icon.pixmap(n, n, modes[i // 2], states[i % 2]))
            s.state.update(images=len(images), size=n)

        def add(path=None, color="#357eb0"):
            pixmap = s.g.QPixmap(path) if path else S.pictogram(s, color, 64)
            if pixmap.isNull():
                raise ValueError("Invalid image")
            row = len(images)
            images.append(pixmap)
            busy[0] = True
            try:
                table.insertRow(row)
                name = Path(path).name if path else "New procedural marker"
                mode = "normal"
                state = "off"
                if bool(S.value(infer, "checked")):
                    for option in ["disabled", "active", "selected"]:
                        if option in name.lower():
                            mode = option
                    if "on" in name.lower():
                        state = "on"
                for col, text in enumerate([name, mode, state]):
                    table.setItem(row, col, s.g.QTableWidgetItem(text))
            finally:
                busy[0] = False
            refresh()

        def clear():
            images.clear()
            table.setRowCount(0)
            refresh()

        s.link(table, "cellChanged(int,int)", refresh)
        s.link(size, "valueChanged(int)", refresh)
        s.link(
            choice,
            "currentIndexChanged(int)",
            lambda i: s.local_style(str(S.value(choice, "currentText"))),
        )
        for n in [16, 32, 64]:
            radio = s.g.QRadioButton(str(n) + " px", s.window)
            s.add(radio)
            s.link(
                radio,
                "toggled(bool)",
                lambda flag, size_=n: size.setValue(size_) if flag else None,
            )
        s.menu(
            "File",
            [
                ("Add image", lambda: s.choose(add)),
                ("Remove all", clear),
                ("Exit", s.h.close),
            ],
        )
        s.menu("View", [("Refresh", refresh)])
        s.menu(
            "Help",
            [
                (
                    "About",
                    lambda: s.state.update(
                        help="Each preview requests one icon mode and state."
                    ),
                )
            ],
        )
        add()
        add(color="#bf873e")
        s.keep("add_image", add)
        s.keep("clear", clear)
        return s.h
