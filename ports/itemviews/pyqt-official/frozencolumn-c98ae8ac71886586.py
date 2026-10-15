# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c98ae8ac71886586.md
# this_file: ports/itemviews/pyqt-official/frozencolumn-c98ae8ac71886586.py

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
    with S.Session(qt, "Frozen leading column") as s:
        s.vertical()
        model = s.model(
            ["Name", "Spring", "Summer", "Autumn", "Winter"],
            [
                [
                    f"Learner {i + 1}",
                    (i * 7) % 100,
                    (i * 11) % 100,
                    (i * 13) % 100,
                    (i * 17) % 100,
                ]
                for i in range(24)
            ],
        )
        table = s.view("table", model)
        frozen = s.keep("frozen", s.g.QTableView(table))
        frozen.setModel(model)
        frozen.setSelectionModel(table.selectionModel())
        frozen.verticalHeader().hide()
        frozen.setHorizontalScrollBarPolicy(s.c.Qt.ScrollBarAlwaysOff)
        frozen.setVerticalScrollBarPolicy(s.c.Qt.ScrollBarAlwaysOff)
        for col in range(1, 5):
            frozen.setColumnHidden(col, True)
        s.h.release.append(
            lambda: frozen.setModel(None) if not s.h.owner.closed else None
        )

        def geometry(*args):
            width = table.columnWidth(0)
            frozen.setColumnWidth(0, width)
            frozen.setGeometry(
                int(S.value(table.verticalHeader(), "width"))
                + int(S.value(table, "frameWidth")),
                int(S.value(table, "frameWidth")),
                width,
                int(S.value(table.viewport(), "height"))
                + int(S.value(table.horizontalHeader(), "height")),
            )

        busy = [False]

        def scroll(target, n):
            if busy[0]:
                return
            busy[0] = True
            try:
                target.setValue(n)
            finally:
                busy[0] = False

        s.link(
            table.verticalScrollBar(),
            "valueChanged(int)",
            lambda n: scroll(frozen.verticalScrollBar(), n),
        )
        s.link(
            frozen.verticalScrollBar(),
            "valueChanged(int)",
            lambda n: scroll(table.verticalScrollBar(), n),
        )
        s.link(
            table.horizontalHeader(),
            "sectionResized(int,int,int)",
            lambda section, old, new: geometry() if section == 0 else None,
        )
        s.link(
            table.verticalHeader(),
            "sectionResized(int,int,int)",
            lambda row, old, new: frozen.setRowHeight(row, new),
        )
        # A cheap geometry timer also covers viewport resizes performed by native layouts.
        s.timer("geometry_timer", 100, geometry)
        geometry()
        frozen.show()
        return s.h
