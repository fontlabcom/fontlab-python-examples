# this_file: ports/insights/metrics-undo.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/RobotLocomotion_director/src/python/director/mainwindowapp.py:444
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned, required


def build(qt: Any) -> ExampleHandle:
    stack_type = required(qt, "QtGui.QUndoStack")
    command_type = required(qt, "QtGui.QUndoCommand")
    gui = qt.QtGui
    state = {"advance": 600}

    class AdvanceCommand(command_type):
        """QUndoStack owns the command; callbacks modify only Python sample data."""

        def __init__(self, before: int, after: int) -> None:
            super().__init__(f"Advance {before} → {after}")
            self.before, self.after = before, after

        def undo(self) -> None:
            state["advance"] = self.before

        def redo(self) -> None:
            state["advance"] = self.after

    with owned(gui.QWidget(), "Undo sample glyph metrics") as handle:
        window = handle.widget
        advance = gui.QSpinBox(window)
        advance.setRange(0, 2000)
        advance.setValue(600)
        apply = gui.QPushButton("Apply sample advance", window)
        undo = gui.QPushButton("Undo", window)
        redo = gui.QPushButton("Redo", window)
        label = gui.QLabel("Advance: 600", window)
        layout = gui.QVBoxLayout(window)
        for control in (advance, apply, undo, redo, label):
            layout.addWidget(control)
        stack, commands = stack_type(window), []

        def update_label(*_args: Any) -> None:
            label.setText(f"Advance: {state['advance']}")

        def push() -> None:
            value = int(advance.value)
            if value == state["advance"]:
                return
            command = AdvanceCommand(state["advance"], value)
            commands.append(
                command
            )  # Retain Python virtual receivers while C++ owns them.
            stack.push(command)

        def release() -> None:
            if not handle.owner.closed:
                stack.clear()  # All explicit connections have already been disconnected.
            commands.clear()

        handle.connect_old(apply, "clicked()", push)
        handle.connect_old(undo, "clicked()", stack.undo)
        handle.connect_old(redo, "clicked()", stack.redo)
        handle.connect(stack.indexChanged, update_label)
        handle.release.append(release)
        handle.controls.update(
            advance=advance,
            apply=apply,
            undo=undo,
            redo=redo,
            stack=stack,
            status=label,
        )
        handle.inspect_ui = lambda: {
            **state,
            "count": int(stack.count()),
            "index": int(stack.index),
            "can_undo": bool(stack.canUndo),
            "can_redo": bool(stack.canRedo),
            "text": str(label.text),
        }
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("metrics-undo")
