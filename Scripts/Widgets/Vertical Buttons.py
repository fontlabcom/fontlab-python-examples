# this_file: Scripts/Widgets/Vertical Buttons.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/03 QVBoxLayout PyQt6/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Original two buttons, arranged Top then Bottom in QVBoxLayout."""

from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    window = qt.QtGui.QWidget()
    buttons = []
    handle = ExampleHandle(
        window, lambda: {"buttons": [str(item.text) for item in buttons]}
    )
    try:
        layout = qt.QtGui.QVBoxLayout(window)
        for text in ("Top", "Bottom"):
            button = qt.QtGui.QPushButton(text, window)
            buttons.append(button)
            layout.addWidget(button)
    except BaseException:
        handle.close()
        raise
    return handle



def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_main-f5ddfd0eaacbf845', 'Vertical Buttons')


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
