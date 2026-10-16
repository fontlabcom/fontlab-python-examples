# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0a3b15766909bdc3.md
# this_file: ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py

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
    with S.Session(qt, "Color editor factory") as s:
        s.vertical()
        model = s.model(
            ["Name", "Color"], [["Bay", "blue"], ["Moss", "green"], ["Clay", "red"]]
        )
        names = ["blue", "green", "red", "yellow", "white", "black"]
        for row, name in enumerate(["blue", "green", "red"]):
            model.setData(model.index(row, 1), s.g.QColor(name), s.c.Qt.EditRole)
        view = s.view("table", model)

        class Creator(s.g.QItemEditorCreatorBase):
            def createWidget(self, parent):
                editor = s.g.QComboBox(parent)
                editor.addItems(names)
                return editor

            def valuePropertyName(self):
                return s.c.QByteArray(b"currentIndex")

        factory = s.keep("factory", s.g.QItemEditorFactory())
        creator = s.keep("creator", Creator())
        factory.registerEditor(s.c.QMetaType.type("QColor"), creator)

        class Delegate(s.g.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                return (
                    creator.createWidget(parent)
                    if index.column() == 1
                    else s.g.QStyledItemDelegate.createEditor(
                        self, parent, option, index
                    )
                )

            def setEditorData(self, editor, index):
                if index.column() != 1:
                    return s.g.QStyledItemDelegate.setEditorData(self, editor, index)
                color = s.g.QColor(model.data(index, s.c.Qt.EditRole))
                editor.setCurrentIndex(
                    next(
                        (
                            i
                            for i, name in enumerate(names)
                            if s.g.QColor(name).name() == color.name()
                        ),
                        0,
                    )
                )

            def setModelData(self, editor, target, index):
                if index.column() != 1:
                    return s.g.QStyledItemDelegate.setModelData(
                        self, editor, target, index
                    )
                target.setData(
                    index,
                    s.g.QColor(names[int(S.value(editor, "currentIndex"))]),
                    s.c.Qt.EditRole,
                )

        delegate = s.keep("delegate", Delegate(view))
        delegate.setItemEditorFactory(factory)
        view.setItemDelegateForColumn(1, delegate)
        return s.h
