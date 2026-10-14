# this_file: ports/insights/compiled-slot-exposure.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/RobotLocomotion_director/src/app/WrapPythonQt.py:71
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned, required


def build(qt: Any) -> ExampleHandle:
    point_type = required(qt, "QtCore.QPoint")
    required(qt, "QtGui.QLineEdit")
    gui = qt.QtGui
    with owned(gui.QWidget(), "Compiled wrappers and native slots") as handle:
        window = handle.widget
        entry = gui.QLineEdit(window)
        entry.setText("A.alt")
        move = gui.QPushButton("Call wrapped move(QPoint)", window)
        clear = gui.QPushButton("Invoke native clear() slot", window)
        stage = gui.QWidget(window)
        stage.setMinimumHeight(80)
        preview = gui.QLabel("Synthetic glyph A", stage)
        status = gui.QLabel("Only existing compiled bindings are used", window)
        layout = gui.QVBoxLayout(window)
        for control in (entry, move, clear, stage, status):
            layout.addWidget(control)
        try:
            meta = entry.metaObject()
            slot_index = meta.indexOfSlot("clear()")
            if slot_index < 0 or not callable(preview.move):
                raise AttributeError("clear() or move(QPoint)")
        except AttributeError as error:
            raise RuntimeError(
                "Host must expose QLineEdit metaObject/clear() and QWidget.move(QPoint)"
            ) from error
        state = {"moves": 0}

        def move_preview() -> None:
            state["moves"] += 1
            preview.move(point_type(20 * (state["moves"] % 3), 10))
            status.setText("Called a wrapped QWidget non-slot method")

        handle.connect_old(move, "clicked()", move_preview)
        handle.connect_old(clear, "clicked()", entry.clear)
        handle.controls.update(
            move=move, clear=clear, input=entry, preview=preview, status=status
        )
        handle.inspect_ui = lambda: {
            **state,
            "input": str(entry.text),
            "native_slot": "clear()",
            "slot_index": int(slot_index),
            "position": [int(preview.pos.x()), int(preview.pos.y())],
            "native_class": str(meta.className()),
            "compiled_here": False,
        }
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("compiled-slot-exposure")
