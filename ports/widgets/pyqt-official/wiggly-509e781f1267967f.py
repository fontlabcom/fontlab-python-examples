# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/509e781f1267967f.md
# this_file: ports/widgets/pyqt-official/wiggly-509e781f1267967f.py

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

import math


def build(qt):
    with S.Session(qt, "Waving text") as s:
        s.vertical()
        s.state.update(text="Hello, moving letters", phase=0)

        def paint(p, w, h):
            text = s.state["text"]
            if not text:
                return
            metrics = s.g.QFontMetrics(S.value(s.window, "font"))
            widths = [int(metrics.width(ch)) for ch in text]
            x = (w - sum(widths)) // 2
            for i, (char, width) in enumerate(zip(text, widths)):
                phase = (s.state["phase"] + i) % 16
                p.setPen(s.g.QColor.fromHsv((phase * 22) % 360, 200, 210))
                p.drawText(
                    int(x), int(h // 2 + math.sin(phase * math.pi / 8) * 15), char
                )
                x += width

        face = S.canvas(s, paint)
        s.add(face)
        entry = s.line("entry", s.state["text"])
        s.link(
            entry,
            "textChanged(QString)",
            lambda text: (s.state.update(text=str(text)), face.update()),
        )

        def tick():
            s.state["phase"] = (s.state["phase"] + 1) % 16
            face.update()

        # The basic timer's native overload includes an explicit TimerType.
        class Receiver(qt.private.QObject):
            def timerEvent(self, event):
                tick()

        receiver = s.keep("receiver", Receiver(s.window))
        timer = s.keep("wave_timer", s.c.QBasicTimer())
        timer.start(60, s.c.Qt.CoarseTimer, receiver)
        s.h.cleanup.append(lambda: timer.stop() if not s.h.owner.closed else None)
        s.keep("tick", tick)
        return s.h
