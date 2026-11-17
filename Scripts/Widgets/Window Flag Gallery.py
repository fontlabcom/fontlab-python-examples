# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/136c45cc9f97c218.md
# this_file: Scripts/Widgets/Window Flag Gallery.py

"""Show window flag gallery using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Window flags") as s:
        s.vertical()
        preview = s.keep("preview", s.alert(s.g.QWidget()))
        pl = s.vertical(preview)
        text = s.g.QPlainTextEdit(preview)
        text.setReadOnly(True)
        pl.addWidget(text)
        button = s.g.QPushButton("Close", preview)
        pl.addWidget(button)
        s.link(button, "clicked()", lambda *a: preview.hide())
        type_group = s.g.QGroupBox("Window type", s.window)
        tl = s.vertical(type_group)
        s.add(type_group)
        types = []
        hints = []
        for name in ["Window", "Dialog", "Tool", "Popup"]:
            radio = s.g.QRadioButton(name, type_group)
            tl.addWidget(radio)
            types.append((name, radio))
        for name in [
            "FramelessWindowHint",
            "WindowStaysOnTopHint",
            "WindowTitleHint",
            "WindowCloseButtonHint",
        ]:
            hints.append((name, s.check(name, name)))

        def apply(*args):
            flags = 0
            names = []
            for name, box in types + hints:
                if bool(S.value(box, "checked")):
                    flags |= int(getattr(s.c.Qt, name))
                    names.append(name)
            preview.setWindowFlags(flags)
            preview.setAttribute(s.c.Qt.WA_QuitOnClose, False)
            preview.move(
                max(0, int(S.value(preview, "x"))), max(0, int(S.value(preview, "y")))
            )
            text.setPlainText("\n".join(names))
            preview.show()
            s.state["flags"] = flags
            s.state["flag_names"] = names

        for name, box in types + hints:
            s.link(box, "toggled(bool)", apply)
        types[0][1].setChecked(True)
        s.button("quit", "Quit", s.h.close)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_windowflags-136c45cc9f97c218', 'Window Flag Gallery')


if __name__ == "__main__":
    main()
