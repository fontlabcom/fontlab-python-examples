# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/f702b62aa47629ad.md
# this_file: Scripts/Widgets/Group Box Gallery.py

"""Show group box gallery using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Group boxes") as s:
        s.vertical()
        for i, title in enumerate(
            [
                "Radio choices",
                "Checkable choices",
                "Independent states",
                "Button styles",
            ]
        ):
            group = s.keep("group_" + str(i), s.g.QGroupBox(title, s.window))
            layout = s.vertical(group)
            s.add(group)
            if i < 2:
                if i == 1:
                    group.setCheckable(True)
                    group.setChecked(True)
                for n in range(3):
                    radio = s.g.QRadioButton("Choice " + str(n + 1), group)
                    layout.addWidget(radio)
                    if n == 0:
                        radio.setChecked(True)
                if i == 0:
                    s.check("independent", "Independent", layout=layout)
            elif i == 2:
                s.check("plain", "Ordinary checkbox", layout=layout)
                tri = s.check("tri", "Three states", layout=layout)
                tri.setTristate(True)
            else:
                s.button("normal", "Normal", layout=layout)
                toggle = s.button("toggle", "Toggle", layout=layout)
                toggle.setCheckable(True)
                flat = s.button("flat", "Flat", layout=layout)
                flat.setFlat(True)
                popup = s.button("popup", "Options", layout=layout)
                menu = s.g.QMenu(popup)
                menu.addAction("Example")
                menu.addMenu("More").addAction("Another choice")
                popup.setMenu(menu)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_groupbox-f702b62aa47629ad', 'Group Box Gallery')


if __name__ == "__main__":
    main()
