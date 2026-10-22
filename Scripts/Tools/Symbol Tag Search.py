# this_file: Scripts/Tools/Symbol Tag Search.py
# SPDX-License-Identifier: Apache-2.0
"""What: Find symbols by native glyph name and tags in the current font.
How: Match all space-separated terms, without case, against each name and tag.
Read names and tags once per refresh; report skipped names. Copy slash names to a Glyph window.
Why: Native tags travel with the font and need no external symbol database.
Usage: Enter name or tag terms. Refresh Result shows matches in font order.
Copy Fresh Result reads the current font again before it copies the proof.
Benefit: Prepare a proof of related symbols, including unencoded glyphs.
This tool reads native tags. External textproto categories, visual similarity,
contour-part assembly and transforms are outside this search tool's scope.
Use FontLab's contour selection and Edit > Copy / Paste for contour parts.
The Font window sidebar > Tags filter searches native tags. This tool matches
several terms across names and tags together and copies an ordered slash proof.

Independent behaviour-only rewrite of the symbol-search idea from Explorer.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.
"""

from threading import current_thread, main_thread
from time import monotonic
from typing import Any

TITLE = "Symbol Tag Search"
HELP = (
    "All terms must match the glyph name or its native tags. Output uses slash names."
)
FIELDS = (("Name or native tag terms (all must match)", ""),)
CHOICES: dict[int, tuple[str, ...]] = {}
_PANELS: list[Any] = []


def capture_tags(
    native: Any = None, *, deadline: float | None = None
) -> tuple[tuple[tuple[str, tuple[str, ...]], ...], tuple[str, ...]]:
    """Read names and tags once; keep bad names as skipped rows, without geometry."""
    if native is None:
        from fly import fl

        native = fl
    if current_thread() is not main_thread():
        raise RuntimeError("Read font tags on the main UI thread.")
    limit = monotonic() + 2.0 if deadline is None else deadline
    workspace = native.flWorkspace.instance()
    package, font = workspace.currentPackage, native.CurrentFont()
    if (
        package is None
        or package.isNull
        or font is None
        or int(package.fgId) != int(font.id)
    ):
        raise ValueError("Open a font first.")
    identity = int(package.id), int(package.fgId)
    rows: list[tuple[str, tuple[str, ...]]] = []
    skipped: list[str] = []
    for record in font.glyphs:
        if monotonic() >= limit:
            raise TimeoutError("Font tag scan expired; no partial result.")
        glyph = package.findFgId(int(record.id))
        if glyph is None or glyph.isNull:
            raise ValueError("A font glyph disappeared; refresh again.")
        name = glyph.name
        try:
            if (
                not isinstance(name, str)
                or not name
                or any(char.isspace() or char == "/" for char in name)
            ):
                raise ValueError("name cannot form a slash proof")
            checked(name)
        except ValueError as error:
            skipped.append(f"Skipped {name!r}: {error}")
            continue
        tags = tuple(glyph.tags or ())
        if not all(isinstance(tag, str) for tag in tags):
            skipped.append(f"Skipped {name!r}: unreadable tags")
            continue
        rows.append((name, tags))
    current = workspace.currentPackage
    if monotonic() >= limit:
        raise TimeoutError("Font tag scan expired; no partial result.")
    if (
        current is None
        or current.isNull
        or (int(current.id), int(current.fgId)) != identity
    ):
        raise ValueError("Current font changed; refresh again.")
    return tuple(rows), tuple(skipped)


def search_result(fields: tuple[str, ...]) -> tuple[str, tuple[str, ...]]:
    """Return a slash proof and separate skip rows; blank queries read no font."""
    terms = checked(fields[0]).casefold().split()
    if not terms:
        return "", ()
    rows, skipped = capture_tags()
    selected = [
        "/" + name
        for name, tags in rows
        if all(term in " ".join((name, *tags)).casefold() for term in terms)
    ]
    return "".join(selected), skipped


def build_output(fields: tuple[str, ...]) -> str:
    """Produce an ordered slash proof from an AND search of names and tags."""
    return search_result(fields)[0]


def checked(text: str) -> str:
    """Refuse characters that the Qt bridge or proof syntax can change."""
    if any(char in text for char in ("\0", "\u00a0", "\u2028", "\u2029", "\r")):
        raise ValueError("Text contains NUL, NBSP, CR or a Unicode line separator.")
    try:
        text.encode("utf-8")
    except UnicodeError as error:
        raise ValueError("Text contains an invalid Unicode surrogate.") from error
    return text


def show(qt: Any, parent: Any) -> Any:
    """Open an owned modeless panel; drain callbacks before deletion."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own inputs, current output and a retryable signal scope."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(740, 540)
            self.stack_box = gui.QVBoxLayout(self)
            self.status_line = gui.QLabel(HELP, self)
            self.stack_box.addWidget(self.status_line)
            self.signal_scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def build_controls(self) -> None:
            """Build fallible controls under the outer owned-window cleanup guard."""
            self.input_boxes: list[Any] = []
            for index, (label, initial) in enumerate(FIELDS):
                self.stack_box.addWidget(gui.QLabel(label, self))
                if index in CHOICES:
                    item = gui.QComboBox(self)
                    item.addItems(list(CHOICES[index]))
                    item.setCurrentIndex(CHOICES[index].index(initial))
                else:
                    item = gui.QLineEdit(self)
                    item.setText(initial)
                self.stack_box.addWidget(item)
                self.input_boxes.append(item)
            self.output_box = gui.QPlainTextEdit(self)
            self.output_box.setReadOnly(True)
            self.stack_box.addWidget(self.output_box)
            for label, action in (
                ("Refresh Result", self.refresh_output),
                ("Copy Fresh Result", self.copy_output),
            ):
                button = gui.QPushButton(label, self)
                self.stack_box.addWidget(button)
                self.signal_scope.connect(
                    button.clicked, lambda *args, call=action: call()
                )
            self.signal_scope.connect(
                self.destroyed, lambda *args: self.release_owner()
            )

        def fresh_output(self) -> str:
            """Recapture live input; never export a previous font's result."""
            fields = tuple(
                checked(
                    str(
                        properties.value(
                            item, "currentText" if index in CHOICES else "text"
                        )
                    )
                )
                for index, item in enumerate(self.input_boxes)
            )
            text, skipped = search_result(fields)
            self.skipped_rows = skipped
            return checked(text)

        def refresh_output(self) -> None:
            """Replace the result atomically; clear stale output after a refusal."""
            try:
                text = self.fresh_output()
                self.output_box.setPlainText(text)
                self.status_line.setText(
                    "Result refreshed. " + HELP + "\n" + "\n".join(self.skipped_rows)
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output_box.setPlainText("")
                self.status_line.setText(str(error))

        def copy_output(self) -> None:
            """Read again before copying a FontLab-consumable proof or table."""
            try:
                text = self.fresh_output()
                if not text:
                    raise ValueError("No matching output to copy.")
                gui.QApplication.clipboard().setText(text)
                self.output_box.setPlainText(text)
                self.status_line.setText(
                    "Fresh result copied.\n" + "\n".join(self.skipped_rows)
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output_box.setPlainText("")
                self.status_line.setText(str(error))

        def release_owner(self) -> None:
            """Release Python state when the native parent destroys this panel."""
            self.signal_scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Retain failed disconnections for a window-Close retry."""
            if not self.signal_scope.finish():
                event.ignore()
                return
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.build_controls()
        panel.refresh_output()
        panel.show()
    except Exception:
        if panel.signal_scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        raise
    return panel


def main() -> None:
    """Open inside FontLab's existing application and main window."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
