# this_file: Scripts/Models/Glyph Review Form.py
# SPDX-License-Identifier: Apache-2.0
"""What: Save a review state and note in the current font's native glyph notes.
How: Map an Unset/Todo/Review/Done combo and a literal note field to one table row with
QDataWidgetMapper. Apply submits only that row, checks the captured glyph id
and original note, then commits metadata through App history.commit.
Why: Native notes travel with the font; existing free-form notes stay intact
until the user explicitly applies a review state. Auto-layer glyphs are refused.
Usage: Choose a row, select its state, enter a note and click Apply. Apply or
Discard Changes before switching rows or closing. Each Apply is one Undo step.
Benefit: Keep review decisions with the glyphs rather than in a separate draft.
Requires: FontLab 9, Python 3.11, Fly and App names_edit, history, draft_signals
and qt_properties. Native read-back failures show the Edit > Undo recovery.

Independent rewrite of the Qt simplewidgetmapper and combowidgetmapper example idea. Based on the author's own FontLab sample,
Apache-2.0.
Historical source: rescued/part2/ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py
SHA256: b6cda27a2fdd03bd8cbfe3604df3e2b4e7f89dbb378d331ba8465d57291902c7
Historical source: rescued/part2/ports/itemviews/pyqt-official/simplewidgetmapper-39de33366209402d.py
SHA256: 610a6d9f48c31599b43c8bd5eecf4686d6cfd5e2915c8cd76d91a65b3248f1a9
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/simplewidgetmapper-39de33366209402d.py
SHA256: fae480ee8369b1fd438007ad15563eacaa22313496ffff7bebd93cb574840ae9
Historical source: rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/combowidgetmapper-cc95f9719b8e4eda.py
SHA256: 741f446ef14303840be12852cc2b9383eb5ccd716c894ebff21dfc95aa6d44d9
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


TITLE = "Glyph Review Form"
HEADERS = ("Glyph name", "State", "Note")
HELP = "Choose an editable row, set its state and note, then Apply. Use Unset to keep free text or clear a note."


STATES = ("Unset", "Todo", "Review", "Done")


def split_note(text: str) -> tuple[str, str]:
    """Decode review notes; show a free-form or empty note with state Unset."""
    checked(text)
    if text in STATES[1:]:
        return text, ""
    state, separator, note = text.partition(":")
    if separator and state in STATES[1:]:
        return state, note.removeprefix(" ")
    return "Unset", text


def compose_note(state: str, note: str) -> str:
    """Store a bare state for an empty note; Unset permits plain text and clearing."""
    if state not in STATES:
        raise ValueError("Choose Unset, Todo, Review or Done.")
    checked(note)
    if state == "Unset":
        return note
    return state if not note else state + ": " + note


def display_note(name: str, text: str) -> tuple[str, str]:
    """Replace unsafe display text with a named reason, retaining raw data in Python."""
    try:
        return split_note(text)
    except ValueError as error:
        return "Read-only", f"{name}: note has unsupported characters. {error}"


def capture_metadata() -> tuple[int, dict[str, tuple[int, str]]]:
    """Read scalar identities and note values; retain no native glyph handles."""
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - use the lazy Fly module alias

    facts = names_edit.scan()
    return facts.package_id, {
        name: (int(entry.record.id), str(entry.glyph.note or ""))
        for name, entry in facts.entries.items()
    }


def apply_changes(
    package_id: int, baseline: dict[str, tuple[int, str]], desired: dict[str, str]
) -> tuple[str, ...]:
    """Commit changed rows once; refuse switched, replaced or externally edited glyphs."""
    import fly.ap.history as history  # noqa: PLR0402 - use the lazy Fly module alias
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - use the lazy Fly module alias

    facts = names_edit.fresh_facts(package_id)
    todo = []
    for name, value in desired.items():
        # Unsafe source notes are inspection-only. Never sanitize and overwrite them.
        if name in baseline:
            try:
                checked(baseline[name][1])
            except ValueError:
                continue
        checked(value)
        if name not in baseline or name not in facts.entries:
            raise ValueError(f"{name} is no longer in the captured font; Refresh.")
        entry = facts.entries[name]
        glyph_id, original = baseline[name]
        if int(entry.record.id) != glyph_id or str(entry.glyph.note or "") != original:
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
            entry.glyph.note = value

    def read_back() -> tuple[str, ...]:
        """Escalate a failed native read-back with the shared Undo recovery hint."""
        for entry, value in todo:
            if str(entry.glyph.note or "") != value:
                raise RuntimeError(f"{entry.name}: native note does not match Apply.")
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


def show(qt: Any, parent: Any = None, capture: Callable[[], Any] | None = None) -> Any:
    """Open through the existing host. Keep exact callback and model owners."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    if capture is None:
        capture = capture_metadata
    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own controls and stage captures before replacing visible results."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.snapshot: Rows = ()
            self.owned_model: Any = None
            self.loading = False
            self.dirty = False
            self.capture_font = capture
            self.package_id: int | None = None
            self.baseline: dict[str, tuple[int, str]] = {}
            self.current_row = 1
            self.blocked: dict[str, str] = {}
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
            self.table_view.setEditTriggers(gui.QAbstractItemView.NoEditTriggers)
            self.row_number = gui.QSpinBox(self)
            self.stack.addWidget(self.row_number)
            self.state_choice = gui.QComboBox(self)
            self.state_choice.addItems(list(STATES))
            self.stack.addWidget(self.state_choice)
            self.note_field = gui.QPlainTextEdit(self)
            self.stack.addWidget(self.note_field)
            self.mapper = gui.QDataWidgetMapper(self)
            self.mapper.setSubmitPolicy(gui.QDataWidgetMapper.ManualSubmit)
            self.mapper.addMapping(
                self.state_choice, 1, core.QByteArray(b"currentText")
            )
            self.mapper.addMapping(self.note_field, 2, core.QByteArray(b"plainText"))
            self.scope.connect(
                self.row_number.valueChanged, lambda *args: self.navigate()
            )
            self.scope.connect(
                self.table_view.clicked,
                lambda index: self.row_number.setValue(index.row() + 1),
            )
            self.scope.connect(
                self.state_choice.currentIndexChanged, lambda *args: self.edited()
            )
            self.scope.connect(self.note_field.textChanged, lambda *args: self.edited())
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
                        item.setEditable(False)
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
            """Capture all notes. Keep unsafe notes as named, read-only rows."""
            if self.dirty:
                raise ValueError("Apply or Discard Changes before Refresh.")
            package_id, baseline = self.capture_font()
            rows = tuple(
                (name, *display_note(name, text))
                for name, (_glyph_id, text) in baseline.items()
            )
            blocked = {name: note for name, state, note in rows if state == "Read-only"}
            model = self.stage(rows)
            self.loading = True
            try:
                self.mapper.setModel(None)
                self.install(model)
                self.mapper.setModel(model)
                self.package_id, self.baseline, self.snapshot, self.blocked = (
                    package_id,
                    baseline,
                    rows,
                    blocked,
                )
                first = next(
                    (i + 1 for i, row in enumerate(rows) if row[0] not in blocked), 1
                )
                self.row_number.setRange(1, max(1, len(rows)))
                self.row_number.setValue(first)
                self.current_row = first
                self.load_row()
            finally:
                self.loading = False
            reasons = " ".join(blocked.values())
            self.status_line.setText(
                f"{len(rows)} native glyph notes loaded. " + reasons
            )

        def edited(self) -> None:
            """Track only edits to an eligible mapper row."""
            if (
                not self.loading
                and self.snapshot
                and self.snapshot[self.current_row - 1][0] not in self.blocked
            ):
                self.dirty = True

        def navigate(self) -> None:
            """Keep unapplied text; route eligible rows only to the mapper."""
            if self.loading:
                return
            number = int(properties.value(self.row_number, "value"))
            if self.dirty and number != self.current_row:
                self.row_number.setValue(self.current_row)
                raise ValueError("Apply or Discard Changes before changing rows.")
            self.current_row = number
            self.load_row()

        def load_row(self) -> None:
            """Disable unsafe rows without passing their native note through Qt."""
            self.loading = True
            try:
                name = self.snapshot[self.current_row - 1][0] if self.snapshot else ""
                eligible = bool(name) and name not in self.blocked
                self.state_choice.setEnabled(eligible)
                self.note_field.setEnabled(eligible)
                if eligible:
                    self.mapper.setCurrentIndex(self.current_row - 1)
                else:
                    self.mapper.setCurrentIndex(-1)
                    self.state_choice.setCurrentText("Unset")
                    self.note_field.setPlainText("")
                    self.status_line.setText(
                        "Read-only. " + self.blocked.get(name, "No glyphs to edit.")
                    )
            finally:
                self.loading = False

        def apply(self) -> None:
            """Submit one mapper row, then save its state and note in one Undo step."""
            if not self.snapshot:
                raise ValueError("Open a font and Refresh first.")
            if self.snapshot[self.current_row - 1][0] in self.blocked:
                self.status_line.setText(
                    "Read-only. " + self.blocked[self.snapshot[self.current_row - 1][0]]
                )
                return
            if not self.dirty:
                self.status_line.setText("No changed review note.")
                return
            row = self.current_row - 1
            name = self.snapshot[row][0]
            text = compose_note(
                str(properties.value(self.state_choice, "currentText")),
                str(properties.value(self.note_field, "toPlainText")),
            )
            if not self.mapper.submit():
                raise RuntimeError("Qt refused the review form submission.")
            changed = apply_changes(self.package_id, self.baseline, {name: text})
            if changed:
                self.baseline[name] = (self.baseline[name][0], text)
            self.dirty = False
            self.status_line.setText(
                "Review state and note saved in one Undo step."
                if changed
                else "No changed review note."
            )

        def discard_changes(self) -> None:
            """Restore only the current row and mapper controls from the native baseline."""
            if not self.snapshot:
                self.dirty = False
                return
            row = self.current_row - 1
            if self.snapshot[row][0] in self.blocked:
                self.dirty = False
                self.load_row()
                return
            state, note = split_note(self.baseline[self.snapshot[row][0]][1])
            self.loading = True
            try:
                self.owned_model.item(row, 1).setText(state)
                self.owned_model.item(row, 2).setText(note)
                self.mapper.revert()
            finally:
                self.loading = False
            self.dirty = False

        def destroyed_owner(self) -> None:
            """Fence retained callbacks when the native parent destroys the panel."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Contain cleanup failures and retain ownership for a Close retry."""
            try:
                if self.dirty:
                    self.status_line.setText(
                        "Unapplied changes. Apply or Discard Changes before Close."
                    )
                    event.ignore()
                    return
                if not self.scope.finish():
                    event.ignore()
                    return
                if hasattr(self, "mapper"):
                    self.mapper.setModel(None)
                if hasattr(self, "table_view"):
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
