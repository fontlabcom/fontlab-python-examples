# this_file: Scripts/Windows/Glyph Snapshot Diff.py
# SPDX-License-Identifier: Apache-2.0
"""What: Compare the first captured glyph catalogue with the newest capture.
How: Bind both snapshots to the current font package. Match glyph names and
compare complete Unicode sets plus modification dates and epoch milliseconds.
Report added, removed, re-encoded and modified glyphs in separate change rows.
Why: A focused difference is easier to review than two complete inventories.
Usage: Run to capture the baseline. Make changes in FontLab, then Capture Latest.
The first capture stays fixed. Reset Baseline explicitly starts a new comparison,
including after switching fonts. Previous and Next page the display; Copy All Diff
copies the complete comparison. Renames appear as a removed and an added glyph.
A glyph can be both re-encoded and modified. Unicode order alone is not a change.
Benefit: Review the actual effects of a script or manual edit, with every changed
Unicode and modification value retained. This tool changes no font data.
Setup: FontLab 9, Python 3.11, Fly and App with glyph_catalog, scripting,
draft_signals. The modeless window contains one reusable table.
Independent rewrite of the Qt mdi example idea (Qt/Nokia, Riverbank).
Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/mdi-1415facde30a25cf.py
SHA256: 29271121483f2c5fabe6b0f0232602bcc32f9d0a0ccc69ad553149a5706d8199
Historical source: rescued/part2/ports/mainwindows/pyqt-official/mdi-1415facde30a25cf.py
SHA256: 4a7cab42d4c0c13dd09e5c098e6758007f81371fbb90b832d25c1f44e055609c
"""

from collections.abc import Callable
from typing import Any

PAGE_SIZE = 100
_PANELS: list[Any] = []
Rows = tuple[tuple[str, str, str], ...]


def checked(text: str) -> str:
    """Refuse characters that Qt may change or that can split table fields."""
    if any(
        char in text for char in ("\0", "\u00a0", "\u2028", "\u2029", "\r", "\n", "\t")
    ):
        raise ValueError("A glyph field contains unsupported whitespace or NUL.")
    text.encode("utf-8")
    return text


def codes(field: str) -> tuple[int, ...]:
    """Parse the public catalogue's U+ tokens into distinct Unicode scalars."""
    values = set()
    checked(field)
    for token in field.split():
        digits = token.removeprefix("U+")
        if (
            not token.startswith("U+")
            or not 4 <= len(digits) <= 6
            or any(char not in "0123456789abcdefABCDEF" for char in digits)
        ):
            raise ValueError("Invalid Unicode token: " + token)
        number = int(digits, 16)
        if not 0 <= number <= 0x10FFFF or 0xD800 <= number <= 0xDFFF:
            raise ValueError("Invalid Unicode scalar: " + token)
        values.add(number)
    return tuple(sorted(values))


def unicode_text(values: tuple[int, ...]) -> str:
    """Format all code points, including non-BMP values, without Qt conversion."""
    return " ".join(f"U+{number:04X}" for number in values)


TITLE = "Glyph Snapshot Diff"
Snapshot = dict[str, tuple[tuple[int, ...], str, int | None]]
Changes = tuple[tuple[str, str, str, str], ...]


def snapshot(table: Any) -> Snapshot:
    """Detach one complete catalogue, retaining epoch precision when available."""
    rows = table.rows
    epochs = table.epochs if table.epochs is not None else (None,) * len(rows)
    if len(rows) != len(epochs):
        raise ValueError("Modification epochs do not cover every glyph.")
    result = {}
    for (name, field, modified), epoch in zip(rows, epochs, strict=True):
        checked(name)
        checked(modified)
        if not name or name in result:
            raise ValueError("Missing or duplicate glyph name.")
        if epoch is not None and type(epoch) is not int:
            raise ValueError("Modification epochs must be integers or None.")
        result[name] = (codes(field), modified, epoch)
    return result


def date_text(record: tuple[tuple[int, ...], str, int | None]) -> str:
    """Show subsecond changes that the catalogue's formatted date cannot show."""
    _, modified, epoch = record
    return (modified or "(unset)") + (f" [{epoch} ms]" if epoch is not None else "")


def diff_rows(first: Snapshot, newest: Snapshot) -> Changes:
    """Compare names, Unicode sets and exact modification values to the baseline.

    Renames appear as removed plus added glyphs. A surviving glyph may appear
    in both Re-encoded and Modified; neither fact suppresses the other.
    """
    added = [
        ("Added", name, "", unicode_text(newest[name][0]) or "(unencoded)")
        for name in sorted(newest.keys() - first.keys())
    ]
    removed = [
        ("Removed", name, unicode_text(first[name][0]) or "(unencoded)", "")
        for name in sorted(first.keys() - newest.keys())
    ]
    reencoded, modified = [], []
    for name in sorted(first.keys() & newest.keys()):
        old, new = first[name], newest[name]
        if old[0] != new[0]:
            reencoded.append(
                (
                    "Re-encoded",
                    name,
                    unicode_text(old[0]) or "(unencoded)",
                    unicode_text(new[0]) or "(unencoded)",
                )
            )
        if old[1:] != new[1:]:
            modified.append(("Modified", name, date_text(old), date_text(new)))
    return tuple(added + removed + reencoded + modified)


def diff_text(rows: Changes) -> str:
    """Copy the full baseline diff for a FontLab change-review handoff."""
    return "Category\tGlyph\tFirst snapshot\tNewest snapshot\n" + "".join(
        "\t".join(row) + "\n" for row in rows
    )


def show(qt: Any, parent: Any, capture: Callable[[], Any] | None = None) -> Any:
    """Open a modeless first-to-latest comparison of one current font."""
    import fly.ap.draft_signals as signals
    import fly.ap.glyph_catalog as catalogue
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly dotted-import contract

    gui, core = qt.QtGui, qt.QtCore
    capture_font = catalogue.capture if capture is None else capture

    class Panel(gui.QWidget):
        """Retain two detached snapshots and one reusable visible model."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.baseline: Snapshot | None = None
            self.latest: Snapshot | None = None
            self.package_id: int | None = None
            self.change_rows: Changes = ()
            self.page_rows: Changes = ()
            self.display_cache: Changes = ()
            self.page_number = 0
            self.capture_number = 0
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(860, 520)
            self.body_stack = gui.QVBoxLayout(self)
            self.body_stack.setContentsMargins(16, 16, 16, 16)
            self.body_stack.setSpacing(8)
            self.status_line = gui.QLabel("Capture reads the current font.", self)
            self.status_line.setTextFormat(core.Qt.PlainText)
            self.status_line.setWordWrap(True)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def populate(self) -> None:
            """Create read-only comparison controls once; no subwindow can go stale."""
            self.count_line = gui.QLabel("No baseline captured", self)
            self.count_line.setTextFormat(core.Qt.PlainText)
            self.body_stack.addWidget(self.count_line)
            self.diff_view = gui.QTableView(self)
            self.data_model = gui.QStandardItemModel(self)
            self.data_model.setHorizontalHeaderLabels(
                ["Change", "Glyph", "First snapshot", "Newest snapshot"]
            )
            self.diff_view.setModel(self.data_model)
            self.body_stack.addWidget(self.diff_view)
            self.action_strip = gui.QHBoxLayout()
            self.body_stack.addLayout(self.action_strip)
            self.body_stack.addWidget(self.status_line)
            self.scope.connect(
                self.destroyed, lambda *args: self.owner_destroyed(), closing=True
            )
            for text, action in (
                ("Capture Latest", self.capture_latest),
                ("Reset Baseline", self.reset_baseline),
                ("Previous", lambda: self.change_page(-1)),
                ("Next", lambda: self.change_page(1)),
                ("Copy All Diff", self.copy_diff),
            ):
                self.add_button(text, action)
            self.add_button("Close", lambda: self.close(), closing=True)

        def add_button(
            self, text: str, action: Callable[[], Any], *, closing: bool = False
        ) -> None:
            """Adapt clicked(bool) and preserve a retry path after failed disconnect."""
            button = gui.QPushButton(text, self)
            self.action_strip.addWidget(button)
            self.scope.connect(
                button.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def perform(self, action: Callable[[], Any]) -> None:
            """Retain both snapshots when a font read fails or times out."""
            try:
                action()
            except (ValueError, RuntimeError, TimeoutError, UnicodeError) as error:
                self.status_line.setText(str(error))

        def read_current(self, *, reset: bool) -> tuple[int, Snapshot]:
            """Refuse a changed font unless Reset Baseline explicitly requests it."""
            expected = None if reset else self.package_id
            package = scripting.current_package(expected)
            if package is None:
                raise ValueError(
                    "The current font is missing or changed; use Reset Baseline for a different font."
                )
            identity = int(package.id)
            records = snapshot(capture_font())
            if scripting.current_package(identity) is None:
                raise ValueError("The current font changed during capture.")
            return identity, records

        def capture_latest(self) -> None:
            """Keep the first capture fixed and replace only the newest capture."""
            identity, records = self.read_current(reset=False)
            baseline = records if self.baseline is None else self.baseline
            changes = diff_rows(baseline, records)
            self.baseline, self.latest = baseline, records
            self.package_id, self.change_rows = identity, changes
            self.capture_number += 1
            self.page_number = 0
            self.display_page()
            self.status_line.setText(
                f"First capture compared with capture {self.capture_number}. Reset Baseline starts a new comparison."
            )

        def reset_baseline(self) -> None:
            """Capture a new first snapshot, including after switching current fonts."""
            identity, records = self.read_current(reset=True)
            self.package_id, self.baseline, self.latest = identity, records, records
            self.change_rows, self.page_number, self.capture_number = (), 0, 1
            self.display_page()
            self.status_line.setText(
                "New baseline captured. Make changes in FontLab, then Capture Latest."
            )

        def change_page(self, direction: int) -> None:
            """Page the visible diff while retaining every change for copying."""
            self.page_number = max(0, self.page_number + direction)
            self.display_page()

        def display_page(self) -> None:
            """Update changed cells in one model instead of rebuilding the model."""
            last = max(0, (len(self.change_rows) - 1) // PAGE_SIZE)
            self.page_number = min(self.page_number, last)
            start = self.page_number * PAGE_SIZE
            page = self.change_rows[start : start + PAGE_SIZE]
            self.data_model.setRowCount(len(page))
            for row_index, row in enumerate(page):
                for column, text in enumerate(row):
                    if (
                        row_index < len(self.display_cache)
                        and self.display_cache[row_index][column] == text
                    ):
                        continue
                    item = gui.QStandardItem(text)
                    item.setEditable(False)
                    self.data_model.setItem(row_index, column, item)
            self.display_cache, self.page_rows = page, page
            counts = {
                label: sum(row[0] == label for row in self.change_rows)
                for label in ("Added", "Removed", "Re-encoded", "Modified")
            }
            self.count_line.setText(
                " · ".join(
                    f"{count} {label.lower()}" for label, count in counts.items()
                )
                + f" · page {self.page_number + 1}/{last + 1}"
            )

        def copy_diff(self) -> None:
            """Copy every change, including changes beyond the visible page."""
            if self.baseline is None:
                raise ValueError("Capture a baseline before copying a diff.")
            gui.QApplication.clipboard().setText(diff_text(self.change_rows))
            self.status_line.setText("Complete first-to-newest diff copied.")

        def owner_destroyed(self) -> None:
            """Fence queued callbacks when FontLab destroys this tool externally."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Disconnect exact owned callbacks before deleting the modeless panel."""
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
        panel.populate()
    except Exception:
        panel.close()
        raise
    panel.perform(panel.capture_latest)
    panel.show()
    return panel


def main() -> Any:
    """Use FontLab's existing application and report expected setup refusals."""
    from fly import fl, qt

    parent = fl.MainWindow()
    try:
        return show(qt, parent)
    except (ValueError, RuntimeError, TimeoutError) as error:
        qt.QtGui.QMessageBox.warning(parent, TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
