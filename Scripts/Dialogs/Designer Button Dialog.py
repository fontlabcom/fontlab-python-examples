# this_file: Scripts/Dialogs/Designer Button Dialog.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann's pyqt/examples, src/05 Qt Designer Python/main.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for exact provenance.
"""Load an inline Designer UI and its OK/Cancel connections via QUiLoader."""

from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle


def _load(qt: Any) -> Any:
    from PythonQt import QtUiTools

    source = qt.QtCore.QBuffer()
    source.setData(qt.QtCore.QByteArray(UI.encode("utf-8")))
    loader = None
    try:
        loader = QtUiTools.QUiLoader()
        if not source.open(qt.QtCore.QIODevice.ReadOnly):
            raise OSError(
                f"Cannot open Designer UI: {source.errorString()}"
            )
        window = loader.load(source)
        if window is None:
            raise RuntimeError(f"Cannot load Designer UI: {loader.errorString()}")
        return window
    finally:
        source.close()
        source.deleteLater()
        if loader is not None:
            loader.deleteLater()


def build(qt: Any) -> ExampleHandle:
    window = _load(qt)
    handle = ExampleHandle(window, lambda: {"result": int(window.result())})
    try:
        window.setModal(False)
        handle.connect(window.finished, lambda *args: window.window().close())
    except BaseException:
        handle.close()
        raise
    return handle


# Authored equivalent UI: the historical asset has no SPDX header.
UI = '<ui version="4.0">\n <class>ButtonDialog</class>\n <widget class="QDialog" name="ButtonDialog">\n  <property name="windowTitle"><string>Designer Button Dialog</string></property>\n  <layout class="QVBoxLayout" name="layout">\n   <item><widget class="QDialogButtonBox" name="buttons">\n    <property name="standardButtons"><set>QDialogButtonBox::Cancel|QDialogButtonBox::Ok</set></property>\n   </widget></item>\n  </layout>\n </widget>\n <connections>\n  <connection><sender>buttons</sender><signal>accepted()</signal><receiver>ButtonDialog</receiver><slot>accept()</slot></connection>\n  <connection><sender>buttons</sender><signal>rejected()</signal><receiver>ButtonDialog</receiver><slot>reject()</slot></connection>\n </connections>\n</ui>'


def main():
    """Open this retained, parented PythonQt demo."""
    from fontlab_python_lessons.qt_demos import launch
    return launch(build, 'restored_designer_dialog', 'Designer Button Dialog')


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
