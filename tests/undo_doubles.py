# this_file: tests/undo_doubles.py
"""QUndoStack owns commands and invokes overrides; in PythonQt index()/count() are methods, canUndo/canRedo properties."""

from qt_doubles import Signal, native_double


def undo_types(qt, widget):
    @native_double
    class Command:
        def __init__(self, text):
            self.text = text
            self.deleted = False

        def undo(self):
            pass

        def redo(self):
            pass

    @native_double
    class Stack(widget):
        def __init__(self, parent):
            super().__init__(parent)
            del self.count
            self.indexChanged = Signal()
            self.commands, self._index = [], 0
            self.clear_count = 0

        def index(self):
            return self._index

        @property
        def canUndo(self):
            return self._index > 0

        @property
        def canRedo(self):
            return self._index < len(self.commands)

        def count(self):
            return len(self.commands)

        def push(self, command):
            for old in self.commands[self._index :]:
                old.deleted = True
            del self.commands[self._index :]
            command.redo()
            self.commands.append(command)
            self._index += 1
            self.indexChanged.emit(self._index)

        def undo(self):
            if self.canUndo:
                self._index -= 1
                self.commands[self._index].undo()
                self.indexChanged.emit(self._index)

        def redo(self):
            if self.canRedo:
                self.commands[self._index].redo()
                self._index += 1
                self.indexChanged.emit(self._index)

        def clear(self):
            assert not self.indexChanged.callbacks, (
                "Disconnect stack before deleting commands"
            )
            self.clear_count += 1
            for command in self.commands:
                command.deleted = True
            self.commands.clear()
            self._index = 0

    return Command, Stack
