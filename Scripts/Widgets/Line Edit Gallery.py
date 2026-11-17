# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/84cb59e07adfae2c.md
# this_file: Scripts/Widgets/Line Edit Gallery.py

"""Show line edit gallery using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Line edit behaviors") as s:
        s.vertical()
        options = [
            ("echo", ["Visible", "Password", "Visible while editing", "Hidden"]),
            ("validator", ["None", "Integer", "Decimal"]),
            ("alignment", ["Left", "Center", "Right"]),
            ("mask", ["None", "Phone", "Date", "Key"]),
            ("access", ["Editable", "Read only"]),
        ]
        for key, items in options:
            group = s.g.QGroupBox(key.title(), s.window)
            layout = s.vertical(group)
            s.add(group)
            choice = s.combo(key, items, layout)
            edit = s.line(key + "_edit", "", layout)
            if key == "echo":
                callback = lambda i, e=edit: e.setEchoMode(
                    [
                        s.g.QLineEdit.Normal,
                        s.g.QLineEdit.Password,
                        s.g.QLineEdit.PasswordEchoOnEdit,
                        s.g.QLineEdit.NoEcho,
                    ][i]
                )
            elif key == "validator":
                integer = s.g.QIntValidator(-999, 999, edit)
                decimal = s.g.QDoubleValidator(-999.0, 999.0, 3, edit)
                s.keep("integer_validator", integer)
                s.keep("decimal_validator", decimal)
                callback = lambda i, e=edit, a=integer, b=decimal: e.setValidator(
                    [None, a, b][i]
                )
            elif key == "alignment":
                callback = lambda i, e=edit: e.setAlignment(
                    [s.c.Qt.AlignLeft, s.c.Qt.AlignCenter, s.c.Qt.AlignRight][i]
                )
            elif key == "mask":
                callback = lambda i, e=edit: e.setInputMask(
                    ["", "+99 999 999 999;_", "0000-00-00;_", ">AAAAA-AAAAA;_"][i]
                )
            else:
                callback = lambda i, e=edit: e.setReadOnly(i == 1)
            s.link(choice, "currentIndexChanged(int)", callback)
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_lineedits-84cb59e07adfae2c', 'Line Edit Gallery')


if __name__ == "__main__":
    main()
