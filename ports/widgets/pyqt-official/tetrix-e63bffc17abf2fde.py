# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/e63bffc17abf2fde.md
# this_file: ports/widgets/pyqt-official/tetrix-e63bffc17abf2fde.py

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

SHAPES = [
    [(0, 0), (1, 0), (0, 1), (1, 1)],
    [(-1, 0), (0, 0), (1, 0), (2, 0)],
    [(-1, 0), (0, 0), (1, 0), (0, 1)],
    [(-1, 0), (0, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (-1, 1), (0, 1)],
    [(-1, 0), (0, 0), (1, 0), (-1, 1)],
    [(-1, 0), (0, 0), (1, 0), (1, 1)],
]


class Game:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.reset()

    def reset(self):
        self.board = [[0] * 10 for _ in range(22)]
        self.score = 0
        self.lines = 0
        self.pieces = 0
        self.level = 1
        self.playing = True
        self.paused = False
        self.next = self.rng.randrange(7)
        self.spawn()

    def spawn(self):
        self.kind = self.next
        self.next = self.rng.randrange(7)
        self.shape = list(SHAPES[self.kind])
        self.x = 4
        self.y = 0
        if not self.fits(self.x, self.y, self.shape):
            self.playing = False

    def fits(self, x, y, shape):
        return all(
            0 <= x + dx < 10 and 0 <= y + dy < 22 and not self.board[y + dy][x + dx]
            for dx, dy in shape
        )

    def move(self, dx, dy):
        if not self.playing or self.paused:
            return False
        if self.fits(self.x + dx, self.y + dy, self.shape):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self, clockwise=True):
        if self.kind == 0 or not self.playing or self.paused:
            return False
        rotated = [(-dy, dx) if clockwise else (dy, -dx) for dx, dy in self.shape]
        if self.fits(self.x, self.y, rotated):
            self.shape = rotated
            return True
        return False

    def place(self, distance=0):
        for dx, dy in self.shape:
            self.board[self.y + dy][self.x + dx] = self.kind + 1
        remaining = [row for row in self.board if not all(row)]
        cleared = 22 - len(remaining)
        self.board = [[0] * 10 for _ in range(cleared)] + remaining
        self.lines += cleared
        self.score += distance + 7 + cleared * 10
        self.pieces += 1
        self.level = 1 + self.pieces // 25
        self.spawn()

    def lower(self):
        if not self.playing or self.paused:
            return
        if not self.move(0, 1):
            self.place()

    def drop(self):
        if not self.playing or self.paused:
            return
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.place(distance)


def build(qt):
    with S.Session(qt, "Falling blocks") as s:
        s.vertical()
        game = Game()
        game.playing = False
        colors = [
            "#192b3a",
            "#d8aa42",
            "#3b93bc",
            "#9273b9",
            "#66a75a",
            "#bd6374",
            "#bc824e",
            "#5eaaa1",
        ]

        def paint(p, w, h):
            size = max(1, min(w // 10, h // 22))
            cells = [list(row) for row in game.board]
            if game.playing:
                for dx, dy in game.shape:
                    cells[game.y + dy][game.x + dx] = game.kind + 1
            for row in range(22):
                for col in range(10):
                    p.setBrush(s.g.QColor(colors[cells[row][col]]))
                    p.drawRect(col * size, row * size, size, size)

        def key(event):
            keys = {
                s.c.Qt.Key_Left: lambda: game.move(-1, 0),
                s.c.Qt.Key_Right: lambda: game.move(1, 0),
                s.c.Qt.Key_Down: lambda: game.rotate(True),
                s.c.Qt.Key_Up: lambda: game.rotate(False),
                s.c.Qt.Key_Space: game.drop,
                s.c.Qt.Key_D: game.lower,
            }
            if event.key() in keys:
                keys[event.key()]()
                update()

        face = S.canvas(s, paint, {"key": key})
        s.add(face)
        preview = s.keep("next_preview", s.label(""))
        score = s.keep("score", s.label("Score 0"))
        level = s.keep("level", s.label("Level 1"))
        lines = s.keep("lines", s.label("Lines 0"))

        def update():
            score.setText(f"Score {game.score}")
            level.setText(f"Level {game.level}")
            lines.setText(f"Lines {game.lines}")
            s.state.update(
                score=game.score,
                level=game.level,
                lines=game.lines,
                playing=game.playing,
                paused=game.paused,
                next=game.next,
                pieces=game.pieces,
            )
            pix = s.g.QPixmap(100, 60)
            pix.fill(s.g.QColor("#ffffff"))
            p = s.g.QPainter(pix)
            try:
                p.setBrush(s.g.QColor(colors[game.next + 1]))
                for x, y in SHAPES[game.next]:
                    p.drawRect((x + 2) * 15, (y + 1) * 15, 15, 15)
            finally:
                p.end()
            preview.setPixmap(pix)
            face.update()
            if game.playing and not game.paused:
                timer.start(max(1, 1000 // (1 + game.level)))
            else:
                timer.stop()

        def tick():
            game.lower()
            update()

        timer = s.timer("game_timer", 500, tick, start=False)

        def start():
            game.reset()
            face.setFocus()
            update()

        def pause():
            game.paused = not game.paused
            update()

        s.button("start", "Start", start)
        s.button("pause", "Pause", pause)
        s.button("quit", "Quit", s.h.close)
        s.keep("game", game)
        s.keep("update", update)
        update()
        return s.h
