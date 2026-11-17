# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/509e781f1267967f.md
# this_file: Scripts/Widgets/Waving Text.py

"""Show waving text using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S

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


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_wiggly-509e781f1267967f', 'Waving Text')


if __name__ == "__main__":
    main()
