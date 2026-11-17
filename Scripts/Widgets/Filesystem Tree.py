# this_file: Scripts/Widgets/Filesystem Tree.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/12 QTreeView example in Python/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
"""Show filesystem tree using FontLab PythonQt; no font data is changed."""
from pathlib import Path
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    view = qt.QtGui.QTreeView()
    model = qt.QtGui.QDirModel(view)
    home = str(Path.home())
    view.setModel(model)
    view.setRootIndex(model.index(home))
    handle = ExampleHandle(
        view,
        lambda: {
            "root_path": str(model.filePath(view.rootIndex())),
            "row_count": int(model.rowCount(view.rootIndex())),
            "column_count": int(model.columnCount(view.rootIndex())),
        },
    )
    handle.model = model
    return handle



def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_main-f5bf995791f1e87b', 'Filesystem Tree')


if __name__ == "__main__":
    main()

# ## MIT License
# 
# Upstream authorship attribution: Michael Herrmann. No copyright year or notice
# appears in the reviewed original files; none is inferred here.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
