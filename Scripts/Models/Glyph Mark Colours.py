# this_file: Scripts/Models/Glyph Mark Colours.py
# SPDX-License-Identifier: Apache-2.0
"""What: Edit glyph mark colours in a table of the current FontLab font.
How: Capture scalar glyph identities and marks through App names_edit. Each
colour cell uses a combo delegate with FontLab hue and grey presets. Apply
rechecks the current font and original values, then calls App history.commit
with metadata policy for only changed rows. One Apply creates one Undo step.
Why: Native marks persist with the font and support FontLab colour selection.
Usage: Open a font, double-click colour cells, choose marks and click Apply.
Use Discard Changes to restore local edits. Glyphs with auto layers are refused.
Benefit: Review many glyph marks without changing names, notes or outlines.
Requires: FontLab 9, Python 3.11, Fly and App names_edit, history, draft_signals
and qt_properties. Failed writes retain the local plan and show Undo guidance.

Independent rewrite of the Qt coloreditorfactory example idea. Based on the author's own FontLab sample,
Apache-2.0.
Source: rescued/part2/ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py
SHA256: 06780068bb97fb0b0787dbc5fc5dc5d51b1c2c29cfd053fa0ba6be4be802ce58
Source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/coloreditorfactory-0a3b15766909bdc3.py
SHA256: 5b4aa3c5c7aaad2b40cb25c868c6aa41f828dbc884021db9fd2d630f5cd64534
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

Rows = tuple[tuple[str, ...], ...]
_PANELS: list[Any] = []


def checked(text: str) -> str:
    """Refuse characters which PythonQt can replace during text conversion."""
    for char, name in (
        ("\0", "NUL"),
        ("\r", "CR"),
        ("\u00a0", "NBSP; replace with a normal space"),
        ("\u2028", "line separator"),
        ("\u2029", "paragraph separator"),
    ):
        if char in text:
            raise ValueError(f"Refuse {name} in text.")
    text.encode("utf-8")
    return text


TITLE = "Glyph Mark Colours"
HEADERS = ("Glyph name", "Mark colour")
HELP = "Open a font, double-click colour cells, choose marks and click Apply."


CHOICES = (
    ("None", 0),
    ("Red", 1),
    ("Orange", 31),
    ("Yellow", 56),
    ("Green", 121),
    ("Teal", 171),
    ("Blue", 211),
    ("Purple", 271),
    ("Pink", 321),
    ("Grey", 1128),
)


def valid_mark(value: int) -> int:
    """Accept FontLab's unmarked, hue and grey mark domains."""
    if type(value) is not int or not (
        value == 0 or 1 <= value <= 360 or 1000 <= value <= 1255
    ):
        raise ValueError("Use a FontLab mark: 0, 1-360 or 1000-1255.")
    return value


def mark_label(value: int) -> str:
    """Keep the numeric value explicit when the colour is not a named preset."""
    return {number: label for label, number in CHOICES}.get(value, f"Mark {value}")


def capture_metadata() -> tuple[int, dict[str, tuple[int, int]]]:
    """Read scalar identities and mark values; retain no native glyph handles."""
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - use the lazy Fly module alias

    facts = names_edit.scan()
    return facts.package_id, {
        name: (int(entry.record.id), int(entry.glyph.mark or 0))
        for name, entry in facts.entries.items()
    }


def apply_changes(
    package_id: int, baseline: dict[str, tuple[int, int]], desired: dict[str, int]
) -> tuple[str, ...]:
    """Commit changed rows once; refuse switched, replaced or externally edited glyphs."""
    import fly.ap.history as history  # noqa: PLR0402 - use the lazy Fly module alias
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - use the lazy Fly module alias

    facts = names_edit.fresh_facts(package_id)
    todo = []
    for name, value in desired.items():
        try:
            valid_mark(value)
        except ValueError as error:
            raise ValueError(f"{name}: {error}") from error
        if name not in baseline or name not in facts.entries:
            raise ValueError(f"{name} is no longer in the captured font; Refresh.")
        entry = facts.entries[name]
        glyph_id, original = baseline[name]
        if int(entry.record.id) != glyph_id or int(entry.glyph.mark or 0) != original:
            raise ValueError(f"{name} changed since capture; Refresh before Apply.")
        if value != original:
            todo.append((entry, value))
    if not todo:
        return ()
    glyphs = [entry.glyph for entry, _value in todo]
    layers = [layer for glyph in glyphs for layer in glyph.layers]

    def mutate() -> None:
        """Set only the planned native metadata fields after history preflight."""
        for entry, value in todo:
            entry.glyph.mark = value

    def read_back() -> tuple[str, ...]:
        """Escalate a failed native read-back with the shared Undo recovery hint."""
        for entry, value in todo:
            if int(entry.glyph.mark or 0) != value:
                raise RuntimeError(f"{entry.name}: native mark does not match Apply.")
        return ()

    history.commit(
        TITLE,
        layers,
        glyphs,
        mutate,
        operation="metadata",
        facts=facts.autos,
        read_back=read_back,
    )
    return tuple(entry.name for entry, _value in todo)


def delegate_type(qt: Any) -> type:
    """Use a native combo editor and an explicit cell-change callback."""
    import fly.ap.qt_properties as properties

    gui = qt.QtGui

    class ChoiceDelegate(gui.QStyledItemDelegate):
        """Keep active editor values available to Apply and safe Close."""

        def __init__(self, owner: Any) -> None:
            gui.QStyledItemDelegate.__init__(self, owner)
            self.owner_panel = owner
            self.active_editor: Any = None
            self.active_index: Any = None

        def createEditor(self, parent: Any, option: Any, index: Any) -> Any:
            """Let Qt create, place and destroy the ordinary combo editor."""
            editor = gui.QComboBox(parent)
            for label, value in CHOICES:
                editor.addItem(label, value)
            self.active_editor, self.active_index = editor, index
            return editor

        def setEditorData(self, editor: Any, index: Any) -> None:
            """Restore the row's value, including a non-preset native mark."""
            current = self.owner_panel.cell_value(index.row())
            found = editor.findData(current)
            if found < 0:
                editor.addItem(f"Mark {current}", current)
                found = editor.findData(current)
            editor.setCurrentIndex(found)

        def submit_editor(self, editor: Any, index: Any) -> None:
            """Read the combo at explicit action boundaries; permit guarded refusal."""
            if not self.owner_panel.scope.closed:
                number = int(properties.value(editor, "currentIndex"))
                self.owner_panel.change_cell(index.row(), editor.itemData(number))

        def setModelData(self, editor: Any, model: Any, index: Any) -> None:
            """Contain a native delegate callback failure in the panel status."""
            try:
                self.submit_editor(editor, index)
            except Exception as error:  # noqa: BLE001 - native delegate boundary
                self.owner_panel.status_line.setText(str(error))

        def reset_editor(self) -> None:
            """Reset an open combo after Discard so late editor closure stays inert."""
            if self.active_editor is not None:
                self.setEditorData(self.active_editor, self.active_index)

        def flush(self) -> None:
            """Capture a still-open combo before Apply, export, refresh or Close."""
            if self.active_editor is not None:
                self.submit_editor(self.active_editor, self.active_index)

        def destroyEditor(self, editor: Any, index: Any) -> None:
            """Drop Python references before Qt releases the native editor."""
            try:
                if not self.owner_panel.scope.closed:
                    self.setModelData(editor, None, index)
            except Exception as error:  # noqa: BLE001 - native delegate boundary
                self.owner_panel.status_line.setText(str(error))
            finally:
                self.active_editor = self.active_index = None
                gui.QStyledItemDelegate.destroyEditor(self, editor, index)

    return ChoiceDelegate


def show(qt: Any, parent: Any = None, capture: Callable[[], Any] | None = None) -> Any:
    """Open through the existing host. Keep exact callback and model owners."""
    import fly.ap.draft_signals as signals

    if capture is None:
        capture = capture_metadata
    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own controls and stage captures before replacing visible results."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.snapshot: Rows = ()
            self.owned_model: Any = None
            self.editor_delegate: Any = None
            self.dirty = False
            self.capture_font = capture
            self.package_id: int | None = None
            self.baseline: dict[str, tuple[int, int]] = {}
            self.changed: dict[str, int] = {}
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(820, 540)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(16, 16, 16, 16)
            self.stack.setSpacing(8)
            self.status_line = gui.QLabel(HELP, self)
            self.status_line.setTextFormat(core.Qt.PlainText)
            self.status_line.setWordWrap(True)
            self.stack.addWidget(self.status_line)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def populate(self) -> None:
            """Connect only after the module retains this window for cleanup."""
            self.scope.connect(
                self.destroyed,
                lambda *args: self.destroyed_owner(),
                closing=True,
                retry=True,
            )
            self.table_view = gui.QTableView(self)
            self.stack.addWidget(self.table_view)
            self.action_strip = gui.QHBoxLayout()
            self.stack.addLayout(self.action_strip)
            self.editor_delegate = delegate_type(qt)(self)
            self.table_view.setItemDelegateForColumn(1, self.editor_delegate)
            self.button("Refresh", self.refresh)
            self.button("Apply", self.apply)
            self.button("Discard Changes", self.discard_changes)
            self.button("Close", lambda: self.close(), closing=True)

        def button(
            self, label: str, action: Callable[[], Any], *, closing: bool = False
        ) -> None:
            """Own a plain callback that accepts native clicked(bool)."""
            control = gui.QPushButton(label, self)
            self.action_strip.addWidget(control)
            self.scope.connect(
                control.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def stage(self, display: Rows) -> Any:
            """Build one model per capture. Cell edits never call this function."""
            model = gui.QStandardItemModel(self)
            try:
                model.setHorizontalHeaderLabels(list(HEADERS))
                for row in display:
                    cells = []
                    for column, text in enumerate(row):
                        item = gui.QStandardItem(checked(text))
                        item.setEditable(column == 1)
                        cells.append(item)
                    model.appendRow(cells)
            except Exception:
                model.deleteLater()
                raise
            return model

        def install(self, model: Any) -> None:
            """Swap a complete model, then release its obsolete selection owner."""
            old = self.owned_model
            selection = self.table_view.selectionModel()
            self.table_view.setModel(model)
            self.owned_model = model
            if selection is not None:
                selection.deleteLater()
            if old is not None:
                old.deleteLater()

        def refresh(self) -> None:
            """Refuse pending edits; read a new scalar native mark snapshot."""
            self.editor_delegate.flush()
            if self.dirty:
                raise ValueError("Apply or Discard Changes before Refresh.")
            package_id, baseline = self.capture_font()
            rows = tuple(
                (name, mark_label(value))
                for name, (_glyph_id, value) in baseline.items()
            )
            model = self.stage(rows)
            self.install(model)
            self.package_id, self.baseline = package_id, baseline
            self.snapshot = rows
            self.changed = {}
            self.status_line.setText(
                f"{len(rows)} glyph marks loaded. Double-click a colour cell."
            )

        def cell_value(self, row: int) -> int:
            """Read the local intended mark, falling back to the captured mark."""
            name = self.snapshot[row][0]
            return self.changed.get(name, self.baseline[name][1])

        def change_cell(self, row: int, value: int) -> None:
            """Record a combo edit and update that row's existing colour item."""
            if value == self.cell_value(row):
                return
            name = self.snapshot[row][0]
            try:
                value = valid_mark(value)
            except ValueError as error:
                raise ValueError(f"{name}: {error}") from error
            if value == self.baseline[name][1]:
                self.changed.pop(name, None)
            else:
                self.changed[name] = value
            self.owned_model.item(row, 1).setText(mark_label(value))
            self.dirty = bool(self.changed)

        def apply(self) -> None:
            """Write changed rows through one metadata history operation."""
            self.editor_delegate.flush()
            try:
                changed = apply_changes(self.package_id, self.baseline, self.changed)
            except ValueError as error:
                raise ValueError(
                    f"Whole Apply refused; no glyphs were changed. {error}"
                ) from error
            for name in changed:
                self.baseline[name] = (self.baseline[name][0], self.changed[name])
            self.changed.clear()
            self.dirty = False
            self.editor_delegate.reset_editor()
            self.status_line.setText(
                f"Applied {len(changed)} glyph mark changes in one Undo step."
                if changed
                else "No changed marks."
            )

        def discard_changes(self) -> None:
            """Restore only edited cells; keep the existing model and native font."""
            for row, (name, _label) in enumerate(self.snapshot):
                if name in self.changed:
                    self.owned_model.item(row, 1).setText(
                        mark_label(self.baseline[name][1])
                    )
            self.changed.clear()
            self.dirty = False
            self.editor_delegate.reset_editor()

        def destroyed_owner(self) -> None:
            """Fence retained callbacks when the native parent destroys the panel."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Contain cleanup failures and retain ownership for a Close retry."""
            try:
                if self.editor_delegate is not None:
                    self.editor_delegate.flush()
                if self.dirty:
                    self.status_line.setText(
                        "Unapplied changes. Apply or Discard Changes before Close."
                    )
                    event.ignore()
                    return
                if not self.scope.finish():
                    event.ignore()
                    return
                if hasattr(self, "table_view"):
                    self.table_view.setItemDelegate(None)
                    self.table_view.setModel(None)
                if self.owned_model is not None:
                    self.owned_model.deleteLater()
                    self.owned_model = None
            except Exception as error:  # noqa: BLE001 - contain native cleanup errors
                self.status_line.setText(f"Close paused: {error}. Retry window Close.")
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.populate()
    except Exception:
        panel.dirty = False
        panel.close()
        raise
    try:
        panel.refresh()
    except (ValueError, RuntimeError, TimeoutError) as error:
        panel.status_line.setText(str(error))
    panel.show()
    return panel


def main() -> None:
    """Use FontLab's application, main window and lazy Fly namespaces."""
    from fly import fl, qt

    show(qt, fl.MainWindow())


if __name__ == "__main__":
    main()
