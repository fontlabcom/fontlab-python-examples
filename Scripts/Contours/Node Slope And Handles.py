# this_file: Scripts/Contours/Node Slope And Handles.py
# SPDX-License-Identifier: Apache-2.0
"""Set selected node slopes and cubic handle lengths in a non-modal panel.

What: Copy a slope, use each master's italic angle, flip the slope or pivot at the
top or bottom selected node. Set cubic handle proportions or Hobby tensions.
How: Slope is dx/dy; selected nodes keep y. Each moved on-curve node carries
its adjacent unselected handles by the same offset, including at a closed
contour's wrap. Selected handles use their own slope targets.
Curve modes require both segment endpoints selected. Handle rays stay fixed;
Proportions measures length against the endpoint chord. Hobby uses the two
endpoint tangent angles and independent positive tensions. Copy Proportions
reads exactly one selected cubic. Closing cubics are included; open ends stay.
Why: Contour > Align Points and Contour > Handles > Harmonize serve direct edits. This
panel adds explicit reusable numbers, two handle tensions and a batch preview.
Use: Select nodes, run the tool, choose the mode and inspect the table. Reload
selection after changing glyphs. Each Apply is recorded as one Undo step.
Benefit: Repeat the same numeric rule across selected glyphs and masters.
Selection is read separately in each master. Automatic layers, shared outlines,
scaled or rotated shapes and quadratic contours are kept. No node is inserted,
deleted or retyped. Zero handle rays and zero chords are kept. General node
conversion, retraction and Tunni editing remain native or existing tools.
The preview lists each changed node's old and planned coordinates. Read-back
uses the App comparison epsilon; native coordinate storage remains subject to
FontLab's rounding preference.

Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0.

Credit: Independent behaviour rewrite after Vassil Kateliev and Karandash Type
Foundry, kateliev/TypeRig, MPL-2.0. Ideas: node_slope.py and curve.py toolbars.
Repository: https://github.com/kateliev/TypeRig . No source code copied.
"""

import math
from itertools import pairwise
from time import monotonic
from typing import Any, NamedTuple

import fly.ap.outline_writer as writer

TITLE = "Node Slope And Handles"
KEY = "numeric_node_slope_handles"
MODES = ("Slope", "Proportions", "Hobby")
# This comparison tolerance is not measured natively; use the App epsilon
# to report coordinate differences instead of assuming a rounding allowance.
READBACK_TOLERANCE = writer.EPSILON
Move = tuple[Any, float, float]
Position = tuple[int, int]
Targets = dict[Position, tuple[float, float]]


class ContourSnapshot(NamedTuple):
    """Retain one ordered node-wrapper read; positions identify nodes within it."""

    nodes: tuple[Any, ...]
    closed: bool
    is_tt: bool


def snapshot_contour(contour: Any) -> ContourSnapshot:
    """Read each native node getter once; reuse an existing snapshot unchanged."""
    if isinstance(contour, ContourSnapshot):
        return contour
    return ContourSnapshot(
        tuple(contour.nodes()), bool(contour.closed), bool(contour.isTT)
    )


def slope_of(nodes: list[Any]) -> float:
    """Measure dx/dy between the lowest and highest selected nodes."""
    if len(nodes) < 2:
        raise ValueError("Select at least two nodes with different y coordinates.")
    low, high = min(nodes, key=lambda n: n.y), max(nodes, key=lambda n: n.y)
    if high.y == low.y:
        raise ValueError("A horizontal selection has no finite dx/dy slope.")
    value = (float(high.x) - float(low.x)) / (float(high.y) - float(low.y))
    if not math.isfinite(value):
        raise ValueError("Node coordinates must be finite.")
    return value


def slope_moves(nodes: list[Any], value: float, top: bool, flip: bool) -> list[Move]:
    """Resolve positional slope targets against this exact node snapshot."""
    indexed = {(0, i): n for i, n in enumerate(nodes)}
    return [
        (indexed[key], x, y)
        for key, (x, y) in slope_targets(indexed, value, top, flip).items()
    ]


def slope_targets(
    nodes: dict[Position, Any], value: float, top: bool, flip: bool
) -> Targets:
    """Key selected-node slope targets by contour/node positions, keeping y."""
    if not math.isfinite(value):
        raise ValueError("Enter a finite dx/dy slope.")
    if len(nodes) < 2:
        return {}
    if min(n.y for n in nodes.values()) == max(n.y for n in nodes.values()):
        raise ValueError(
            "Select nodes with different y coordinates; horizontal nodes kept."
        )
    pivot = (max if top else min)(nodes.values(), key=lambda n: n.y)
    rate = -value if flip else value
    result = {
        key: (float(pivot.x) + (float(n.y) - float(pivot.y)) * rate, float(n.y))
        for key, n in nodes.items()
    }
    if any(not math.isfinite(x) or not math.isfinite(y) for x, y in result.values()):
        raise ValueError("Node coordinates must be finite.")
    return {
        key: target
        for key, target in result.items()
        if (nodes[key].x, nodes[key].y) != target
    }


def carry_handles(contours: list[ContourSnapshot], moves: Targets) -> Targets:
    """Carry adjacent unselected off-curves with their moved on-curve owner."""
    result = dict(moves)
    for contour_index, contour in enumerate(contours):
        nodes = contour.nodes
        for index, node in enumerate(nodes):
            key = contour_index, index
            if not node.isOn() or key not in moves:
                continue
            x, y = moves[key]
            for adjacent in (index - 1, index + 1):
                if not contour.closed and not 0 <= adjacent < len(nodes):
                    continue
                handle_index = adjacent % len(nodes)
                handle = nodes[handle_index]
                handle_key = contour_index, handle_index
                if handle.isOn() or handle.selected or handle_key in result:
                    continue
                target = float(handle.x) + x - node.x, float(handle.y) + y - node.y
                if not all(math.isfinite(v) for v in target):
                    raise ValueError("Handle coordinates must be finite.")
                result[handle_key] = target
    return result


def coordinate_rows(
    contours: list[ContourSnapshot], moves: Targets
) -> list[writer.Change]:
    """Show one exact old/planned coordinate pair per changed native node."""
    rows = []
    for (contour_index, node_index), (x, y) in moves.items():
        n = contours[contour_index].nodes[node_index]
        rows.append(
            writer.Change(
                f"contour {contour_index + 1} node {node_index}",
                f"{float(n.x)!r}, {float(n.y)!r}",
                f"{x!r}, {y!r}",
                [(n, x, y)],
            )
        )
    return rows


def segments(contour: Any) -> list[list[Any]]:
    """Read selected cubic spans, including a closed contour's wrapped span."""
    snapshot = snapshot_contour(contour)
    return [[snapshot.nodes[i] for i in span] for span in segment_indices(snapshot)]


def segment_indices(contour: ContourSnapshot) -> list[tuple[int, ...]]:
    """Find cubic spans by position within the retained ordered snapshot."""
    if contour.is_tt:
        return []
    nodes = contour.nodes
    ends = [i for i, n in enumerate(nodes) if n.isOn()]
    pairs = list(pairwise(ends))
    if contour.closed and ends:
        pairs.append((ends[-1], ends[0] + len(nodes)))
    return [
        tuple(i % len(nodes) for i in range(a, b + 1))
        for a, b in pairs
        if b - a == 3 and nodes[a].selected and nodes[b % len(nodes)].selected
    ]


def proportions(contour: Any) -> tuple[float, float]:
    """Read one selected cubic's handle lengths relative to its chord."""
    spans = segments(contour)
    if len(spans) != 1:
        raise ValueError("Select exactly one cubic segment with both endpoints.")
    p, c, d, q = spans[0]
    if any(not math.isfinite(v) for n in (p, c, d, q) for v in (n.x, n.y)):
        raise ValueError("Handle coordinates must be finite.")
    chord = math.hypot(q.x - p.x, q.y - p.y)
    if not chord:
        raise ValueError("The selected segment has a zero chord.")
    return math.hypot(c.x - p.x, c.y - p.y) / chord, math.hypot(
        d.x - q.x, d.y - q.y
    ) / chord


def hobby_ratio(theta: float, phi: float) -> float:
    """Evaluate Hobby's tangent-angle velocity factor at unit tension."""
    s, t, u, v = math.sin(theta), math.sin(phi), math.cos(theta), math.cos(phi)
    numerator = 2 + math.sqrt(2) * (s - t / 16) * (t - s / 16) * (u - v)
    denominator = 3 * (1 + (math.sqrt(5) - 1) / 2 * u + (3 - math.sqrt(5)) / 2 * v)
    if denominator <= 1e-9:
        raise ValueError("Hobby tangents turn too far; segment kept.")
    result = numerator / denominator
    if not math.isfinite(result) or result <= 0:
        raise ValueError("Hobby handle length is not positive; segment kept.")
    return result


def handle_moves(contour: Any, mode: str, first: float, second: float) -> list[Move]:
    """Resolve positional handle targets against one retained node snapshot."""
    snapshot = snapshot_contour(contour)
    return [
        (snapshot.nodes[index], x, y)
        for index, (x, y) in handle_targets(snapshot, mode, first, second).items()
    ]


def handle_targets(
    contour: ContourSnapshot, mode: str, first: float, second: float
) -> dict[int, tuple[float, float]]:
    """Keep tangent rays; key proportional or Hobby targets by node index."""
    if mode not in MODES[1:] or not all(
        math.isfinite(v) and v >= 0 for v in (first, second)
    ):
        raise ValueError("Use finite nonnegative proportions or positive tensions.")
    if mode == "Hobby" and min(first, second) <= 0:
        raise ValueError("Hobby tensions must be positive.")
    moves = {}
    for indices in segment_indices(contour):
        p, c, d, q = [contour.nodes[i] for i in indices]
        chord = math.hypot(q.x - p.x, q.y - p.y)
        left, right = math.hypot(c.x - p.x, c.y - p.y), math.hypot(d.x - q.x, d.y - q.y)
        if not chord or not left or not right:
            continue
        a, b = first, second
        if mode == "Hobby":
            direction = math.atan2(q.y - p.y, q.x - p.x)
            theta = math.atan2(c.y - p.y, c.x - p.x) - direction
            phi = direction - math.atan2(q.y - d.y, q.x - d.x)
            a, b = hobby_ratio(theta, phi) / first, hobby_ratio(phi, theta) / second
        for index, base, length, ratio in (
            (indices[1], p, left, a),
            (indices[2], q, right, b),
        ):
            node = contour.nodes[index]
            x = float(base.x) + (node.x - base.x) / length * chord * ratio
            y = float(base.y) + (node.y - base.y) / length * chord * ratio
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Handle coordinates must be finite.")
            if (node.x, node.y) != (x, y):
                moves[index] = x, y
    return moves


def changes(
    layer: Any, mode: str, first: float, second: float, top: bool, flip: bool
) -> list[writer.Change]:
    """Keep unsafe items as rows and plan the remaining contour coordinates."""
    shapes, notes = writer.outline_shapes(layer)
    contours = [snapshot_contour(c) for s in shapes for c in s.contours if not c.isTT]
    rows = writer.note_rows(notes)
    if any(c.isTT for s in shapes for c in s.contours):
        rows.append(writer.Change("quadratic contours", "", "kept"))
    if mode == "Slope":
        nodes = {
            (ci, ni): n
            for ci, c in enumerate(contours)
            for ni, n in enumerate(c.nodes)
            if n.selected
        }
        try:
            moves = carry_handles(contours, slope_targets(nodes, first, top, flip))
            rows.extend(
                coordinate_rows(contours, moves)
                if moves
                else [
                    writer.Change(
                        "selected nodes",
                        str(len(nodes)),
                        "kept: no selected node needs movement",
                    )
                ]
            )
        except ValueError as error:
            rows.append(writer.Change("selected nodes", "", f"kept: {error}"))
        return rows
    for i, contour in enumerate(contours, 1):
        try:
            for index, indices in enumerate(segment_indices(contour), 1):
                p, c, d, q = [contour.nodes[n] for n in indices]
                if any((a.x, a.y) == (b.x, b.y) for a, b in ((p, q), (p, c), (q, d))):
                    rows.append(
                        writer.Change(
                            f"contour {i} segment {index}",
                            "",
                            "kept: zero chord or handle ray",
                        )
                    )
            moves = {
                (i - 1, index): point
                for index, point in handle_targets(contour, mode, first, second).items()
            }
            rows.extend(
                coordinate_rows(contours, moves)
                if moves
                else [
                    writer.Change(f"contour {i}", "", "kept: no movable selected cubic")
                ]
            )
        except ValueError as error:
            rows.append(writer.Change(f"contour {i}", "", f"kept: {error}"))
    return rows


class CoordinateEditor(writer.Editor):
    """Write existing coordinates; return App read-back mismatch descriptions."""

    def write(self, layer: Any, steps: list[Any]) -> None:
        for moves in steps:
            for node, x, y in moves:
                node.x, node.y = x, y

    def check(self, prepared: list[tuple[Any, list[Any]]]) -> list[str]:
        missed = [
            f"{layer.name}: coordinates"
            for layer, steps in prepared
            if any(
                not math.isfinite(n.x)
                or not math.isfinite(n.y)
                or abs(n.x - x) > READBACK_TOLERANCE
                or abs(n.y - y) > READBACK_TOLERANCE
                for moves in steps
                for n, x, y in moves
            )
        ]
        return missed


def selected_contours() -> list[Any]:
    """Read one current layer for Copy actions; refuse ambiguous selections."""
    import fly.ap.layer_selection as selection

    snapshot = selection.capture(deadline=monotonic() + 2)
    layers = {int(item.layer.id): item.layer for item in snapshot.occurrences}
    if len(layers) != 1:
        raise ValueError("Open one glyph layer for Copy.")
    shapes, _ = writer.outline_shapes(next(iter(layers.values())))
    return [c for s in shapes for c in s.contours if not c.isTT]


def panel_type() -> type:
    """Build the non-modal App panel only inside the native host."""
    import fly.ap.outline_panel as panel
    import fly.ap.scripting as scripting  # noqa: PLR0402 - retain the Fly module import
    from fly import qt

    class NumericPanel(panel.panel_type()):
        TITLE, KEY, ACTION, DONE, UNIT = (
            TITLE,
            KEY,
            "Apply",
            "Changed",
            "coordinate group",
        )

        def build_controls(self) -> None:
            self.mode_box = qt.QtGui.QComboBox()
            self.mode_box.addItems(list(MODES))
            self.first_value = self.spin(-100, 100, 0.3, decimals=6)
            self.second_value = self.spin(0, 100, 0.3, decimals=6)
            self.first_label = qt.QtGui.QLabel()
            self.second_label = qt.QtGui.QLabel()
            self.per_master_italic = qt.QtGui.QCheckBox(
                "Use each master's italic angle"
            )
            self.top_pivot = qt.QtGui.QCheckBox("Pivot at highest selected node")
            self.flip_slope = qt.QtGui.QCheckBox("Flip slope horizontally")
            self.add_row("Mode", self.mode_box)
            self.add_row("", self.first_label, self.first_value)
            self.add_row("", self.second_label, self.second_value)
            self.add_row("", self.per_master_italic)
            for tick in (self.top_pivot, self.flip_slope):
                self.add_row("", tick)
                self.watch(tick.toggled)
            self.watch(self.mode_box.currentIndexChanged, self.mode_changed)
            self.watch(self.per_master_italic.toggled, self.mode_changed)
            for title, action in (
                ("Copy Slope", "slope"),
                ("Use Italic Angles", "italic"),
                ("Copy Proportions", "handles"),
            ):
                button = qt.QtGui.QPushButton(title)
                self.add_row("", button)
                self.watch(
                    button.clicked, lambda action=action: self.copy_values(action)
                )
            self.update_mode_fields()

        def update_mode_fields(self) -> None:
            """Label values in their actual units; disable unrelated controls."""
            mode = MODES[self.mode_box.currentIndex]
            slope = mode == "Slope"
            self.first_label.setText(
                {
                    "Slope": "Slope (dx/dy)",
                    "Proportions": "First handle / chord",
                    "Hobby": "First Hobby tension",
                }[mode]
            )
            self.second_label.setText(
                "Second Hobby tension" if mode == "Hobby" else "Second handle / chord"
            )
            self.first_value.setRange(
                -100 if slope else (0.000001 if mode == "Hobby" else 0), 100
            )
            self.second_value.setRange(0.000001 if mode == "Hobby" else 0, 100)
            self.second_value.setEnabled(not slope)
            self.second_label.setEnabled(not slope)
            self.per_master_italic.setEnabled(slope)
            self.first_value.setEnabled(
                not (slope and self.per_master_italic.isChecked())
            )
            for tick in (self.top_pivot, self.flip_slope):
                tick.setEnabled(slope)

        def mode_changed(self) -> None:
            """Update mode-specific controls before recomputing the preview."""
            self.update_mode_fields()
            self.refresh()

        def intro(self) -> str:
            guidance = super().intro()
            if self.package is None or not self.glyphs:
                return guidance
            return (
                guidance
                + " · Slope uses dx/dy and carries adjacent unselected handles; proportions use chord length; Hobby uses positive tensions (1 = unit). Select both cubic endpoints."
            )

        def copy_values(self, action: str) -> None:
            try:
                if action == "italic":
                    package = scripting.current_package(self.package_id)
                    if package is None:
                        raise ValueError("Open the bound font first.")
                    value = -math.tan(math.radians(float(package.italicAngle_value)))
                    self.mode_box.setCurrentIndex(0)
                    self.per_master_italic.setChecked(True)
                else:
                    self.per_master_italic.setChecked(False)
                    contours = [snapshot_contour(c) for c in selected_contours()]
                    if action == "slope":
                        value = slope_of(
                            [n for c in contours for n in c.nodes if n.selected]
                        )
                        self.mode_box.setCurrentIndex(0)
                    else:
                        chosen = [c for c in contours if segments(c)]
                        if len(chosen) != 1:
                            raise ValueError("Select exactly one cubic segment.")
                        value, second = proportions(chosen[0])
                        if second > 100:
                            raise ValueError(
                                "Handle proportion exceeds the field range."
                            )
                        self.second_value.setValue(second)
                        self.mode_box.setCurrentIndex(1)
                if not -100 <= value <= 100:
                    raise ValueError("Copied value exceeds the field range.")
                self.first_value.setValue(value)
                self.refresh()
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status.setText(str(error))

        def planner(self) -> writer.Planner:
            mode, a, b = (
                MODES[self.mode_box.currentIndex],
                float(self.first_value.value),
                float(self.second_value.value),
            )
            top, flip = self.top_pivot.isChecked(), self.flip_slope.isChecked()
            slopes = {}
            use_italic = mode == "Slope" and self.per_master_italic.isChecked()
            if use_italic:
                import fly.ap.master_angles as angles

                package = scripting.current_package(self.package_id)
                if package is None:
                    raise ValueError("Open the bound font first.")
                slopes = {
                    master: -math.tan(math.radians(angle))
                    for master, angle in angles.capture(package).angles
                }

            def plan(glyph: Any, master: str, layer: Any) -> list[writer.Change]:
                value = slopes.get(master) if use_italic else a
                if value is None:
                    raise ValueError(
                        f"Master {master!r} not found in the font's italic angles; reload selection."
                    )
                return changes(layer, mode, value, b, top, flip)

            return plan

        def editor(self) -> writer.Editor:
            return CoordinateEditor()

    return NumericPanel


def main() -> Any:
    """Show the retained panel; contain native read and deadline errors."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - retain the Fly module import

    try:
        return scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")
        return None


if __name__ == "__main__":
    main()
