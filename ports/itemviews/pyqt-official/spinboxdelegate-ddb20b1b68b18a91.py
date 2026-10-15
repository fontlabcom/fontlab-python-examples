# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ddb20b1b68b18a91.md
# this_file: ports/itemviews/pyqt-official/spinboxdelegate-ddb20b1b68b18a91.py

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


def build(qt):
    with S.Session(qt, "Numeric cell delegate") as s:
        s.vertical()
        model = s.model(
            ["Factor A", "Factor B"],
            [[(r + 1) * (c + 1) for c in range(2)] for r in range(4)],
        )
        view = s.view("table", model)

        class Delegate(s.g.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                editor = s.g.QSpinBox(parent)
                editor.setRange(0, 100)
                return editor

            def setEditorData(self, editor, index):
                editor.setValue(int(model.data(index, s.c.Qt.EditRole)))

            def setModelData(self, editor, target, index):
                editor.interpretText()
                target.setData(index, int(S.value(editor, "value")), s.c.Qt.EditRole)

            def updateEditorGeometry(self, editor, option, index):
                editor.setGeometry(option.rect)

        delegate = s.keep("delegate", Delegate(view))
        view.setItemDelegate(delegate)
        return s.h
