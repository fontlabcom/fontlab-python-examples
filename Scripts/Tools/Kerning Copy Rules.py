# this_file: Scripts/Tools/Kerning Copy Rules.py
# SPDX-License-Identifier: Apache-2.0
"""What: Expand kerning copy rules into a current-master import list.
How: Read explicit pairs once. Use `A|V A|W = T|o @ -5` to copy T/o minus
five units to A/V and A/W. @class names use native kerning-class notation.
Every rule reads the original snapshot. No rule reads another rule's output.
Why: Reuse measured pairs without manual arithmetic or repeated pair edits.
Usage: Open a font. Enter rules. Build, inspect and Copy. Paste straight into
Tools > Import Kerning Pair List, then Preview and Apply. Export is optional.
Import uses the master that is current when you press Preview; check its status.
Benefit: Keep a reproducible pair list. This panel never changes the font.

Only explicit current-master pairs are read; inherited class results are not
guessed. All glyphs and class sides must exist. Offsets and results must be
whole units. A repeated destination or invalid row refuses the entire output.
The source supports all masters, automatic glyph-to-class lookup, character
tokens and arithmetic adjustments. This port keeps explicit current-master
glyph or @class tokens and integer additive adjustments only. It has no All
masters mode, automatic class lookup, character tokens, general arithmetic,
class-file import or direct application.
Use native Kerning panel > Copy Kerning From for complete-master transfers.
Requires FontLab 9, Python 3.11, Fly and App >= 0.2.150.dev0.

Credit: Independent behaviour rewrite of CopyKerning.py by Vassil Kateliev,
Karandash Type Foundry, kateliev/TypeRig, MPL-2.0.
https://github.com/kateliev/TypeRig
No source code, comments, icons or preset formats are copied.
"""

import math
import re
from pathlib import Path
from typing import Any

TITLE = "Kerning Copy Rules"
_PANELS: list[Any] = []


def pair_token(token: str) -> tuple[str, str]:
    """Parse one explicit native-name pair; refuse ambiguous import-list text."""
    parts = token.split("|")
    if len(parts) != 2 or any(
        not name or any(c.isspace() or c in "|=#\0" for c in name) for name in parts
    ):
        raise ValueError("Use left|right with two nonempty glyph or @class names.")
    return parts[0], parts[1]


def expand_rules(
    text: str, pairs: dict[tuple[str, str], int]
) -> dict[tuple[str, str], int]:
    """Resolve all rules against one immutable explicit-pair snapshot."""
    if any(c in text for c in ("\0", "\u00a0", "\u2028", "\u2029")):
        raise ValueError("Text contains characters that Qt cannot preserve.")
    text.encode("utf-8")
    result: dict[tuple[str, str], int] = {}
    for number, line in enumerate(text.splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            if line.count("=") != 1:
                raise ValueError("Use exactly one =.")
            destinations, source = line.split("=")
            # A class marker belongs to the pair; an offset marker follows it.
            match = re.fullmatch(r"\s*(\S+?\|\S+?)(?:\s*@\s*([+-]?\d+))?\s*", source)
            if match is None:
                raise ValueError(
                    "Use source left|right with an optional @ signed-integer offset."
                )
            token, adjustment = match.groups()
            key = pair_token(token)
            if key not in pairs:
                raise ValueError(f"No explicit source pair: {token}")
            value = float(pairs[key]) + (
                int(adjustment) if adjustment is not None else 0
            )
            if not math.isfinite(value) or not value.is_integer():
                raise ValueError("Source and result must be finite whole units.")
            if not destinations.split():
                raise ValueError("Give at least one destination pair.")
            for token in destinations.split():
                destination = pair_token(token)
                if destination in result:
                    raise ValueError(f"Repeated destination: {token}")
                result[destination] = int(value)
        except (ValueError, OverflowError) as error:
            raise ValueError(f"Line {number}: {error}") from error
    if not result:
        raise ValueError("Enter at least one copy rule.")
    return result


def build_pair_list(text: str) -> str:
    """Read the current master; validate class sides and recheck the full snapshot."""
    import fly.ap.kerning_batch as batch
    import fly.ap.scripting as scripting  # noqa: PLR0402

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font first.")
    master = str(package.master)
    snapshot = batch.snapshot_kerning(package)
    if master not in snapshot.pairs:
        raise ValueError("Current master changed during capture; Build again.")
    changes = expand_rules(text, snapshot.pairs[master])
    limit = 2 * float(package.upm)
    if not math.isfinite(limit) or limit <= 0:
        raise ValueError("Use a font with finite positive units per em.")
    for pair, value in changes.items():
        batch.validate_pair(package, master, pair, groups=snapshot.groups[master])
        if abs(value) > min(limit, 32767):
            raise ValueError(f"{pair}: value exceeds the pair-list or font save range.")
    batch.ensure_snapshot(package, snapshot)
    if str(package.master) != master:
        raise ValueError("Current master changed; Build again.")
    safe_master = master.encode("unicode_escape").decode("ascii")
    return f"# Master: {safe_master}\n" + "".join(
        f"{left} {right} {value}\n" for (left, right), value in changes.items()
    )


def export_new(filename: str, content: str) -> None:
    """Write the exact visible artifact once to an absolute file."""
    path = Path(filename).expanduser()
    if not path.is_absolute() or not content:
        raise ValueError("Build a result and enter a new absolute output path.")
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(content)


def show(qt: Any, parent: Any) -> Any:
    """Keep a non-modal recipe panel with owned callbacks and read-only output."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Keep complete output; discard stale preview when the recipe changes."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(640, 560)
            self.box = gui.QVBoxLayout(self)
            self.status_line = gui.QLabel(
                "Copy explicit current-master pairs. No font writes.", self
            )
            self.box.addWidget(self.status_line)
            self.box.addWidget(gui.QLabel("A|V A|W = T|o @ -5", self))
            self.rule_field = gui.QPlainTextEdit(self)
            self.box.addWidget(self.rule_field)
            self.result_field = gui.QPlainTextEdit(self)
            self.result_field.setReadOnly(True)
            self.box.addWidget(self.result_field)
            self.box.addWidget(gui.QLabel("New output file (absolute path)", self))
            self.path_field = gui.QLineEdit(self)
            self.box.addWidget(self.path_field)
            self.content = ""
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())
            self.scope.connect(
                self.rule_field.textChanged, lambda *args: self.clear_result()
            )
            for label, action in (
                ("Build Pair List", self.build_result),
                ("Copy", self.copy_result),
                ("Export New", self.save_result),
            ):
                button = gui.QPushButton(label, self)
                self.box.addWidget(button)
                self.scope.connect(
                    button.clicked, lambda *args, action=action: action()
                )

        def clear_result(self) -> None:
            """Prevent exporting a previous recipe after editing the input."""
            self.content = ""
            self.result_field.setPlainText("")

        def build_result(self) -> None:
            """Publish only a complete validated current-master pair list."""
            self.clear_result()
            try:
                self.content = build_pair_list(str(self.rule_field.toPlainText()))
                self.result_field.setPlainText(self.content)
                self.status_line.setText(
                    "Copy into Tools > Import Kerning Pair List. Import applies to its current Preview master."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def copy_result(self) -> None:
            """Copy the validated list directly to the importer's paste field."""
            if not self.content:
                self.status_line.setText("Build the pair list first.")
                return
            gui.QApplication.clipboard().setText(self.content)
            self.status_line.setText(
                "Paste into Tools > Import Kerning Pair List. Check the master at Preview."
            )

        def save_result(self) -> None:
            """Save the displayed detached list; never refresh it silently."""
            try:
                export_new(str(properties.value(self.path_field, "text")), self.content)
                self.status_line.setText("Pair list exported. Font data is unchanged.")
            except (ValueError, RuntimeError, OSError) as error:
                self.status_line.setText(
                    f"{error} A failed write may leave a partial file."
                )

        def release_owner(self) -> None:
            """Release callbacks after native parent destruction."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Disconnect before deletion; retain the panel if cleanup fails."""
            if not self.scope.finish():
                event.ignore()
                return
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
    """Show inside FontLab's existing application."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
