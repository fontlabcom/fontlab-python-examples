# this_file: Scripts/Insights/Metrics Undo.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/RobotLocomotion_director/src/python/director/mainwindowapp.py:444
"""Demonstrate metrics undo with owned sample data and modeless UI.

Setup: FontLab 9, Fly App and fontlab-python-lessons. No open font is required.
"""
from typing import Any

from fontlab_python_lessons.qt_demos import ExampleHandle
from fontlab_python_lessons import qt_demos as S


def build(qt: Any) -> ExampleHandle:
    stack_type = qt.QtGui.QUndoStack
    command_type = qt.QtGui.QUndoCommand
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

    with S.Session(qt, "Undo sample glyph metrics", gui.QWidget()) as session:
        handle = session.h
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
            value = int(S.value(advance, "value"))
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
        handle.connect_old(undo, "clicked()", lambda *args: stack.undo())
        handle.connect_old(redo, "clicked()", lambda *args: stack.redo())
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
            "index": int(stack.index()),  # a method in PythonQt; canUndo/canRedo are properties
            "can_undo": bool(S.value(stack, "canUndo")),
            "can_redo": bool(S.value(stack, "canRedo")),
            "text": str(S.value(label, "text")),
        }
        return handle


def main():
    """Open the retained modeless example; no FontLab data is changed."""
    return S.launch(build, "restored_insights_metrics-undo", "Metrics Undo")


if __name__ == "__main__":
    main()
