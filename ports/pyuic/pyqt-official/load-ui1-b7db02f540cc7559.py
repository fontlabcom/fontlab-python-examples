# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b7db02f540cc7559.md
# this_file: ports/pyuic/pyqt-official/load-ui1-b7db02f540cc7559.py
"""Independent FontLab example with an explicitly owned lifetime."""

from contextlib import contextmanager

from fontlab_python_examples.handle import ExampleHandle


def value(obj, name):
    item = getattr(obj, name)
    return item() if callable(item) else item


@contextmanager
def owned(qt, title):
    state = {"closing": False}

    class Window(qt.QtGui.QWidget):
        def closeEvent(self, event):
            if not state["closing"]:
                handle.close()
            event.accept()

    window = Window()
    handle = ExampleHandle(window, dict)
    handle.cleanup.append(lambda: state.update(closing=True))
    try:
        window.setWindowTitle(title)
        window.setAttribute(qt.QtCore.Qt.WA_QuitOnClose, False)
        window.resize(760, 540)
        layout = qt.QtGui.QVBoxLayout(window)
        handle.controls["layout"] = layout
        yield handle, layout
    except BaseException:
        handle.close()
        raise


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
    with owned(qt, "Owned word list") as (handle, layout):
        items = qt.QtGui.QListWidget(handle.widget)
        layout.addWidget(items)
        handle.controls["items"] = items
        button(qt, handle, layout, "Add", lambda: None)
        button(qt, handle, layout, "Clear", items.clear)
        button(qt, handle, layout, "OK", handle.close)
        handle.inspect_ui = lambda: {"count": int(value(items, "count"))}
        return handle
