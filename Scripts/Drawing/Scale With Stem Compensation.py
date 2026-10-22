# this_file: Scripts/Drawing/Scale With Stem Compensation.py
# SPDX-License-Identifier: Apache-2.0
"""What: Scale selected glyphs with independent vertical/horizontal stem
compensation.
How: Each checked master row supplies two source layers, their measured stems,
target stems, scale X/Y and slant. Unslant all nodes, blend X/Y independently,
scale and reslant. Preview lists every glyph/master and output layer. Confirm,
then Create Layers. The entire batch is recorded as one Undo step.
Why: Plain scaling changes stems. Per-master stem measurements make derived
small caps or superiors without changing the source masters.
Usage: Select glyphs in the Font window. Use Selection, check target master
rows,
edit their source pairs and measurements, Preview, inspect kept rows, confirm.
Benefit: Generate many compensated glyph layers in one repeatable action.

Outputs are new auxiliary layers named master + suffix. Existing outputs are
kept. New names cannot contain @ or # or start with |temp|. No in-place
overwrite
or whole-font default is provided. Preview and Apply each scan dependencies
once;
control edits never scan fonts. Apply rechecks the displayed plan.
All nodes and controls use the same affine blend; TT contours remain quadratic,
including consecutive controls and implied on-curves. First-source node names,
raw flags and contour names are retained, with selection flags cleared. Advance
is first-source advance times scale X. Components, transforms, automatic or
locked
sources, custom node/contour properties and unsafe automatic dependants are
kept.
Anchors, guides, hints, element metadata and metrics expressions are not
copied.
Source layers stay unchanged. Slant defaults to minus the current master's
angle;
each table row can override it. Extrapolation, boundary-fix, stem probing and
saved table presets are not provided. Partial failures direct you to Edit >
Undo.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0. Non-modal panel.

Independent behaviour rewrite of DeltaMachine.py, Vassil Kateliev / Karandash
Type Foundry, kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
The small arithmetic helper reuses the Apache-2.0 Stem Blend implementation.
No TypeRig code, private identifiers, comments or assets copied.
Capture allows 3 seconds plus one second per selected glyph/master. A timeout
refuses the whole preview; select fewer glyphs.
Read-back allows coordinate changes up to 1e-5 units. Advance is checked
against
its detached value read immediately after the native setter applies the current
rounding preference, with the same tolerance. The coordinate tolerance comes
from native source; it is unmeasured in native FontLab execution.

"""

import math
from time import monotonic
from typing import Any

TITLE, KEY = "Scale With Stem Compensation", "scale_with_stem_compensation"
HEADERS = (
    "Use",
    "Master",
    "Source A",
    "Source B",
    "V A",
    "V B",
    "H A",
    "H B",
    "Target V",
    "Target H",
    "Scale X",
    "Scale Y",
    "Slant",
)


def checked_name(name: str) -> str:
    """Reject FontLab recipe, temporary and lossy text syntax."""
    if (
        not name.strip()
        or "@" in name
        or "#" in name
        or name.startswith("|temp|")
        or name.casefold().startswith(("mask", "img.", "bw."))
        or any(ord(c) < 32 or c in "\u00a0\u2028\u2029" for c in name)
    ):
        raise ValueError("Use a nonempty layer name without @, #, |temp| or reserved mask/img./bw. prefixes.")
    return name


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
    first: list, second: list, stems: tuple, target: tuple, scales: tuple, angle: float
) -> list:
    """Private Stem Blend arithmetic; preserve topology and transform every control."""
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
        raise ValueError("Target stems divided by scale must lie between source stems.")
    if not first or len(first) != len(second):
        raise ValueError("Use nonempty compatible source contours.")
    tangent, result = math.tan(math.radians(angle)), []
    for (closed, one, tt), (other_closed, two, other_tt) in zip(
        first, second, strict=True
    ):
        if (
            closed != other_closed
            or tt != other_tt
            or not one
            or [p[2] for p in one] != [p[2] for p in two]
        ):
            raise ValueError(
                "Closure, contour type, node count and node types must match."
            )
        points = []
        for (x1, y1, on), (x2, y2, _) in zip(one, two, strict=True):
            y = (y1 + (y2 - y1) * ty) * scales[1]
            u1, u2 = x1 - y1 * tangent, x2 - y2 * tangent
            x = (u1 + (u2 - u1) * tx) * scales[0] + y * tangent
            if not math.isfinite(x) or not math.isfinite(y):
                raise ValueError("Result is outside the finite coordinate range.")
            points.append((x, y, on))
        result.append((closed, points, tt))
    return result


def read_contours(layer: Any, deadline: float) -> tuple[list, list]:
    """Capture each contour once, including TT flag and stable index-based metadata."""
    if layer is None or layer.isNull or layer.autoLayer or layer.isLocked:
        raise ValueError("missing, locked or automatic source layer")
    data, metadata = [], []
    for shape in layer.shapes:
        if shape.isComponent or not shape.transform.isIdentity():
            raise ValueError("components or transformed source shapes")
        for contour in shape.contours:
            nodes = list(contour.nodes())
            if contour.getProperties() or any(
                n.getProperties() or n.getProperty("corner_smooth") is not None
                for n in nodes
            ):
                raise ValueError("custom node or contour properties")
            if monotonic() >= deadline:
                raise TimeoutError("Outline capture expired; select fewer glyphs.")
            data.append(
                (
                    bool(contour.closed),
                    [(float(n.x), float(n.y), bool(n.isOn())) for n in nodes],
                    bool(contour.isTT),
                )
            )
            metadata.append(
                (
                    str(contour.name),
                    tuple((str(n.name), int(n.nodeState) & ~0x20) for n in nodes),
                )
            )
    return data, metadata


def current_font(identity: int) -> Any:
    """Bind to the current font's fgId, never its label or wrapper identity."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    package = scripting.current_package()
    if package is None or int(package.fgId) != identity:
        raise ValueError("The selected font changed; Use Selection again.")
    return package


def survey(
    package: Any,
    names: list[str],
    configs: list[dict[str, Any]],
    suffix: str,
    facts: Any,
) -> list[dict[str, Any]]:
    """Plan selected glyphs times checked masters; retain every refused combination."""
    import fly.ap.history as history  # noqa: PLR0402

    if not names or not configs:
        raise ValueError("Select glyphs and check at least one master row.")
    if len({c["master"] for c in configs}) != len(configs):
        raise ValueError("Use each target master once.")
    deadline, rows = monotonic() + 3 + len(names) * len(configs), []
    masters = {str(m).casefold() for m in package.masters}
    for name in names:
        glyph = package.findName(name) if monotonic() < deadline else None
        for config in configs:
            row = {
                "name": name,
                "master": config["master"],
                "target": config["master"] + suffix,
                "note": "",
                "sources": None,
                "metadata": None,
                "result": None,
                "advance": None,
            }
            try:
                if monotonic() >= deadline:
                    raise TimeoutError("Outline capture expired; select fewer glyphs.")
                checked_name(row["target"])
                if config.get("error"):
                    raise ValueError(config["error"])
                if (
                    config["master"].casefold() not in masters
                    or row["target"].casefold() in masters
                ):
                    raise ValueError(
                        "choose an existing master and a nonempty auxiliary-layer suffix"
                    )
                if glyph is None or glyph.isNull:
                    raise ValueError("glyph disappeared")
                reason = history.refusal(facts, name, "geometry")
                if reason:
                    raise ValueError(reason)
                if any(
                    str(l.name).casefold() == row["target"].casefold()
                    for l in glyph.layers
                ):
                    raise ValueError("output layer already exists")
                a, b = (
                    glyph.findLayer(config["first"]),
                    glyph.findLayer(config["second"]),
                )
                one, meta = read_contours(a, deadline)
                two, other_meta = read_contours(b, deadline)
                row["sources"], row["metadata"] = (one, two), (meta, other_meta)
                row["result"] = blend_contours(
                    one,
                    two,
                    config["stems"],
                    config["target"],
                    config["scales"],
                    config["angle"],
                )
                row["advance"] = float(a.advanceWidth) * config["scales"][0]
                if not math.isfinite(row["advance"]):
                    raise ValueError("advance is outside the finite range")
            except (ValueError, RuntimeError) as error:
                row["note"] = str(error)
            rows.append(row)
    return rows


def make_plan(
    identity: int, names: list[str], configs: list[dict[str, Any]], suffix: str
) -> dict[str, Any]:
    """Take an explicit batch preview with one shared dependency scan."""
    import fly.ap.history as history  # noqa: PLR0402

    package = current_font(identity)
    facts = history.scan_auto_facts(package)
    return {
        "identity": identity,
        "names": list(names),
        "configs": configs,
        "suffix": suffix,
        "rows": survey(package, names, configs, suffix, facts),
    }


def apply_plan(plan: dict[str, Any], confirmed: bool) -> dict[str, Any]:
    """Create all ready layers through one history.commit, after rechecking Preview."""
    import fly.ap.contour_copy as copies
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.layer_writer as writer
    from fly import fl, qt

    if not confirmed:
        raise ValueError("Preview and confirm the new layers first.")
    package = current_font(plan["identity"])
    facts = history.scan_auto_facts(package)
    rows = survey(package, plan["names"], plan["configs"], plan["suffix"], facts)
    if rows != plan["rows"]:
        raise ValueError("Font or source data changed; Preview again.")
    configs = {c["master"]: c for c in plan["configs"]}
    prepared, owners = [], {}
    for row in rows:
        if row["note"]:
            continue
        glyph = package.findName(row["name"])
        source = glyph.findLayer(configs[row["master"]]["first"])
        contours = copies.copy_contours(source, qt.QtGui.QTransform())
        if len(contours) != len(row["result"]):
            raise ValueError("Native copy changed the contour count.")
        shape, layer = fl.flShape(), fl.flLayer()
        layer.name, layer.advanceWidth = checked_name(row["target"]), row["advance"]
        for index, (contour, (closed, points, tt)) in enumerate(
            zip(contours, row["result"], strict=True)
        ):
            nodes = list(contour.nodes())
            if (
                len(nodes) != len(points)
                or contour.closed != closed
                or contour.isTT != tt
            ):
                raise ValueError("Native copy changed contour topology.")
            contour.name = row["metadata"][0][index][0]
            for node, (x, y, _) in zip(nodes, points, strict=True):
                node.x, node.y = x, y
            shape.addContour(contour, False, False)
        layer.addShape(shape)
        prepared.append((row, glyph, layer, float(layer.advanceWidth)))
        owners[row["name"]] = glyph
    if not prepared:
        return {"pending_updates": (), "pending_note": "", "changed": 0, "kept": len(rows)}
    made, failures = [], []

    def mutate() -> list[Any]:
        for row, glyph, layer, _ in prepared:
            try:
                try:
                    glyph.addLayer(layer)
                finally:
                    found = glyph.findLayer(row["target"])
                    if found is not None and not found.isNull:
                        made.append(found)
                if found is None or found.isNull:
                    raise RuntimeError("FontLab did not attach the new layer.")
                writer.settle(found)
            except Exception as error:  # noqa: BLE001 - enroll every attached layer before reporting
                failures.append(error)
                break
        return made

    def read_back() -> list[str]:
        if failures:
            raise RuntimeError(str(failures[0])) from failures[0]
        missed = []
        for row, glyph, _, stored_advance in prepared:
            found = glyph.findLayer(row["target"])
            if found is None or found.isNull:
                missed.append(row["name"] + "/" + row["target"])
                continue
            data, metadata = read_contours(found, monotonic() + 3)
            if (
                not stored_outline_matches(data, row["result"])
                or metadata != row["metadata"][0]
                or not abs(float(found.advanceWidth) - stored_advance)
                <= COORDINATE_TOLERANCE
            ):
                missed.append(row["name"] + "/" + row["target"])
        return missed

    done = history.commit(
        TITLE,
        [],
        list(owners.values()),
        mutate,
        operation="geometry",
        facts=facts,
        window=int(package.id),
        read_back=read_back,
    )
    if done.mismatches:
        raise RuntimeError(
            "Native changes may remain; use Edit > Undo. " + "; ".join(done.mismatches)
        )
    return {"pending_note": done.pending_note, "pending_updates": done.pending_updates, "changed": len(prepared), "kept": sum(bool(r["note"]) for r in rows)}


def panel_type() -> type:
    """Build a per-master table, explicit Preview and separate confirmation."""
    import fly.ap.edit_guards as guards
    import fly.ap.master_angles as master_angles  # noqa: PLR0402
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    gui = qt.QtGui

    class ScalePanel(gui.QDialog):
        def __init__(self, parent: Any = None) -> None:
            gui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.setWindowTitle(TITLE)
            self.resize(1100, 680)
            self.stack_box = gui.QVBoxLayout(self)
            self.suffix_field = gui.QLineEdit(".scaled")
            self.stack_box.addWidget(gui.QLabel("New layer suffix"))
            self.stack_box.addWidget(self.suffix_field)
            self.master_table = gui.QTableWidget(0, len(HEADERS))
            self.master_table.setHorizontalHeaderLabels(list(HEADERS))
            self.stack_box.addWidget(self.master_table)
            self.preview_field = gui.QPlainTextEdit()
            self.preview_field.setReadOnly(True)
            self.stack_box.addWidget(self.preview_field)
            self.confirm_box = gui.QCheckBox("I confirm the previewed new layers")
            self.stack_box.addWidget(self.confirm_box)
            self.status = gui.QLabel(
                "Select glyphs, check master rows, edit measured stems and Preview."
            )
            self.stack_box.addWidget(self.status)
            self.plan_data: Any = None
            self.identity: int | None = None
            self.names: list[str] = []
            for label, action in (
                ("Use Selection / Reload Masters", self.reload_selection),
                ("Preview", self.preview_scale),
                ("Create Layers", self.create_layers),
            ):
                button = gui.QPushButton(label)
                self.stack_box.addWidget(button)
                scripting.connect_guarded(
                    self, button.clicked, lambda *args, call=action: call()
                )
            for signal in (
                self.suffix_field.textChanged,
                self.master_table.cellChanged,
            ):
                scripting.connect_guarded(self, signal, lambda *args: self.invalidate())
            self.reload_selection()

        def invalidate(self) -> None:
            self.plan_data = None
            self.confirm_box.setChecked(False)
            self.preview_field.setPlainText("")

        def reload_selection(self) -> None:
            package = scripting.current_package()
            if package is None:
                raise ValueError("Open a font first.")
            guards.require_selection_window(int(package.id))
            identity = int(package.fgId)
            names = scripting.names_font_window_selection(
                expected_fg_id=identity, deadline=monotonic() + 3
            )
            masters = [str(m) for m in package.masters]
            angles = dict(master_angles.capture(package).angles)
            if hasattr(self, "master_names"):
                if masters != self.master_names:
                    raise ValueError("The master list changed; reopen this panel.")
            else:
                self.master_names = masters
                self.master_table.setRowCount(len(masters))
                for row, master in enumerate(masters):
                    check = gui.QCheckBox()
                    check.setChecked(master == str(package.master))
                    self.master_table.setCellWidget(row, 0, check)
                    scripting.connect_guarded(
                        self, check.toggled, lambda *args: self.invalidate()
                    )
                    values = [
                        master,
                        masters[0],
                        masters[-1],
                        "50",
                        "100",
                        "50",
                        "100",
                        "75",
                        "75",
                        "1",
                        "1",
                        f"{-angles[master]:g}",
                    ]
                    for col, value in enumerate(values, 1):
                        self.master_table.setItem(row, col, gui.QTableWidgetItem(value))
            self.invalidate()
            self.identity, self.names = identity, names
            self.status.setText(
                f"{len(self.names)} glyphs selected. Replace example stems with measured values."
            )

        def configurations(self) -> list[dict[str, Any]]:
            configs = []
            for row in range(self.master_table.rowCount):
                if not self.master_table.cellWidget(row, 0).isChecked():
                    continue
                values = [
                    str(self.master_table.item(row, col).text())
                    for col in range(1, len(HEADERS))
                ]
                config = {"master": values[0], "first": values[1], "second": values[2]}
                try:
                    numbers = tuple(float(v) for v in values[3:])
                    config.update(
                        stems=numbers[:4],
                        target=numbers[4:6],
                        scales=numbers[6:8],
                        angle=numbers[8],
                    )
                except ValueError:
                    config["error"] = (
                        "enter numbers in every stem, scale and slant cell"
                    )
                configs.append(config)
            return configs

        def preview_scale(self) -> None:
            self.invalidate()
            self.plan_data = make_plan(
                self.identity,
                self.names,
                self.configurations(),
                str(self.suffix_field.text),
            )
            self.preview_field.setPlainText(
                "\n".join(
                    f"{r['name']} / {r['master']} -> {r['target']}: "
                    + (
                        "Kept: " + r["note"]
                        if r["note"]
                        else f"Create; advance {r['advance']:g}"
                    )
                    for r in self.plan_data["rows"]
                )
            )

        def create_layers(self) -> None:
            if self.plan_data is None:
                raise ValueError("Preview first.")
            try:
                result = apply_plan(self.plan_data, bool(self.confirm_box.isChecked()))
                self.status.setText(
                    f"Created {result['changed']} layers; kept {result['kept']}. One Undo step."
                    + (" · " + result["pending_note"] if result.get("pending_note") else "")
                )
            finally:
                self.plan_data = None
                self.confirm_box.setChecked(False)

        def closeEvent(self, event: Any) -> None:
            scripting.close_script_dialog(self, event, KEY)

    return ScalePanel


def main() -> None:
    """Contain startup errors; the App guards all owned callbacks."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
