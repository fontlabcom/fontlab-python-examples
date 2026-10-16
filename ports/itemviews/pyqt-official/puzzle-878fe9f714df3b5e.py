# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/878fe9f714df3b5e.md
# this_file: ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py

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

import random

MIME = "application/x-fontlab-cleanroom-tile"


def build(qt):
    with S.Session(qt, "Five by five tile puzzle") as s:
        s.vertical()
        c = s.c
        g = s.g
        rng = random.Random()
        unplaced = list(range(25))
        rng.shuffle(unplaced)
        board = [None] * 25
        picture = [
            S.port(
                "widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py"
            ).generated_image(qt, 250, 250)
        ]
        painter = g.QPainter(picture[0])
        try:
            for number in range(25):
                row, col = divmod(number, 5)
                painter.setBrush(g.QColor.fromHsv(number * 14, 150, 230))
                painter.drawRect(col * 50, row * 50, 50, 50)
                painter.drawText(
                    col * 50, row * 50, 50, 50, c.Qt.AlignCenter, str(number + 1)
                )
        finally:
            painter.end()

        def tile(identity):
            row, col = divmod(identity, 5)
            return g.QPixmap.fromImage(picture[0].copy(col * 50, row * 50, 50, 50))

        def mime(indexes, board_source):
            data = c.QMimeData()
            if indexes:
                index = indexes[0]
                identity = (
                    board[index.row() * 5 + index.column()]
                    if board_source
                    else unplaced[index.row()]
                )
                if identity is not None:
                    data.setData(MIME, c.QByteArray(str(identity).encode("ascii")))
            return data

        def identity(data):
            if not data.hasFormat(MIME):
                return None
            try:
                raw = data.data(MIME)
                number = int(bytes(raw.data()) if hasattr(raw, "data") else bytes(raw))
                return number if 0 <= number < 25 else None
            except (ValueError, TypeError):
                return None

        def state():
            s.state.update(
                placed=sum(x is not None for x in board),
                correct=sum(x == i for i, x in enumerate(board)),
                complete=all(x == i for i, x in enumerate(board)),
            )

        def move(number, target):
            if not 0 <= number < 25 or (
                target is not None
                and (not 0 <= target < 25 or board[target] is not None)
            ):
                return False
            source = board.index(number) if number in board else None
            if source is None and number not in unplaced:
                return False
            if target is None:
                if source is None:
                    return False
                row = len(unplaced)
                list_model.beginInsertRows(c.QModelIndex(), row, row)
                unplaced.append(number)
                list_model.endInsertRows()
            elif number in unplaced:
                row = unplaced.index(number)
                list_model.beginRemoveRows(c.QModelIndex(), row, row)
                unplaced.pop(row)
                list_model.endRemoveRows()
            if source is not None:
                board[source] = None
            if target is not None:
                board[target] = number
            board_model.dataChanged(
                board_model.index(0, 0), board_model.index(4, 4), []
            )
            state()
            return True

        class Pieces(c.QAbstractListModel):
            def rowCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() else len(unplaced)

            def data(self, index, role=c.Qt.DisplayRole):
                if not index.isValid() or not 0 <= index.row() < len(unplaced):
                    return None
                number = unplaced[index.row()]
                if role == c.Qt.DecorationRole:
                    return tile(number)
                if role == c.Qt.DisplayRole:
                    return f"{number // 5 + 1}, {number % 5 + 1}"
                return None

            def flags(self, index):
                return (
                    c.Qt.ItemIsEnabled
                    | c.Qt.ItemIsSelectable
                    | c.Qt.ItemIsDragEnabled
                    | c.Qt.ItemIsDropEnabled
                )

            def mimeTypes(self):
                return [MIME]

            def mimeData(self, indexes):
                return mime(indexes, False)

            def supportedDropActions(self):
                return c.Qt.MoveAction

            def dropMimeData(self, data, action, row, col, parent):
                number = identity(data)
                return move(number, None) if number is not None else False

        class Board(g.QAbstractTableModel):
            def rowCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() else 5

            def columnCount(self, parent=None):
                if parent is None:
                    parent = c.QModelIndex()
                return 0 if parent.isValid() else 5

            def data(self, index, role=c.Qt.DisplayRole):
                if not index.isValid():
                    return None
                number = board[index.row() * 5 + index.column()]
                if role == c.Qt.DecorationRole and number is not None:
                    return tile(number)
                return None

            def flags(self, index):
                return (
                    c.Qt.ItemIsEnabled
                    | c.Qt.ItemIsSelectable
                    | c.Qt.ItemIsDragEnabled
                    | c.Qt.ItemIsDropEnabled
                )

            def mimeTypes(self):
                return [MIME]

            def mimeData(self, indexes):
                return mime(indexes, True)

            def supportedDropActions(self):
                return c.Qt.MoveAction

            def dropMimeData(self, data, action, row, col, parent):
                number = identity(data)
                if parent.isValid():
                    row, col = parent.row(), parent.column()
                return (
                    move(number, row * 5 + col)
                    if number is not None and 0 <= row < 5 and 0 <= col < 5
                    else False
                )

        list_model = s.keep("pieces_model", Pieces(s.window))
        board_model = s.keep("board_model", Board(s.window))
        list_view = s.view("pieces", list_model, "QListView")
        board_view = s.view("board", board_model)
        list_view.setViewMode(g.QListView.IconMode)
        board_view.horizontalHeader().setDefaultSectionSize(50)
        board_view.verticalHeader().setDefaultSectionSize(50)
        for view in [list_view, board_view]:
            view.setDragDropMode(g.QAbstractItemView.DragDrop)
            view.setDragEnabled(True)
            view.setAcceptDrops(True)
            view.setDropIndicatorShown(True)
            view.setDefaultDropAction(c.Qt.MoveAction)

        def restart():
            list_model.beginResetModel()
            board_model.beginResetModel()
            unplaced[:] = range(25)
            rng.shuffle(unplaced)
            board[:] = [None] * 25
            list_model.endResetModel()
            board_model.endResetModel()
            state()

        def load(path):
            image = g.QImage(path)
            if image.isNull():
                raise ValueError("Cannot read puzzle image")
            picture[0] = image.scaled(
                250, 250, c.Qt.IgnoreAspectRatio, c.Qt.SmoothTransformation
            )
            restart()

        s.menu("File", [("Open", lambda: s.choose(load)), ("Exit", s.h.close)])
        s.menu("Game", [("Restart", restart)])
        s.keep("move", move)
        s.keep("restart", restart)
        s.keep("unplaced", unplaced)
        s.keep("board_cells", board)
        state()
        return s.h
