# this_file: Scripts/Widgets/Hello Label.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/01 PyQt QLabel/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Original Hello World QLabel, using FontLab's existing application loop."""

from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    label = qt.QtGui.QLabel("Hello World!")
    return ExampleHandle(label, lambda: {"text": str(label.text)})



def main():
    """Open a parented, retained modeless example in FontLab."""
    from fontlab_python_lessons.qt_demos import launch

    return launch(build, 'restored_main-ce3e17a7a2a03a02', 'Hello Label')


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
