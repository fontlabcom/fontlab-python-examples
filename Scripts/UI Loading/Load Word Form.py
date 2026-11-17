# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b7db02f540cc7559.md
# this_file: Scripts/UI Loading/Load Word Form.py
"""Load Word Form. Setup: FontLab 9, Fly App and Lessons; no font needed."""


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
        items = qt.QtGui.QListWidget(handle.widget)
        layout.addWidget(items)
        handle.controls["items"] = items
        button(qt, handle, layout, "Add", lambda: items.addItems(list(WORDS)))
        button(qt, handle, layout, "Clear", items.clear)
        button(qt, handle, layout, "OK", handle.close)
        handle.inspect_ui = lambda: {"count": int(value(items, "count"))}
        return handle


def main():
    """Open a retained modeless menu demonstration in FontLab."""
    return S.launch(build, 'restored_load-ui1-b7db02f540cc7559', 'Load Word Form')


if __name__ == "__main__":
    main()
