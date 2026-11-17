# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/1321540b04f33117.md
# this_file: Scripts/Widgets/Counter Label.py

"""Show counter label using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Counter component") as s:
        s.vertical()
        s.state.update(minimum=1, maximum=1, value=1, offset=0, notifications=[])

        def paint(p, w, h):
            font = s.g.QFont(S.value(s.window, "font"))
            font.setPixelSize(
                max(1, min(h, int(w / max(1, len(str(s.state["maximum"]))))))
            )
            p.setFont(font)
            p.drawText(0, 0, w, h, s.c.Qt.AlignCenter, str(s.state["value"]))

        face = S.canvas(s, paint)
        s.add(face)

        def change(key, n):
            n = int(n)
            if key == "value" and not s.state["minimum"] <= n <= s.state["maximum"]:
                return False
            if key == "minimum" and n > s.state["maximum"]:
                return False
            if key == "maximum" and n < s.state["minimum"]:
                return False
            s.state[key] = n
            if key == "value":
                emitted = n + s.state["offset"]
                s.state["notifications"].append([emitted, str(emitted)])
            face.update()
            return True

        for key in ["minimum", "maximum", "value", "offset"]:
            s.keep("set_" + key, lambda n, k=key: change(k, n))
        s.keep("step_up", lambda: change("value", s.state["value"] + 1))
        s.keep("step_down", lambda: change("value", s.state["value"] - 1))
        s.keep("set_font", face.setFont)
        change("value", 123)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_counterlabel-1321540b04f33117', 'Counter Label')


if __name__ == "__main__":
    main()
