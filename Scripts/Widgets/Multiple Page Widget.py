# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/de4979a99c6d0bed.md
# this_file: Scripts/Widgets/Multiple Page Widget.py

"""Show multiple page widget using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


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


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_multipagewidget-de4979a99c6d0bed', 'Multiple Page Widget')


if __name__ == "__main__":
    main()
