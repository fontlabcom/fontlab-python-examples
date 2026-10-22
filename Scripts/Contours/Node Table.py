# this_file: Scripts/Contours/Node Table.py
# SPDX-License-Identifier: Apache-2.0
"""What: Inspect all own nodes of the current glyph layer and edit X and Y.
How: Read node order, coordinates, types and canvas selection. Stage numeric
cells in a non-modal table. Apply writes accepted edits through App's outline
writer and history.commit. An Apply that changes coordinates is recorded as
one Undo step.
Why: A complete node table exposes unselected points and keeps refused rows.
Usage: Open a glyph. Refresh reads its active layer and discards local cell
edits. Table selection selects canvas nodes; Read Canvas Selection reads the
other direction without discarding cell edits. Edit X/Y, then press Apply.
Refresh caches auto-layer facts; Apply scans them again. Selection reads only
the current layer and synchronizes own nodes even when coordinate edits are
refused. Selection flags are verified; unsynced rows are named in the status.
Benefit: Inspect and edit exact node coordinates without changing node order.
Coordinates use each shape's local space. Translated shapes remain editable;
components, shared outlines, transformed or locked shapes, locked layers,
auto layers and bases of auto composites stay as named kept rows.
Invalid numeric cells and nodes changed since Refresh are kept independently.
Node types are read-only. Distance and angle columns are outside this table.
Window > Panels > Node edits selected canvas points; this table lists every
own node and synchronizes its row selection with the canvas.

Independent behaviour-only rewrite of the node-table idea from Outline.py.
Credit: Vassil Kateliev and Karandash Type Foundry; kateliev/TypeRig, MPL-2.0.
No TypeRig code, comments, icons or resources are included.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.
"""

from dataclasses import dataclass, field, replace
from math import isfinite, isnan
from threading import current_thread, main_thread
from time import monotonic
from typing import Any

TITLE = "Node Table"
Key = tuple[int, int, int]
_PANELS: list[Any] = []


@dataclass(frozen=True)
class NodeRow:
    """One node or a kept component row, with a retained native node handle."""

    key: Key
    x: float | None
    y: float | None
    kind: str
    kept: str
    selected: bool
    node: Any = field(compare=False, repr=False)


@dataclass(frozen=True)
class Snapshot:
    """Current registered font, glyph and layer, plus every displayed row."""

    context: tuple[int, int, int, int]
    rows: tuple[NodeRow, ...]
    package: Any = field(compare=False, repr=False)
    glyph: Any = field(compare=False, repr=False)
    layer: Any = field(compare=False, repr=False)
    facts: Any = field(compare=False, repr=False)


def native_module(native: Any = None) -> Any:
    """Resolve the host lazily and require its main UI thread."""
    if current_thread() is not main_thread():
        raise RuntimeError("Use Node Table on the main UI thread.")
    if native is None:
        from fly import fl

        return fl
    return native


def current_context(native: Any) -> tuple[tuple[int, int, int, int], Any, Any, Any]:
    """Map the active FontGate glyph by fgId into its registered font."""
    package = native.flWorkspace.instance().currentPackage
    source, font = native.CurrentGlyph(), native.CurrentFont()
    if package is None or package.isNull or source is None or font is None:
        raise ValueError("Open a font and a glyph first.")
    if int(font.id) != int(package.fgId):
        raise ValueError("Current font changed; refresh again.")
    glyph = package.findFgId(int(source.id))
    if glyph is None or glyph.isNull or int(glyph.package.id) != int(package.id):
        raise ValueError("The current glyph belongs to another font.")
    layer = glyph.activeLayer
    if layer is None or layer.isNull:
        raise ValueError("The current glyph has no active layer.")
    return (
        (int(package.id), int(package.fgId), int(glyph.id), int(layer.id)),
        package,
        glyph,
        layer,
    )


def read_rows(layer: Any, deadline: float) -> tuple[NodeRow, ...]:
    """Read current-layer nodes and shape guards only; never scan font dependencies."""
    import fly.ap.outline_writer as outlines

    allowed, _ = outlines.outline_shapes(layer)
    editable_ids = {int(shape.id) for shape in allowed}
    rows: list[NodeRow] = []
    for si, shape in enumerate(layer.shapes):
        kept = ""
        if shape.isComponent:
            rows.append(
                NodeRow(
                    (si, -1, -1),
                    None,
                    None,
                    "component",
                    "component; edit its base glyph",
                    False,
                    None,
                )
            )
            continue
        if shape.contentLocked:
            kept = kept or "locked shape"
        elif int(shape.id) not in editable_ids:
            kept = kept or (
                "shared outline"
                if int(shape.shapeData.referenceCount) > 1
                else "scaled or rotated shape"
            )
        for ci, contour in enumerate(shape.contours):
            for ni, node in enumerate(contour.nodes()):
                if monotonic() >= deadline:
                    raise TimeoutError("Node scan expired; no partial table.")
                x, y = float(node.x), float(node.y)
                note = kept or (
                    "non-finite coordinates"
                    if not isfinite(x) or not isfinite(y)
                    else ""
                )
                rows.append(
                    NodeRow(
                        (si, ci, ni),
                        x,
                        y,
                        str(node.type),
                        note,
                        bool(node.selected),
                        node,
                    )
                )
    if monotonic() >= deadline:
        raise TimeoutError("Node scan expired; no partial table.")
    return tuple(rows)


def capture_nodes(native: Any = None, *, facts: Any = None) -> Snapshot:
    """Refresh/Apply scan once; selection and post-Apply reads reuse cached facts.

    Start the geometry budget after the dependency scan. The scan is the App's
    separate whole-font preflight and is not charged to the current-layer read.
    """
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.qt_properties as properties

    native = native_module(native)
    context, package, glyph, layer = current_context(native)
    if facts is None:
        facts = history.scan_auto_facts(package)
    deadline = monotonic() + 2.0
    rows = read_rows(layer, deadline)
    reason = history.refusal(facts, glyph.name, "geometry")
    if layer.autoLayer:
        reason = "auto layer"
    if properties.value(layer, "isLocked") or properties.value(layer, "isLockedI"):
        reason = "locked layer"
    if reason:
        rows = tuple(replace(row, kept=reason) for row in rows)
    if current_context(native)[0] != context:
        raise ValueError("Current glyph or layer changed; refresh again.")
    return Snapshot(context, rows, package, glyph, layer, facts)


@dataclass(frozen=True)
class ApplyResult:
    """Completed coordinate writes, attempted kept edits and freshly scanned facts."""

    changed: int
    kept: dict[Key, str]
    facts: Any


def same_geometry(left: NodeRow, right: NodeRow) -> bool:
    """Ignore selection changes while guarding coordinates, order and type."""
    return (left.key, left.kind) == (right.key, right.kind) and all(
        a == b or (a is not None and b is not None and isnan(a) and isnan(b))
        for a, b in ((left.x, right.x), (left.y, right.y))
    )


def apply_edits(
    snapshot: Snapshot, cells: dict[Key, tuple[str, str]], native: Any = None
) -> ApplyResult:
    """Write valid fresh rows once; keep each refused or invalid row independently."""
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.outline_writer as outlines

    current = capture_nodes(native)
    if current.context != snapshot.context:
        raise ValueError("Current font, glyph or layer changed; refresh before Apply.")
    original = {row.key: row for row in snapshot.rows}
    live = {row.key: row for row in current.rows}
    kept: dict[Key, str] = {}
    edits: list[tuple[NodeRow, float, float]] = []
    for key, (x_text, y_text) in cells.items():
        row, old = live.get(key), original.get(key)
        if old is not None and (x_text, y_text) == (repr(old.x), repr(old.y)):
            continue
        if row is None or old is None or not same_geometry(old, row):
            kept[key] = "node changed since Refresh"
            continue
        if row.kept:
            kept[key] = row.kept
            continue
        try:
            x, y = float(x_text), float(y_text)
            if not isfinite(x) or not isfinite(y):
                raise ValueError("coordinates must be finite")
        except ValueError as error:
            kept[key] = f"invalid coordinates: {error}"
            continue
        if (x, y) != (row.x, row.y):
            edits.append((row, x, y))
    if not edits:
        return ApplyResult(0, kept, current.facts)

    class CoordinateEditor(outlines.Editor):
        """Change existing nodes only; preserve native objects and metadata."""

        def write(self, layer: Any, steps: list[Any]) -> None:
            for row, x, y in steps:
                row.node.x, row.node.y = x, y

        def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
            return [
                f"node {row.key}"
                for _, steps in prepared
                for row, x, y in steps
                if (float(row.node.x), float(row.node.y)) != (x, y)
            ]

    try:
        outlines.apply_work(
            [(current.glyph, current.layer, edits)],
            TITLE,
            current.facts,
            CoordinateEditor(),
        )
    except RuntimeError as error:
        if str(error).startswith(history.NOT_STORED):
            raise RuntimeError(f"{error} {history.UNDO_HINT}") from error
        raise
    return ApplyResult(len(edits), kept, current.facts)


def select_nodes(
    snapshot: Snapshot, chosen: set[Key], native: Any = None
) -> dict[Key, str]:
    """Sync every own node independently of edit refusals; name failed rows.

    Deselection clears smart-selection metadata; other values are retained.
    Read flags back; restore a failed row's opening flags where possible.
    Geometry is read; no geometry writes, history or dependency scans occur.
    """
    native = native_module(native)
    current = capture_nodes(native, facts=snapshot.facts)
    if (
        current.context != snapshot.context
        or len(current.rows) != len(snapshot.rows)
        or any(
            not same_geometry(a, b)
            for a, b in zip(current.rows, snapshot.rows, strict=True)
        )
    ):
        raise ValueError("Node table changed; refresh before selecting rows.")
    canvas = native.flWorkspace.instance().getActiveCanvas()
    if canvas is None or canvas.isNull:
        raise ValueError("Activate the Glyph window before selecting nodes.")
    failures: dict[Key, str] = {}
    verified: list[tuple[NodeRow, bool, Any]] = []
    for row in current.rows:
        if row.node is None:
            if row.key in chosen:
                failures[row.key] = "component; edit its base glyph"
            continue
        node = row.node
        wanted = row.key in chosen
        opening: tuple[bool, Any] | None = None
        try:
            old, smart = bool(node.selected), node.getProperty("__smart_selected")
            opening = old, smart
            expected_smart = False if old and not wanted else smart
            if old != wanted:
                node.selected = wanted
            if node.getProperty("__smart_selected") != expected_smart:
                node.setProperty("__smart_selected", expected_smart)
            if (
                bool(node.selected) != wanted
                or node.getProperty("__smart_selected") != expected_smart
            ):
                raise RuntimeError(
                    "native selection flags did not retain the requested state"
                )
            verified.append((row, wanted, expected_smart))
        except Exception as error:  # noqa: BLE001 - native selection boundary
            failures[row.key] = str(error)
            if opening is None:
                continue
            old, smart = opening
            try:
                if bool(node.selected) != old:
                    node.selected = old
                if node.getProperty("__smart_selected") != smart:
                    node.setProperty("__smart_selected", smart)
                if (
                    bool(node.selected) != old
                    or node.getProperty("__smart_selected") != smart
                ):
                    raise RuntimeError("opening selection flags were not retained")
            except Exception as restore:  # noqa: BLE001 - native selection recovery
                failures[row.key] += f"; selection may remain partial: {restore}"
    canvas.refreshAll()
    for row, wanted, smart in verified:
        try:
            if (
                bool(row.node.selected) != wanted
                or row.node.getProperty("__smart_selected") != smart
            ):
                raise RuntimeError(
                    "native selection flags changed during canvas refresh"
                )
        except Exception as error:  # noqa: BLE001 - native selection verification
            failures[row.key] = str(error)
    return failures


def show(qt: Any, parent: Any) -> Any:
    """Open an owned editable table; drain callbacks on Close or setup failure."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Keep cell edits until Apply or Refresh; synchronize selection explicitly."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(800, 560)
            self.stack_box = gui.QVBoxLayout(self)
            self.status_line = gui.QLabel(
                "Shape-local X/Y. Refresh discards cell edits.", self
            )
            self.stack_box.addWidget(self.status_line)
            self.signal_scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )
            self.snapshot_data: Snapshot | None = None

        def build_controls(self) -> None:
            """Build fallible controls under the outer owned-window cleanup guard."""
            self.node_table = gui.QTableWidget(0, 7, self)
            self.node_table.setHorizontalHeaderLabels(
                ["Shape", "Contour", "Node", "X", "Y", "Type", "State"]
            )
            self.node_table.setSelectionBehavior(gui.QAbstractItemView.SelectRows)
            self.node_table.setSelectionMode(gui.QAbstractItemView.ExtendedSelection)
            self.stack_box.addWidget(self.node_table)
            for text, action in (
                ("Refresh", self.refresh_nodes),
                ("Read Canvas Selection", self.read_selection),
                ("Apply", self.write_cells),
            ):
                button = gui.QPushButton(text, self)
                self.stack_box.addWidget(button)
                self.signal_scope.connect(
                    button.clicked, lambda *args, call=action: call()
                )
            self.signal_scope.connect(
                self.node_table.itemSelectionChanged,
                lambda *args: self.write_selection(),
            )
            self.signal_scope.connect(
                self.destroyed, lambda *args: self.release_owner()
            )

        def fill_nodes(self, snapshot: Snapshot, kept: dict[Key, str]) -> None:
            """Publish every row; only safe coordinate cells are editable."""
            self.node_table.blockSignals(True)
            try:
                self.node_table.setRowCount(len(snapshot.rows))
                for index, row in enumerate(snapshot.rows):
                    texts = [
                        *(str(i) for i in row.key),
                        "" if row.x is None else repr(row.x),
                        "" if row.y is None else repr(row.y),
                        row.kind,
                        "Kept: " + (kept.get(row.key) or row.kept)
                        if kept.get(row.key) or row.kept
                        else "Editable",
                    ]
                    for column, text in enumerate(texts):
                        item = gui.QTableWidgetItem(text)
                        flags = core.Qt.ItemIsEnabled | core.Qt.ItemIsSelectable
                        if column in (3, 4) and not row.kept:
                            flags |= core.Qt.ItemIsEditable
                        item.setFlags(int(flags))
                        self.node_table.setItem(index, column, item)
                    area = gui.QTableWidgetSelectionRange(index, 0, index, 6)
                    self.node_table.setRangeSelected(area, row.selected)
            finally:
                self.node_table.blockSignals(False)
            self.snapshot_data = snapshot

        def refresh_nodes(self) -> None:
            """Read current-layer rows; clear stale state on capture failure."""
            try:
                self.fill_nodes(capture_nodes(), {})
                self.status_line.setText(
                    f"{len(self.snapshot_data.rows)} rows. Edit X/Y, then Apply."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.snapshot_data = None
                self.node_table.setRowCount(0)
                self.status_line.setText(str(error))

        def write_cells(self) -> None:
            """Report a completed write even when its separate display read fails."""
            try:
                if self.snapshot_data is None:
                    raise ValueError("Refresh the node table first.")
                cells = {
                    row.key: tuple(
                        str(properties.value(self.node_table.item(index, col), "text"))
                        for col in (3, 4)
                    )
                    for index, row in enumerate(self.snapshot_data.rows)
                    if row.node is not None
                }
                result = apply_edits(self.snapshot_data, cells)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))
                return
            message = (
                f"Changed {result.changed} nodes; kept {len(result.kept)} attempted rows. "
                + (
                    "Apply is recorded as one Undo step."
                    if result.changed
                    else "No coordinate write."
                )
            )
            try:
                fresh = capture_nodes(facts=result.facts)
                if fresh.context != self.snapshot_data.context:
                    raise ValueError(
                        "Current glyph changed after Apply; Refresh the table."
                    )
                self.fill_nodes(fresh, result.kept)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.snapshot_data = None
                self.node_table.setRowCount(0)
                message += f" Refresh failed: {error}"
            self.status_line.setText(message)

        def write_selection(self) -> None:
            """Route table row selection to the active canvas."""
            try:
                if self.snapshot_data is None:
                    return
                model = self.node_table.selectionModel()
                indices = properties.value(model, "selectedIndexes")
                keys = {
                    self.snapshot_data.rows[int(properties.value(index, "row"))].key
                    for index in indices
                }
                failures = select_nodes(self.snapshot_data, keys)
                self.status_line.setText(
                    "Selection synchronized."
                    if not failures
                    else "; ".join(
                        f"Unsynced row {key}: {reason}"
                        for key, reason in failures.items()
                    )
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def read_selection(self) -> None:
            """Read canvas selection without replacing staged numeric cells."""
            try:
                old = self.snapshot_data
                if old is None:
                    raise ValueError("Refresh the node table first.")
                fresh = capture_nodes(facts=old.facts)
                if (
                    old is None
                    or old.context != fresh.context
                    or len(old.rows) != len(fresh.rows)
                    or any(
                        not same_geometry(a, b)
                        for a, b in zip(old.rows, fresh.rows, strict=True)
                    )
                ):
                    raise ValueError(
                        "Node geometry changed; Refresh before reading selection."
                    )
                self.node_table.blockSignals(True)
                try:
                    for index, row in enumerate(fresh.rows):
                        self.node_table.setRangeSelected(
                            gui.QTableWidgetSelectionRange(index, 0, index, 6),
                            row.selected,
                        )
                finally:
                    self.node_table.blockSignals(False)
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def release_owner(self) -> None:
            self.signal_scope.finish(destroyed=True)
            self.snapshot_data = None
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            if not self.signal_scope.finish():
                event.ignore()
                return
            self.snapshot_data = None
            if self in _PANELS:
                _PANELS.remove(self)
            event.accept()
            self.deleteLater()

    panel = Panel()
    _PANELS.append(panel)
    try:
        panel.build_controls()
        panel.refresh_nodes()
        panel.show()
    except Exception:
        if panel.signal_scope.finish():
            _PANELS.remove(panel)
            panel.deleteLater()
        raise
    return panel


def main() -> None:
    """Use FontLab's existing event loop and parent window."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
