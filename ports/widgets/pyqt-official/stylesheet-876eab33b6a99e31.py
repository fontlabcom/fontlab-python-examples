# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/876eab33b6a99e31.md
# this_file: ports/widgets/pyqt-official/stylesheet-876eab33b6a99e31.py

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

PRESETS = {
    "Restrained": "QWidget { background: #f3f5f7; color: #243347; } QPushButton { padding: 6px; }",
    "Cafe": "QWidget { background: #f7e9cf; color: #583c2c; } QPushButton { background: #d8b38b; padding: 7px; }",
    "Folded paper": "QWidget { background: #faf8ee; color: #38474a; } QPushButton { border: 2px solid #708b90; border-radius: 2px; padding: 7px; }",
}


def build(qt):
    with S.Session(qt, "Local stylesheet sample") as s:
        s.vertical()
        s.label("A sample panel")
        s.line("sample_name", "Editable sample")
        s.check("sample_check", "Sample choice")
        s.spin("sample_value", 0, 100, 25)
        s.button("sample_button", "A sample button")
        editor = s.keep("editor", s.alert(s.g.QDialog(s.window)))
        layout = s.vertical(editor)
        preset = s.combo("preset", list(PRESETS), layout)
        style = s.combo("style", list(s.g.QStyleFactory.keys()), layout)
        text = s.keep("stylesheet", s.g.QPlainTextEdit(editor))
        layout.addWidget(text)

        def choose(index):
            text.setPlainText(PRESETS[list(PRESETS)[index]])

        def apply():
            css = str(text.toPlainText())
            s.window.setStyleSheet(css)
            editor.setStyleSheet(css)
            s.state["stylesheet"] = css

        def save(path):
            Path(path).write_text(str(text.toPlainText()), encoding="utf-8")

        s.link(preset, "currentIndexChanged(int)", choose)
        s.link(
            style,
            "currentIndexChanged(int)",
            lambda index: s.local_style(
                str(S.value(style, "currentText")), [s.window, editor]
            ),
        )
        choose(0)
        s.button("apply", "Apply", apply, layout)
        s.button("save", "Save", lambda: s.choose(save, save=True), layout)
        s.button("edit", "Edit stylesheet", editor.show)
        s.keep("apply_style", apply)
        return s.h
