# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/27bf65f8b059fd96.md
# this_file: Scripts/Widgets/Calculator Form.py

"""Show calculator form using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Add two integers") as s:
        s.vertical()
        a = s.spin("first")
        s.label("+")
        b = s.spin("second")
        s.label("=")
        result = s.keep("result", s.label("0"))

        def update(*args):
            total = int(S.value(a, "value")) + int(S.value(b, "value"))
            result.setText(str(total))
            s.state["sum"] = total

        s.link(a, "valueChanged(int)", update)
        s.link(b, "valueChanged(int)", update)
        update()
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_calculatorform-27bf65f8b059fd96', 'Calculator Form')


if __name__ == "__main__":
    main()
