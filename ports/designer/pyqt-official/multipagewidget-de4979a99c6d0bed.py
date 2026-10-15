# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/de4979a99c6d0bed.md
# this_file: ports/designer/pyqt-official/multipagewidget-de4979a99c6d0bed.py

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
    with S.Session(qt, "Multiple pages") as s:
        s.vertical()
        choice = s.combo("selector", [])
        stack = s.keep("stack", s.g.QStackedWidget(s.window))
        s.add(stack)
        pages = []
        busy = [False]
        s.state["notifications"] = []

        def snapshot():
            s.state.update(
                count=len(pages),
                index=int(S.value(stack, "currentIndex")),
                titles=[p[0] for p in pages],
            )
            s.state["notifications"].append(s.state["index"])

        def select(index):
            if 0 <= int(index) < len(pages):
                stack.setCurrentIndex(index)
                if not busy[0]:
                    busy[0] = True
                    choice.setCurrentIndex(index)
                    busy[0] = False
                snapshot()
                return True
            return False

        def insert(index, title):
            if not 0 <= index <= len(pages):
                return False
            page = s.g.QLabel(str(title), stack)
            pages.insert(index, [str(title), page])
            stack.insertWidget(index, page)
            choice.insertItem(index, str(title))
            snapshot()
            return True

        def remove(index):
            if not 0 <= index < len(pages):
                return False
            _title, page = pages.pop(index)
            stack.removeWidget(page)
            choice.removeItem(index)
            page.deleteLater()
            snapshot()
            return True

        def rename(index, title):
            if not 0 <= index < len(pages):
                return False
            pages[index][0] = str(title)
            pages[index][1].setText(str(title))
            choice.setItemText(index, str(title))
            snapshot()
            return True

        s.link(choice, "currentIndexChanged(int)", select)
        insert(0, "First reading")
        insert(1, "Second reading")
        select(0)
        for key, fn in [
            ("insert", insert),
            ("remove", remove),
            ("rename", rename),
            ("set_index", select),
        ]:
            s.keep(key, fn)
        return s.h
