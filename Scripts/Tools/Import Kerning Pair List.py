# this_file: Scripts/Tools/Import Kerning Pair List.py
# SPDX-License-Identifier: Apache-2.0
"""What: Import many current-master kerning pairs from a pasted text list.
How: Read left right value lines; # begins a comment. Preview every row before
Apply. Decimal values round half away from zero to whole units. Invalid rows
block the entire batch. Duplicate pair lines require correction.
Why: A pair list can carry different values for many glyph and class pairs.
Usage: Open a font, paste the list, press Preview and inspect the table. Press
Apply for one Undo step. Edit the list and Preview again for another batch.
Benefit: Transfer measured pairs without creating glyphs or kerning classes.

@class names must already exist on the correct side of the current master's
kerning. Glyphs with automatic layers, including members of a named class,
are refused by the shared FontLab editing rules. Apply checks the font,
master, text and complete kerning snapshot again. Native read-back verifies
the written batch. Keep the panel open for repeated imports.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Based on the author's own FontLab sample, Apache-2.0.
Source: recipe.py (Kerning Pairs from Text).
"""

from __future__ import annotations

import math
from typing import Any

TITLE = "Import Kerning Pair List"
_PANELS: list[Any] = []


def parse_pairs(text: str) -> list[dict[str, Any]]:
    """Parse every non-comment row, retaining line numbers and row errors."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Text contains characters that Qt cannot preserve.")
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for line, source in enumerate(text.splitlines(), 1):
        content = source.split("#", 1)[0].strip()
        if not content:
            continue
        parts = content.split()
        row: dict[str, Any] = {
            "line": line,
            "left": "",
            "right": "",
            "value": None,
            "error": "",
        }
        try:
            if len(parts) != 3:
                raise ValueError("Expected left right value.")
            row["left"], row["right"] = parts[:2]
            value = float(parts[2])
            if not math.isfinite(value):
                raise ValueError("Value must be finite.")
            if abs(value) > 32767:
                raise ValueError("Value exceeds the pair-list range of +/-32767.")
            row["value"] = int(math.copysign(math.floor(abs(value) + 0.5), value))
            pair = (row["left"], row["right"])
            if pair in seen:
                raise ValueError("Repeated pair; keep one value per pair.")
            seen.add(pair)
        except ValueError as error:
            row["error"] = str(error)
        rows.append(row)
    return rows


def validate_row(
    package: Any,
    master: str,
    row: dict[str, Any],
    snapshot: Any,
    facts: Any,
    batch: Any,
    history: Any,
) -> None:
    """Use public App class-side, glyph-existence and auto-layer policies."""
    if row["error"]:
        raise ValueError(row["error"])
    pair = (row["left"], row["right"])
    groups = snapshot.groups[master]
    batch.validate_pair(package, master, pair, groups=groups)
    for side in pair:
        members = groups[side[1:]][0] if side.startswith("@") else (side,)
        for name in members:
            reason = history.refusal(facts, name, "metadata")
            if reason:
                raise ValueError(f"{name}: {reason}")


def prepare_pairs(text: str) -> dict[str, Any]:
    """Bind a complete row preview to current font, master and kerning values."""
    import fly.ap.history as history  # noqa: PLR0402 - preserve module imports
    import fly.ap.kerning_batch as batch
    import fly.ap.scripting as scripting  # noqa: PLR0402 - preserve module imports

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font first.")
    master = str(package.master)
    snapshot = batch.snapshot_kerning(package)
    facts = history.scan_auto_facts(package)
    rows = parse_pairs(text)
    for row in rows:
        try:
            validate_row(package, master, row, snapshot, facts, batch, history)
        except ValueError as error:
            row["error"] = str(error)
        row["current"] = snapshot.pairs[master].get((row["left"], row["right"]))
    batch.ensure_snapshot(package, snapshot)
    if str(package.master) != master:
        raise ValueError("Current master changed; Preview again.")
    return {
        "package_id": int(package.id),
        "master": master,
        "snapshot": snapshot,
        "rows": rows,
        "text": text,
    }


def apply_pairs(plan: dict[str, Any], text: str) -> bool:
    """Revalidate the displayed batch, then use the shared native kerning writer.

    This is the same checkpoint and read-back path as Scriptmix Pairs From
    Text. It never notifies glyphs or layers and never creates a glyph.
    """
    import fly.ap.history as history  # noqa: PLR0402 - preserve module imports
    import fly.ap.kerning_batch as batch
    import fly.ap.scripting as scripting  # noqa: PLR0402 - preserve module imports

    if text != plan["text"]:
        raise ValueError("Text changed; Preview again.")
    rows = plan["rows"]
    if not rows or any(row["error"] for row in rows):
        raise ValueError("Correct the rows and Preview before Apply.")
    package = scripting.current_package(plan["package_id"])
    if package is None or str(package.master) != plan["master"]:
        raise ValueError("Current font or master changed; Preview again.")
    batch.ensure_snapshot(package, plan["snapshot"])
    facts = history.scan_auto_facts(package)
    for row in rows:
        validate_row(
            package, plan["master"], row, plan["snapshot"], facts, batch, history
        )
    edits = {
        plan["master"]: {(row["left"], row["right"]): row["value"] for row in rows}
    }
    return batch.write_kerning(package, edits, TITLE, expected=plan["snapshot"])


def show(qt: Any, parent: Any) -> Any:
    """Build a modeless list importer with explicit Preview and Apply actions."""
    import fly.ap.draft_signals as signals

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own input, complete preview and exact signal connections."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(760, 580)
            self.stack = gui.QVBoxLayout(self)
            self.stack.setContentsMargins(16, 16, 16, 16)
            self.stack.setSpacing(8)
            self.status_line = gui.QLabel(
                "Paste left right value lines. # begins a comment.", self
            )
            self.stack.addWidget(self.status_line)
            self.input_field = gui.QPlainTextEdit(self)
            self.stack.addWidget(self.input_field)
            self.preview_table = gui.QTableWidget(self)
            self.preview_table.setColumnCount(6)
            self.preview_table.setHorizontalHeaderLabels(
                ["Line", "Left", "Right", "Explicit now", "Requested", "Result"]
            )
            self.preview_table.setEditTriggers(gui.QAbstractItemView.NoEditTriggers)
            self.preview_table.setAlternatingRowColors(True)
            self.stack.addWidget(self.preview_table)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )
            self.plan_data: dict[str, Any] | None = None
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())
            self.scope.connect(
                self.input_field.textChanged, lambda *args: self.invalidate_preview()
            )
            self.preview_button = gui.QPushButton("Preview", self)
            self.apply_button = gui.QPushButton("Apply", self)
            self.apply_button.setEnabled(False)
            for button, action in (
                (self.preview_button, self.preview_pairs),
                (self.apply_button, self.apply_list),
            ):
                self.stack.addWidget(button)
                self.scope.connect(
                    button.clicked, lambda *args, action=action: action()
                )

        def invalidate_preview(self) -> None:
            """Text edits must never apply an older displayed plan."""
            self.plan_data = None
            self.preview_table.setRowCount(0)
            self.apply_button.setEnabled(False)

        def preview_pairs(self) -> None:
            """Show each row and error; one invalid row blocks the whole batch."""
            self.invalidate_preview()
            try:
                plan = prepare_pairs(str(self.input_field.toPlainText()))
                self.preview_table.setRowCount(len(plan["rows"]))
                for index, row in enumerate(plan["rows"]):
                    values = [
                        row["line"],
                        row["left"],
                        row["right"],
                        row["current"] if row["current"] is not None else "Absent",
                        row["value"] if row["value"] is not None else "",
                        row["error"] or "Ready",
                    ]
                    for column, value in enumerate(values):
                        self.preview_table.setItem(
                            index, column, gui.QTableWidgetItem(str(value))
                        )
                self.plan_data = plan
                valid = bool(plan["rows"]) and not any(
                    row["error"] for row in plan["rows"]
                )
                self.apply_button.setEnabled(valid)
                self.status_line.setText(
                    f"{plan['master']}: {len(plan['rows'])} rows. "
                    + (
                        "Ready to Apply."
                        if valid
                        else "Correct invalid rows; Preview again."
                    )
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.invalidate_preview()
                self.status_line.setText(str(error))

        def apply_list(self) -> None:
            """Apply once; require a new preview after any attempt."""
            try:
                if self.plan_data is None:
                    raise ValueError("Preview the pair list first.")
                changed = apply_pairs(
                    self.plan_data, str(self.input_field.toPlainText())
                )
                self.status_line.setText(
                    "Pairs applied and read back."
                    if changed
                    else "No pair values changed."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))
            finally:
                self.plan_data = None
                self.apply_button.setEnabled(False)

        def release_owner(self) -> None:
            """Drop Python references if FontLab destroys the parent."""
            self.scope.finish(destroyed=True)
            self.plan_data = None
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Disconnect all owned callbacks before deletion; keep failed retries."""
            if not self.scope.finish():
                event.ignore()
                return
            self.plan_data = None
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.show()
    except Exception:
        if panel.scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        raise
    return panel


def main() -> None:
    """Use the host application without creating another Qt event loop."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
