# this_file: Scripts/Windows/Unicode Issues Dock.py
# SPDX-License-Identifier: Apache-2.0
"""What: Find unencoded glyphs and glyphs that share a Unicode in the current font.
How: Read the public glyph catalogue. Count owners of each Unicode scalar, then
filter and page only the issue rows. Double-click uses App scripting.select_glyphs;
its Font-window guard refuses a Glyph window or a changed current font (fl#8528).
Why: Keep an actionable Unicode checklist beside the Font window.
Usage: Activate the Font window, run this script, and double-click an issue row.
Type a name, issue or U+ value to filter. Refresh reads the current font again.
If the status line asks for the Font window, click it and double-click the row again.
The default dock area is right. show(..., area="left") chooses the left area;
top and bottom are also valid. Drag the dock title to float it or dock it again.
App widgets.create_panel floats the registered dock automatically when FontLab's
macOS multi-window profile hides MainWindow. No separate main window is created.
Close or the dock X calls handle.close_owned(): disconnect callbacks first, then
OwnedWidget.close() removes the dock and schedules its widget for deletion.
Benefit: Select the exact glyph that needs an encoding decision, without changing
its Unicode values or geometry. Counts cover every issue, even on other pages.
Setup: FontLab 9, Python 3.11, Fly and App with widgets, scripting, glyph_catalog,
draft_signals and qt_properties.
Independent rewrite of the Qt dockwidgets, menus, separations, basiclayouts and
borderlayout example ideas (Qt/Nokia, Riverbank). Based on the author's own FontLab sample, Apache-2.0.
No upstream code or assets copied.

Historical source: rescued/part3/pyqt-official-ports/ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py
SHA256: b53b4e5e158d8046220bde8de76c0af424ab90c8a96e362f29906349a5a19d35
Historical source: rescued/part3/pyqt-official-ports/ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py
SHA256: 658638cfc0891ae0a6ffabb4024cbe2aa63bec688958a28cfa46da47df90fd37
Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py
SHA256: b14d351359ef448ca38eba7a8fcf66dbdf162dbd45f63f00718ac50096000cff
Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
SHA256: 95fe3a5c2f8bb6eb3528403bcc0433ffac2550cc8cdbab52deaff372f17c4deb
Historical source: rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
SHA256: f5e1af92ebcf6d666477dc2b3f6d85cd324bc39ea1940982913b60b15c7285c6
Historical source: rescued/part2/ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py
SHA256: 6fa0e1268b7c81dbf6c373ae9ebb98ef86ffa0d7c8207ab78a003e65fc49a00d
Historical source: rescued/part2/ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
SHA256: 5db7de5bb81c11df39be0c6e83c9a39d1f42463982413e62eb27253f0efb58a6
Historical source: rescued/part2/ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py
SHA256: 61dce583b8707e5724dc6e28f4f86b2b32884dd9af5f4a25a3a145a54d146dd4
Historical source: rescued/part2/ports/mainwindows/pyqt-official/dockwidgets-4efac54bae01fc62.py
SHA256: 20ab7a5fd5b64e7c3b0cf66bfb80fbca9f8301317b314bb95e66d76b4475fc8d
Historical source: rescued/part2/ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
SHA256: fedecc268d265622812e43e61b3d80d9c4dbbb812411cc177a2f37d58ad1b039
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


TITLE = "Unicode Issues Dock"


def issue_rows(rows: Rows) -> Rows:
    """Return only unencoded glyphs and owners of shared Unicode assignments."""
    entries = []
    counts: dict[int, int] = {}
    names: set[str] = set()
    for name, field, modified in rows:
        checked(name)
        checked(modified)
        if not name or name in names:
            raise ValueError("Missing or duplicate glyph name.")
        names.add(name)
        points = codes(field)
        entries.append((name, points))
        for point in points:
            counts[point] = counts.get(point, 0) + 1
    result = []
    for name, points in entries:
        shared = tuple(point for point in points if counts[point] > 1)
        if not points:
            result.append((name, "Unencoded", ""))
        elif shared:
            result.append((name, "Shared Unicode", unicode_text(shared)))
    return tuple(result)


def show(
    qt: Any,
    main_window: Any,
    capture: Callable[[], Any] | None = None,
    *,
    area: str = "right",
) -> Any:
    """Attach one owned issues dock to FontLab's main window."""
    import fly.ap.draft_signals as signals
    import fly.ap.glyph_catalog as catalogue
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly dotted-import contract
    import fly.ap.widgets as widgets  # noqa: PLR0402 - Fly dotted-import contract

    gui, core = qt.QtGui, qt.QtCore
    capture_font = catalogue.capture if capture is None else capture

    class Panel:
        """Keep detached issue records separate from native widget wrappers."""

        def __init__(self) -> None:
            self.owned: Any = None
            self.close_in_progress = False
            self.package_id: int | None = None
            self.issue_snapshot: Rows = ()
            self.page_rows: Rows = ()
            self.page_number = 0
            self.display_cache: Rows = ()
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )

        def populate(self, content: Any) -> None:
            """Build the table once. Filtering updates only changed page cells."""
            self.body_stack = gui.QVBoxLayout(content)
            self.body_stack.setContentsMargins(12, 12, 12, 12)
            self.body_stack.setSpacing(8)
            self.count_line = gui.QLabel("No font captured", content)
            self.count_line.setTextFormat(core.Qt.PlainText)
            self.body_stack.addWidget(self.count_line)
            self.filter_field = gui.QLineEdit(content)
            self.filter_field.setPlaceholderText("Filter glyph name, issue or U+ value")
            self.body_stack.addWidget(self.filter_field)
            self.issue_view = gui.QTableView(content)
            self.data_model = gui.QStandardItemModel(content)
            self.data_model.setHorizontalHeaderLabels(
                ["Glyph", "Issue", "Shared Unicode"]
            )
            self.issue_view.setModel(self.data_model)
            self.issue_view.setSelectionBehavior(gui.QAbstractItemView.SelectRows)
            self.issue_view.setSelectionMode(gui.QAbstractItemView.SingleSelection)
            self.body_stack.addWidget(self.issue_view)
            self.action_strip = gui.QHBoxLayout()
            self.body_stack.addLayout(self.action_strip)
            self.status_line = gui.QLabel(
                "Double-click an issue to select its glyph in the active Font window.",
                content,
            )
            self.status_line.setTextFormat(core.Qt.PlainText)
            self.status_line.setWordWrap(True)
            self.body_stack.addWidget(self.status_line)
            self.scope.connect(
                content.destroyed, lambda *args: self.owner_destroyed(), closing=True
            )
            self.scope.connect(
                self.issue_view.doubleClicked, lambda index: self.select_issue(index)
            )
            self.scope.connect(
                self.filter_field.textChanged, lambda *args: self.filter_issues()
            )
            for text, action in (
                ("Refresh", self.refresh_issues),
                ("Previous", lambda: self.change_page(-1)),
                ("Next", lambda: self.change_page(1)),
            ):
                self.add_button(text, action)
            self.add_button("Close", self.close_owned, closing=True)

        def add_button(
            self, text: str, action: Callable[[], Any], *, closing: bool = False
        ) -> None:
            """Adapt clicked(bool) explicitly and retain the exact owned connection."""
            button = gui.QPushButton(text, self.owned.content)
            self.action_strip.addWidget(button)
            self.scope.connect(
                button.clicked, lambda *args: action(), closing=closing, retry=closing
            )

        def perform(self, action: Callable[[], Any]) -> None:
            """Show expected capture failures without dropping the last valid page."""
            try:
                action()
            except (ValueError, RuntimeError, TimeoutError, UnicodeError) as error:
                self.status_line.setText(str(error))

        def refresh_issues(self) -> None:
            """Bind the detached issue snapshot to the same current package."""
            package = scripting.current_package()
            if package is None:
                raise ValueError("Open a font before refreshing issues.")
            identity = int(package.id)
            rows = issue_rows(capture_font().rows)
            if scripting.current_package(identity) is None:
                raise ValueError(
                    "The current font changed during capture; refresh again."
                )
            self.package_id, self.issue_snapshot = identity, rows
            self.page_number = 0
            self.display_page()
            self.status_line.setText(
                "Double-click selects in the active Font window. Activate that window first."
            )

        def filter_issues(self) -> None:
            """Reset pagination after a name, reason or Unicode substring changes."""
            self.page_number = 0
            self.display_page()

        def change_page(self, direction: int) -> None:
            """Move through every matching issue without refusing a large font."""
            self.page_number = max(0, self.page_number + direction)
            self.display_page()

        def display_page(self) -> None:
            """Keep full issue data; update at most one hundred visible rows."""
            query = str(properties.value(self.filter_field, "text")).casefold()
            matches = tuple(
                row for row in self.issue_snapshot if query in " ".join(row).casefold()
            )
            last = max(0, (len(matches) - 1) // PAGE_SIZE)
            self.page_number = min(self.page_number, last)
            start = self.page_number * PAGE_SIZE
            page = matches[start : start + PAGE_SIZE]
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
            unencoded = sum(row[1] == "Unencoded" for row in self.issue_snapshot)
            shared = len(self.issue_snapshot) - unencoded
            self.count_line.setText(
                f"{unencoded} unencoded · {shared} shared · {len(matches)} matching · page {self.page_number + 1}/{last + 1}"
            )

        def select_issue(self, index: Any) -> None:
            """Use App's fl#8528 guard before any Font-window selection writer."""
            if not properties.value(index, "isValid"):
                return
            row = int(properties.value(index, "row"))
            if not 0 <= row < len(self.page_rows) or self.package_id is None:
                raise ValueError("Refresh issues before selecting a glyph.")
            if scripting.current_package(self.package_id) is None:
                raise ValueError(
                    "The captured font is no longer current; refresh issues."
                )
            name = self.page_rows[row][0]
            selected = scripting.select_glyphs([name], package_id=self.package_id)
            if selected != [name]:
                raise RuntimeError("FontLab did not confirm selection of /" + name)
            self.status_line.setText("Selected /" + name + " in the Font window.")

        def owner_destroyed(self) -> None:
            """Fence queued work after external destruction of the dock content."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def close_owned(self) -> bool:
            """Drain signals before OwnedWidget.close; retain a failed Close for retry."""
            if self.scope.dead and self not in _PANELS:
                return True
            if self.owned.closed and self.owned.widget is not None:
                self.status_line.setText(
                    "Dock cleanup is incomplete; the native parent still owns the dock."
                )
                return False
            if not self.scope.finish():
                return False
            self.close_in_progress = True
            try:
                self.owned.close()
            except (ValueError, RuntimeError, TimeoutError) as error:
                # A helper cleanup failure must not drop the surviving dock owner.
                self.status_line.setText("Dock cleanup paused: " + str(error))
                self.scope = signals.Scope(
                    lambda failure: self.status_line.setText(str(failure))
                )
                self.scope.connect(
                    self.owned.content.destroyed,
                    lambda *args: self.owner_destroyed(),
                    closing=True,
                )
                self.scope.closed = True
                return False
            finally:
                self.close_in_progress = False
            if self in _PANELS:
                _PANELS.remove(self)
            return True

    panel = Panel()

    class CloseFilter(gui.QWidget):
        """Route the dock's window Close through the same owned cleanup path."""

        def eventFilter(self, watched: Any, event: Any) -> bool:
            """Consume external Close; let OwnedWidget's internal Close pass."""
            if (
                properties.value(event, "type") != core.QEvent.Close
                or panel.close_in_progress
            ):
                return False
            try:
                panel.close_owned()
            except (ValueError, RuntimeError, TimeoutError) as error:
                panel.status_line.setText(str(error))
            return True

    panel.owned = widgets.create_panel(main_window, TITLE, None, area)
    _PANELS.append(panel)
    try:
        panel.owned.widget.setAttribute(core.Qt.WA_QuitOnClose, False)
        panel.close_filter = CloseFilter(panel.owned.widget)
        panel.close_filter.hide()
        panel.owned.widget.installEventFilter(panel.close_filter)
        panel.populate(panel.owned.content)
    except Exception:
        panel.close_owned()
        raise
    panel.perform(panel.refresh_issues)
    return panel


def main() -> Any:
    """Attach to the host main window; show a readable setup refusal."""
    from fly import fl, qt

    parent = fl.MainWindow()
    try:
        return show(qt, parent)
    except (ValueError, RuntimeError, TimeoutError) as error:
        qt.QtGui.QMessageBox.warning(parent, TITLE, str(error))
        return None


if __name__ == "__main__":
    main()
