# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/bcfa5de0140286d5.md
# this_file: Scripts/Widgets/Rich Text Component.py

"""Show rich text component using FontLab PythonQt; no font data is changed."""
from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Rich text component") as s:
        s.vertical()
        view = s.keep("text", s.g.QTextEdit(s.window))
        s.add(view)
        view.setReadOnly(True)
        view.setHtml(
            "<h1>A small reading room</h1><p><b>Bold</b> ideas and <i>quiet</i> details.</p><ul><li>One useful example</li><li>A second observation</li></ul>"
        )
        s.state.update(zoom=0, author="Example author", notifications=[])

        def zoom(n):
            n = max(-10, min(30, int(n)))
            delta = n - s.state["zoom"]
            view.zoomIn(delta)
            s.state["zoom"] = n
            s.state["notifications"].append(n)

        s.keep("set_zoom", zoom)
        s.keep("reset_zoom", lambda: zoom(0))
        s.keep("set_author", lambda text: s.state.update(author=str(text)))
        s.keep("reset_author", lambda: s.state.update(author="Example author"))
        return s.h


def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_pydemo-bcfa5de0140286d5', 'Rich Text Component')


if __name__ == "__main__":
    main()
