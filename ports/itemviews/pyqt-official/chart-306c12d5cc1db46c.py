# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/306c12d5cc1db46c.md
# this_file: ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py

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

import csv
import io
import math

DATA = [["Paper", 14.0, "#467d9e"], ["Wood", 9.0, "#be985e"], ["Cloth", 7.0, "#8f6ea3"]]


def read_rows(text):
    rows = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) != 3:
            raise ValueError("Each row needs label, quantity and color")
        number = float(row[1])
        if not math.isfinite(number):
            raise ValueError("Quantity must be finite")
        rows.append([row[0], number, row[2]])
    return rows


def valid_color(s, text):
    import re

    if text.startswith("#"):
        return bool(
            re.fullmatch(
                r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8}|[0-9a-fA-F]{9}|[0-9a-fA-F]{12})",
                text,
            )
        )
    return text.lower() in [str(name).lower() for name in s.g.QColor.colorNames()]


def write_rows(rows):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerows(rows)
    return stream.getvalue()


def slices(rows):
    total = sum(max(0.0, float(row[1])) for row in rows)
    angle = 0.0
    result = []
    for row in rows:
        span = max(0.0, float(row[1])) / total * 360 if total else 0.0
        result.append((angle, span))
        angle += span
    return result


def build(qt):
    with S.Session(qt, "Editable pie data") as s:
        s.vertical()
        split = s.keep("splitter", s.g.QSplitter(s.window))
        s.add(split)
        model = s.model(["Label", "Quantity", "Color"], DATA)
        view = s.keep("table", s.g.QTableView(split))
        view.setModel(model)
        split.addWidget(view)
        selection = view.selectionModel()
        s.keep("selection", selection)
        rows = [list(row) for row in DATA]
        busy = [False]
        drag = [None]

        def chosen():
            return {index.row() for index in S.value(selection, "selectedIndexes")}

        def paint(p, w, h):
            diameter = max(1, min(w - 20, h - 100))
            selected = chosen()
            for i, (start, span) in enumerate(slices(rows)):
                p.setBrush(s.g.QColor(rows[i][2]))
                p.setPen(s.g.QPen(s.g.QColor("#152d41"), 3 if i in selected else 1))
                p.drawPie(10, 10, diameter, diameter, int(start * 16), int(span * 16))
                p.drawText(12, diameter + 28 + i * 18, str(rows[i][0]))

        def point(event):
            pos = event.pos()
            return int(S.value(pos, "x")), int(S.value(pos, "y"))

        def pick(x, y):
            d = max(
                1,
                min(
                    int(S.value(face, "width")) - 20, int(S.value(face, "height")) - 100
                ),
            )
            dx = x - 10 - d / 2
            dy = 10 + d / 2 - y
            if dx * dx + dy * dy > (d / 2) ** 2:
                return None
            angle = math.degrees(math.atan2(dy, dx)) % 360
            return next(
                (
                    i
                    for i, (start, span) in enumerate(slices(rows))
                    if span > 0 and start <= angle < start + span
                ),
                None,
            )

        def press(event):
            drag[0] = point(event)

        def release(event):
            if drag[0] is None:
                return
            x, y = point(event)
            x0, y0 = drag[0]
            drag[0] = None
            indexes = []
            if abs(x - x0) + abs(y - y0) < 5:
                index = pick(x, y)
                if index is not None:
                    indexes = [index]
            else:
                # Sample the rubber rectangle over the same angular hit-test.
                seen = set()
                for px in range(min(x, x0), max(x, x0) + 1, 4):
                    for py in range(min(y, y0), max(y, y0) + 1, 4):
                        index = pick(px, py)
                        if index is not None:
                            seen.add(index)
                indexes = sorted(seen)
            selection.clearSelection()
            for index in indexes:
                selection.select(
                    model.index(index, 0),
                    s.g.QItemSelectionModel.Select | s.g.QItemSelectionModel.Rows,
                )
            face.update()

        face = S.canvas(s, paint, {"press": press, "release": release})
        split.addWidget(face)

        def replace(new):
            for row in new:
                if not valid_color(s, row[2]):
                    raise ValueError("Invalid color")
            busy[0] = True
            try:
                model.setRowCount(len(new))
                for r, row in enumerate(new):
                    for c, val in enumerate(row):
                        model.setData(model.index(r, c), str(val), s.c.Qt.EditRole)
                rows[:] = new
            finally:
                busy[0] = False
            face.update()
            s.state["rows"] = [list(row) for row in rows]

        def changed(*args):
            if busy[0]:
                return
            try:
                new = [
                    [
                        str(model.data(model.index(r, c), s.c.Qt.EditRole))
                        for c in range(3)
                    ]
                    for r in range(int(S.value(model, "rowCount")))
                ]
                parsed = read_rows(write_rows(new))
                replace(parsed)
                s.state["error"] = ""
            except (ValueError, OverflowError) as error:
                s.state["error"] = str(error)
                replace([list(row) for row in rows])

        def load(path):
            replace(read_rows(Path(path).read_text(encoding="utf-8")))

        def save(path):
            Path(path).write_text(write_rows(rows), encoding="utf-8")

        s.link(model, "dataChanged(QModelIndex,QModelIndex,QVector<int>)", changed)
        s.link(
            selection,
            "selectionChanged(QItemSelection,QItemSelection)",
            lambda *a: face.update(),
        )
        s.menu(
            "File",
            [
                ("Open", lambda: s.choose(load)),
                ("Save As", lambda: s.choose(save, save=True)),
                ("Exit", s.h.close),
            ],
        )
        s.h.release.append(
            lambda: view.setModel(None) if not s.h.owner.closed else None
        )
        s.keep("load", load)
        s.keep("save", save)
        s.keep("replace", replace)
        s.state["rows"] = [list(row) for row in rows]
        return s.h
