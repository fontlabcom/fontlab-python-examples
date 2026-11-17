# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/c98ae8ac71886586.md
# this_file: Scripts/Item Views/Frozen Column.py

"""Frozen Column: modeless PythonQt demonstration; no font data is changed."""

from fontlab_python_lessons import qt_demos as S


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


def main():
    """Open this example through the retained App dialog owner."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_frozencolumn-c98ae8ac71886586', 'Frozen Column')


if __name__ == "__main__":
    main()
