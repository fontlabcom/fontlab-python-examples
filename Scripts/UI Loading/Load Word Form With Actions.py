# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b9660f4ee653ca01.md
# this_file: Scripts/UI Loading/Load Word Form With Actions.py
"""Load Word Form With Actions. Setup: FontLab 9, Fly App and Lessons; no font needed."""


from fontlab_python_lessons import qt_demos as S


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


def wire(handle, obj, signature, callback):
    def receive(*args):
        if not handle.owner.closed:
            callback(*args)

    handle.connect_old(obj, signature, receive)
    return receive


def button(qt, handle, layout, name, callback):
    item = qt.QtGui.QPushButton(name, handle.widget)
    layout.addWidget(item)
    handle.controls[name] = item
    wire(handle, item, "clicked()", lambda *args: callback())
    return item


WORDS = ("amber", "birch", "cloud", "dawn")


def build(qt):
    with S.Session(qt, "Owned word list") as session:
        handle, layout = session.h, session.vertical()
        # QUiLoader consumes a native QBuffer, never a generated binding class.
        data = b'<ui version="4.0"><class>WordForm</class><widget class="QDialog" name="WordForm"><layout class="QVBoxLayout" name="layout"><item><widget class="QListWidget" name="words"/></item></layout></widget><resources/><connections/></ui>'
        buffer = qt.QtCore.QBuffer(handle.widget)
        buffer.setData(qt.QtCore.QByteArray(data))
        buffer.open(qt.QtCore.QIODevice.ReadOnly)
        ui = getattr(qt, "QtUiTools", None)
        if ui is None:
            from PythonQt import QtUiTools as ui
        loader = ui.QUiLoader()
        try:
            form = loader.load(buffer, handle.widget)
            if form is None:
                raise RuntimeError("Unable to load the owned word form")
            layout.addWidget(form)
            items = form.findChild(qt.QtGui.QListWidget, "words")
            if items is None:
                raise RuntimeError("Owned form has no word list")
        finally:
            buffer.close()
            loader.deleteLater()
        handle.controls["items"] = items
        button(qt, handle, layout, "Add", lambda: items.addItems(list(WORDS)))
        button(qt, handle, layout, "Clear", items.clear)
        button(qt, handle, layout, "OK", handle.close)
        handle.inspect_ui = lambda: {"count": int(value(items, "count"))}
        return handle


def main():
    """Open a retained modeless menu demonstration in FontLab."""
    return S.launch(build, 'restored_load-ui2-b9660f4ee653ca01', 'Load Word Form With Actions')


if __name__ == "__main__":
    main()
