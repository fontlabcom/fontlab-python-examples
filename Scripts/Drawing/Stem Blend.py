# this_file: Scripts/Drawing/Stem Blend.py
# SPDX-License-Identifier: Apache-2.0
"""What: Write a stem-compensated blend into a new layer of the current glyph.
How: Divide target stems by scale to choose independent X/Y interpolation
fractions. Unslant, blend, scale and reslant. The final stems match the typed
measurements when the source stems interpolate linearly.
Why: Make scaled lettering at a requested stem size without changing masters.
Usage: Open a glyph. Choose two source layers. Enter measured source and target
stems and scale factors. Build, inspect the output name, then Create Layer.
The layer name is Stem <vertical>x<horizontal> (<current master>), for example
Stem 75x60 (Light). Names containing @ or #, starting with |temp|, or matching
a master name are refused. An existing layer name is refused. Each new layer
is recorded as one Undo step through App history. The new layer becomes the
active layer.
Benefit: Keep native font-unit geometry without an artwork import transform.

The angle starts at minus the current master's italic angle; positive means
that the top moves right. Refresh Sources reloads layer choices and the angle.
Targets divided by scale must lie between the measured source stems. Equal
stems, components, shape transforms and incompatible paths are refused.
TrueType off-curves stay quadratic, including implied on-curve midpoints.
The new layer keeps the first source's advance. Anchors, hints, node flags
and other source metadata are not copied. Automatic-layer owners and bases of
automatic composites are kept unchanged and named in the refusal message.
Copy SVG is secondary artwork only. SVG import may rescale or reposition it;
no SVG import preserves scale by this tool's guarantee.
No stored axis setup, extrapolation or batch target baking is provided.
Use native Font > Generate Instance for native instance generation.
Requires FontLab 9, Python 3.11, Fly and App >= 0.2.150.dev0.

Credit: Independent behaviour rewrite of Delta.py and DeltaNew.py by Vassil
Kateliev, TypeRig, kateliev/TypeRig, MPL-2.0.
https://github.com/kateliev/TypeRig
No source code, comments, icons or preset formats are copied.
Read-back allows coordinate changes up to 1e-5 units. Advance is checked
against
its detached value read immediately after the native setter applies the current
rounding preference, with the same tolerance. The coordinate tolerance comes
from native source; it is unmeasured in native FontLab execution.

"""

import math
from html import escape
from pathlib import Path
from time import monotonic
from typing import Any

TITLE = "Stem Blend"
Point = tuple[float, float, bool]
Contour = tuple[bool, list[Point]] | tuple[bool, list[Point], bool]
Contours = list[Contour]
_PANELS: list[Any] = []



# Source-derived tolerances; not measured in native FontLab execution.
COORDINATE_TOLERANCE = 1e-5


def stored_outline_matches(actual: list, expected: list) -> bool:
    """Accept native integer snapping; require exact topology and node kinds."""
    if len(actual) != len(expected):
        return False
    for (closed, points, tt), (want_closed, wanted, want_tt) in zip(
        actual, expected, strict=True
    ):
        if (closed, tt, len(points)) != (want_closed, want_tt, len(wanted)):
            return False
        for (x, y, on), (wx, wy, won) in zip(points, wanted, strict=True):
            if on != won or not (
                abs(x - wx) <= COORDINATE_TOLERANCE
                and abs(y - wy) <= COORDINATE_TOLERANCE
            ):
                return False
    return True


def blend_contours(
    first: Contours,
    second: Contours,
    stems: tuple[float, float, float, float],
    target: tuple[float, float],
    scales: tuple[float, float],
    angle: float,
) -> Contours:
    """Use independent measured-stem fractions; never change source coordinates."""
    values = (*stems, *target, *scales, angle)
    if not all(math.isfinite(v) for v in values) or min(*stems, *target, *scales) <= 0:
        raise ValueError("Stems and scales must be finite positive numbers.")
    if abs(angle) >= 85:
        raise ValueError("Use a slant angle between -85 and 85 degrees.")
    a, b, c, d = stems
    if a == b or c == d:
        raise ValueError("Each pair of source stems must differ.")
    tx, ty = (
        (target[0] / scales[0] - a) / (b - a),
        (target[1] / scales[1] - c) / (d - c),
    )
    if not 0 <= tx <= 1 or not 0 <= ty <= 1:
        raise ValueError(
            "Target stems divided by scale must be between the measured source stems."
        )
    if not first or len(first) != len(second):
        raise ValueError("Use two nonempty layers with equal contour counts.")
    tangent = math.tan(math.radians(angle))
    result = []
    for left, right in zip(first, second, strict=True):
        closed, one, tt = contour_parts(left)
        other_closed, two, other_tt = contour_parts(right)
        if (
            closed != other_closed
            or tt != other_tt
            or not one
            or [p[2] for p in one] != [p[2] for p in two]
        ):
            raise ValueError("Contour closure, node count and node types must match.")
        points = []
        for (x1, y1, on), (x2, y2, _) in zip(one, two, strict=True):
            y = (y1 + (y2 - y1) * ty) * scales[1]
            u1, u2 = x1 - y1 * tangent, x2 - y2 * tangent
            x = (u1 + (u2 - u1) * tx) * scales[0] + y * tangent
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Blended coordinates are outside the finite range.")
            points.append((x, y, on))
        result.append((closed, points, tt))
    return result


def contour_parts(contour: Contour) -> tuple[bool, list[Point], bool]:
    """Read an explicit TT flag; older detached cubic inputs default to cubic."""
    return contour[0], contour[1], contour[2] if len(contour) == 3 else False


def path_text(closed: bool, points: list[Point], tt: bool = False) -> str:
    """Serialize complete paths; refuse malformed control runs instead of dropping nodes."""
    if tt and closed and points and not any(p[2] for p in points):
        x, y = ((points[-1][i] + points[0][i]) / 2 for i in (0, 1))
        points = [(x, y, True), *points]
    if not points or not any(p[2] for p in points):
        raise ValueError("A contour must contain an on-curve node.")
    if not all(math.isfinite(v) for p in points for v in p[:2]):
        raise ValueError("Outline coordinates must be finite.")
    start = next(i for i, p in enumerate(points) if p[2])
    if not closed and (start != 0 or not points[-1][2]):
        raise ValueError("An open contour must begin and end on-curve.")
    nodes = points[start:] + points[:start] if closed else points
    commands = [f"M {nodes[0][0]:.17g} {nodes[0][1]:.17g}"]
    handles = []
    for x, y, on in nodes[1:] + (nodes[:1] if closed else []):
        if not on:
            handles.append((x, y))
            continue
        if tt and handles:
            for index, handle in enumerate(handles):
                end = (
                    (x, y)
                    if index == len(handles) - 1
                    else tuple(
                        handle[i] / 2 + handles[index + 1][i] / 2 for i in (0, 1)
                    )
                )
                commands.append("Q " + " ".join(f"{v:.17g}" for v in (*handle, *end)))
            handles = []
            continue
        if len(handles) > 2:
            raise ValueError("More than two controls between on-curve nodes.")
        prefix = ("L", "Q", "C")[len(handles)]
        coords = " ".join(f"{v:.17g}" for p in [*handles, (x, y)] for v in p)
        commands.append(f"{prefix} {coords}")
        handles = []
    if closed:
        commands.append("Z")
    return " ".join(commands)


def svg_text(label: str, contours: Contours) -> str:
    """Keep font-unit coordinates and invert SVG y exactly once."""
    if any(
        ord(c) < 32
        or c in "\u00a0\u2028\u2029\ufffe\uffff"
        or 0xD800 <= ord(c) <= 0xDFFF
        for c in label
    ):
        raise ValueError("The glyph name cannot be transferred exactly to SVG.")
    paths = [path_text(*contour_parts(contour)) for contour in contours]
    if not paths:
        raise ValueError("There is no outline to export.")
    points = [p for contour in contours for p in contour[1]]
    left, right = min(0.0, *(p[0] for p in points)), max(0.0, *(p[0] for p in points))
    bottom, top = min(0.0, *(p[1] for p in points)), max(0.0, *(p[1] for p in points))
    width, height = max(1.0, right - left), max(1.0, top - bottom)
    if not math.isfinite(width) or not math.isfinite(height):
        raise ValueError("The SVG frame is outside the finite range.")
    data = " ".join(paths)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{left:.17g} {-top:.17g} {width:.17g} {height:.17g}">\n'
        f'<title>{escape(label)}</title>\n<g transform="scale(1 -1)">'
        f'<path d="{data}" fill="black" fill-rule="nonzero"/></g>\n</svg>\n'
    )


def read_contours(layer: Any, deadline: float) -> Contours:
    """Read plain contour shapes with a deadline; refuse geometry that needs flattening."""
    result = []
    for shape in layer.shapes:
        if shape.isComponent or not shape.transform.isIdentity() or not shape.contours:
            raise ValueError(
                "Use plain contour shapes without components or shape transforms."
            )
        for contour in shape.contours:
            points = []
            for node in contour.nodes():
                if monotonic() >= deadline:
                    raise TimeoutError("Outline capture expired; Build again.")
                points.append((float(node.x), float(node.y), bool(node.isOn())))
            tt = bool(contour.isTT)
            path_text(bool(contour.closed), points, tt)
            result.append((bool(contour.closed), points, tt))
    return result


def capture_pair(first: str, second: str) -> tuple[str, Contours, Contours]:
    """Read both source layers twice and refuse a changed current font or glyph."""
    import fly.ap.node_coordinates as coordinates
    import fly.ap.scripting as scripting  # noqa: PLR0402

    deadline = monotonic() + 3.0
    snapshots = []
    for _ in range(2):
        package = scripting.current_package()
        if package is None:
            raise ValueError("Open a font and a glyph first.")
        glyph = coordinates.current_glyph(package)
        if glyph is None or int(glyph.package.id) != int(package.id):
            raise ValueError("Open a glyph in the current font.")
        layers = [glyph.findLayer(name) for name in (first, second)]
        if any(layer is None or layer.isNull for layer in layers):
            raise ValueError("Both named layers must exist in the current glyph.")
        data = [read_contours(layer, deadline) for layer in layers]
        snapshots.append(
            (
                int(package.id),
                int(glyph.id),
                tuple(int(layer.id) for layer in layers),
                str(glyph.name),
                *data,
            )
        )
    if snapshots[0] != snapshots[1] or monotonic() >= deadline:
        raise ValueError("Font, glyph or source geometry changed; Build again.")
    return snapshots[0][3], snapshots[0][4], snapshots[0][5]


def export_new(filename: str, content: str) -> None:
    """Write one detached SVG artifact; refuse overwriting an existing file."""
    path = Path(filename).expanduser()
    if not path.is_absolute() or path.suffix.lower() != ".svg" or not content:
        raise ValueError("Build a result and enter a new absolute .svg path.")
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(content)


def numbers(text: str, count: int) -> tuple[float, ...]:
    """Parse the exact count of space-separated finite numeric controls."""
    try:
        values = tuple(float(v) for v in text.split())
    except ValueError as error:
        raise ValueError("Use space-separated numbers.") from error
    if len(values) != count or not all(math.isfinite(v) for v in values):
        raise ValueError(f"Enter exactly {count} finite numbers.")
    return values


def current_context() -> tuple[Any, Any]:
    """Resolve an owned current glyph without reading native FontGate caches."""
    import fly.ap.node_coordinates as coordinates
    import fly.ap.scripting as scripting  # noqa: PLR0402

    package = scripting.current_package()
    if package is None:
        raise ValueError("Open a font and a glyph first.")
    glyph = coordinates.current_glyph(package)
    if glyph is None or int(glyph.package.id) != int(package.id):
        raise ValueError("Open a glyph in the current font.")
    return package, glyph


def source_options() -> tuple[list[str], float]:
    """Offer current-glyph layer names and the current master's rightward slant."""
    package, glyph = current_context()
    return [str(layer.name) for layer in glyph.layers], -float(
        package.italicAngle_value
    )


def checked_layer_name(name: str, masters: tuple[str, ...]) -> str:
    """Refuse native recipe, master and temporary-layer naming syntax."""
    if "@" in name or "#" in name or name.startswith("|temp|"):
        raise ValueError("Layer name must not contain @ or #, or start with |temp|.")
    if name.casefold() in {master.casefold() for master in masters}:
        raise ValueError("Layer name must not equal a master name.")
    return name


def prepare_blend(
    first: str, second: str, stems: tuple, target: tuple, scales: tuple, angle: float
) -> dict[str, Any]:
    """Bind a detached outline preview to its exact font, glyph, layers and advance."""
    package, glyph = current_context()
    identity = (int(package.id), int(glyph.id), str(package.master))
    label, one, two = capture_pair(first, second)
    blended = blend_contours(one, two, stems, target, scales, angle)
    name = checked_layer_name(
        f"Stem {target[0]:.12g}x{target[1]:.12g} ({package.master})",
        tuple(str(master) for master in package.masters),
    )
    if any(str(layer.name).casefold() == name.casefold() for layer in glyph.layers):
        raise ValueError(f"Kept {glyph.name}: layer '{name}' already exists.")
    advance = float(glyph.findLayer(first).advanceWidth)
    if not math.isfinite(advance):
        raise ValueError("The first source advance must be finite.")
    after_package, after_glyph = current_context()
    if identity != (
        int(after_package.id),
        int(after_glyph.id),
        str(after_package.master),
    ):
        raise ValueError("Font, glyph or current master changed; Build again.")
    return {
        "identity": identity,
        "label": label,
        "name": name,
        "sources": (first, second),
        "source_data": (one, two),
        "contours": blended,
        "advance": advance,
        "stems": stems,
        "target": target,
        "scales": scales,
        "angle": angle,
    }


def create_layer(plan: dict[str, Any], *, disclosure: dict[str, Any] | None = None) -> str:
    """Create one layer through App history and settle; reject stale or unsafe previews."""
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.layer_writer as writer
    from fly import fl, qt

    package, _ = current_context()
    checked_layer_name(plan["name"], tuple(str(master) for master in package.masters))
    fresh = prepare_blend(
        *plan["sources"], plan["stems"], plan["target"], plan["scales"], plan["angle"]
    )
    if fresh != plan:
        raise ValueError("Source or current context changed; Build again.")
    package, glyph = current_context()
    facts = history.scan_auto_facts(package)
    reason = history.refusal(facts, str(glyph.name), "geometry")
    if reason:
        raise ValueError(f"Kept {glyph.name}: {reason}")
    # Build detached native objects before history; no source shape is cloned.
    layer = fl.flLayer()
    layer.name, layer.advanceWidth = plan["name"], plan["advance"]
    stored_advance = float(layer.advanceWidth)
    shape = fl.flShape()
    for contour in plan["contours"]:
        closed, points, tt = contour_parts(contour)
        nodes = [
            fl.flNode(
                qt.QtCore.QPointF(x, y),
                nodeType="on" if on else ("off" if tt else "curve"),
            )
            for x, y, on in points
        ]
        shape.addContour(fl.flContour(nodes, closed=closed), False, False)
    layer.addShape(shape)
    added: list[Any] = []
    failures: list[Exception] = []

    def mutate() -> list[Any]:
        """Attach the prepared outline and return only the newly added body layer."""
        try:
            glyph.addLayer(layer)
        except Exception as error:  # noqa: BLE001 - retain attached layers in history even after a native failure
            failures.append(error)
        found = glyph.findLayer(plan["name"])
        if found is None or found.isNull:
            failures.append(RuntimeError("FontLab did not add the target layer."))
            return []
        added.append(found)
        try:
            writer.settle(found)
        except Exception as error:  # noqa: BLE001 - retain attached layers in history even after a native failure
            failures.append(error)
        return added

    def read_back() -> list[str]:
        """Verify coordinates, node kinds, closure and the source advance."""
        if failures:
            raise RuntimeError(str(failures[0])) from failures[0]
        found = glyph.findLayer(plan["name"])
        if found is None or found.isNull:
            return ["new layer is missing"]
        actual = read_contours(found, monotonic() + 3.0)
        expected = [contour_parts(contour) for contour in plan["contours"]]
        return (
            []
            if stored_outline_matches(actual, expected)
            and abs(float(found.advanceWidth) - stored_advance) <= COORDINATE_TOLERANCE
            else ["new layer outline or advance differs"]
        )

    result = history.commit(
        TITLE,
        [],
        [glyph],
        mutate,
        operation="geometry",
        facts=facts,
        read_back=read_back,
    )
    import fly.ap.edit_guards as _guards
    _guards.disclose(result, disclosure)
    if result.mismatches:
        raise RuntimeError(
            "Native changes may remain; use Edit > Undo. "
            + str(history.unstored_error(result.mismatches))
        )
    return _guards.append_note(f"{glyph.name}: '{plan['name']}' is recorded as one Undo step. The new layer becomes the active layer.", result)


def show(qt: Any, parent: Any) -> Any:
    """Show repeatable blend controls; keep SVG detached and invalidate on edits."""
    import fly.ap.draft_signals as signals
    import fly.ap.qt_properties as properties

    gui, core = qt.QtGui, qt.QtCore

    class Panel(gui.QWidget):
        """Own source controls, output and signal cleanup."""

        def __init__(self) -> None:
            gui.QWidget.__init__(self, parent, core.Qt.WindowFlags(core.Qt.Tool))
            self.setWindowTitle(TITLE)
            self.setAttribute(core.Qt.WA_QuitOnClose, False)
            self.resize(680, 640)
            self.box = gui.QVBoxLayout(self)
            self.status_line = gui.QLabel(
                "Build a blend, then Create Layer. The new layer becomes active.", self
            )
            self.box.addWidget(self.status_line)
            self.scope = signals.Scope(
                lambda error: self.status_line.setText(str(error))
            )
            self.scope.connect(self.destroyed, lambda *args: self.release_owner())
            form = gui.QFormLayout()
            self.box.addLayout(form)
            self.fields = []
            self.plan_data: dict[str, Any] | None = None
            labels = (
                "First layer",
                "Second layer",
                "Vertical stems: first second",
                "Horizontal stems: first second",
                "Target stems: vertical horizontal",
                "Scale factors: x y",
                "Slant angle: degrees",
                "New SVG file (absolute path)",
            )
            for label, initial in zip(
                labels, ("", "", "", "", "", "1 1", "0", ""), strict=True
            ):
                if len(self.fields) < 2:
                    field = gui.QComboBox(self)
                else:
                    field = gui.QLineEdit(self)
                    field.setText(initial)
                form.addRow(label, field)
                self.fields.append(field)
            self.result_field = gui.QPlainTextEdit(self)
            self.result_field.setReadOnly(True)
            self.box.addWidget(self.result_field)
            self.content = ""
            for index, field in enumerate(self.fields[:-1]):
                signal = field.currentIndexChanged if index < 2 else field.textChanged
                self.scope.connect(signal, lambda *args: self.clear_result())
            for label, action in (
                ("Build Blend", self.build_result),
                ("Create Layer", self.apply_result),
                ("Copy SVG", self.copy_result),
                ("Export SVG", self.save_result),
                ("Refresh Sources", self.refresh_sources),
            ):
                button = gui.QPushButton(label, self)
                self.box.addWidget(button)
                self.scope.connect(
                    button.clicked, lambda *args, action=action: action()
                )

            self.refresh_sources()

        def refresh_sources(self) -> None:
            """Reload layer pickers and slant without silently changing a built result."""
            self.clear_result()
            try:
                choices, angle = source_options()
                for index, field in enumerate(self.fields[:2]):
                    field.clear()
                    field.addItems(choices)
                    if choices:
                        field.setCurrentIndex(min(index, len(choices) - 1))
                self.fields[6].setText(f"{angle:g}")
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def clear_result(self) -> None:
            """Prevent exporting artwork from older control values."""
            self.content = ""
            self.plan_data = None
            self.result_field.setPlainText("")

        def build_result(self) -> None:
            """Read the current glyph and publish a complete validated SVG."""
            self.clear_result()
            try:
                values = [
                    str(properties.value(field, "currentText" if index < 2 else "text"))
                    for index, field in enumerate(self.fields)
                ]
                stems = numbers(values[2], 2) + numbers(values[3], 2)
                plan = prepare_blend(
                    values[0],
                    values[1],
                    stems,
                    numbers(values[4], 2),
                    numbers(values[5], 2),
                    numbers(values[6], 1)[0],
                )
                self.content = svg_text(plan["label"], plan["contours"])
                self.plan_data = plan
                self.result_field.setPlainText(self.content)
                self.status_line.setText(
                    f"New layer: {plan['name']}. Create Layer writes one Undo step and makes the new layer active."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(str(error))

        def apply_result(self) -> None:
            """Write only the displayed plan; require a new Build after every attempt."""
            import fly.ap.edit_guards as result_guards
            disclosure = {"pending_updates": (), "pending_note": ""}
            try:
                if self.plan_data is None:
                    raise ValueError("Build the blend first.")
                self.status_line.setText(result_guards.append_note(create_layer(self.plan_data, disclosure=disclosure), disclosure))
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.status_line.setText(result_guards.append_note(str(error), disclosure))
            finally:
                self.plan_data = None

        def copy_result(self) -> None:
            """Copy optional artwork without promising SVG import scale or position."""
            if not self.content:
                self.status_line.setText("Build the blend first.")
                return
            gui.QApplication.clipboard().setText(self.content)
            self.status_line.setText(
                "SVG copied. Artwork import may change its scale and position."
            )

        def save_result(self) -> None:
            """Save the visible detached artifact without a new font read."""
            try:
                export_new(str(properties.value(self.fields[-1], "text")), self.content)
                self.status_line.setText(
                    "SVG exported. Artwork import may change scale and position."
                )
            except (ValueError, RuntimeError, OSError) as error:
                self.status_line.setText(
                    f"{error} A failed write may leave a partial file."
                )

        def release_owner(self) -> None:
            """Release Python callbacks when the native parent is destroyed."""
            self.scope.finish(destroyed=True)
            if self in _PANELS:
                _PANELS.remove(self)

        def closeEvent(self, event: Any) -> None:
            """Disconnect before deletion; retain failed cleanup for retry."""
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
    """Use the existing FontLab application and main window."""
    from fly import fl, qt

    try:
        show(qt, fl.MainWindow())
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
