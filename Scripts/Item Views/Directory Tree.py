# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/4b8851287931abd0.md
# this_file: Scripts/Item Views/Directory Tree.py

"""Directory Tree: modeless PythonQt demonstration; no font data is changed."""

from fontlab_python_lessons import qt_demos as S


def build(qt):
    with S.Session(qt, "Deferred sample directory") as s:
        s.vertical()
        s.state.update(loading=True, root=None)
        # Do not attach QFileSystemModel until the owned directory exists.
        tree = s.keep("tree", s.g.QTreeView(s.window))
        s.add(tree)

        def initialize():
            root = s.temp()
            (root / "notes.txt").write_text("One small directory fixture.\n")
            model = s.keep("model", s.g.QFileSystemModel(s.window))
            model.setReadOnly(True)
            index = model.setRootPath(str(root))
            tree.setModel(model)
            tree.setRootIndex(index)
            tree.setSortingEnabled(True)
            s.h.model = model
            s.state.update(loading=False, root=str(root))

        s.h.release.append(
            lambda: tree.setModel(None) if not s.h.owner.closed else None
        )
        s.timer("load_timer", 0, initialize, single=True)
        s.keep("initialize", initialize)
        return s.h


def main():
    """Open this example through the retained App dialog owner."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_dirview-4b8851287931abd0', 'Directory Tree')


if __name__ == "__main__":
    main()
