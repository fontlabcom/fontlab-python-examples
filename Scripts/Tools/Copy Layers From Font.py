# this_file: Scripts/Tools/Copy Layers From Font.py
# SPDX-License-Identifier: Apache-2.0
"""What: Copy layers from another open font to selected current-font glyphs.
How: Map source and destination layer names. Preview and confirm Overwrite,
Incoming + suffix, Destination + suffix or Mask. One Copy is recorded as one
Undo step in the destination. Both fonts are identified by fgId.
Why: Native Paste Special uses the clipboard; this repeats explicit layer maps
without switching fonts. The source is read only and glyphs must already exist.
Usage: Select destination glyphs in its Font window, choose a source, enter
mappings, Preview, inspect kept rows, confirm, then Copy.
Benefit: Transfer outlines, anchor positions and advances across many glyphs.

Components, hints, guides, metric expressions, locked/automatic layers and
unsafe automatic dependants are kept. Element names, notes and transforms,
contour names, node names and raw flags are retained; selection flags clear.
Custom node/contour properties are refused. Anchor coordinates use App;
existing
pin styles stay, new pins use name-derived styles. Anchor expressions, layer
metadata, links and colour marks are not copied. Units per em must match.
Mask replaces the mapped layer's mask. Destination + suffix refuses master
renames; existing suffix names are kept. New names cannot contain @ or # or
begin with |temp|, mask, img. or bw.. Capture allows 3 seconds plus
one second per selected glyph/mapping; a timeout refuses the whole preview.
Apply rechecks the displayed plan. Partial failures direct
you to Edit > Undo. Setup: FontLab 9, Python 3.11, Fly, App>=0.2.150.dev0.
Independent behaviour rewrite of TR-CopyLayers.py, Vassil Kateliev / Karandash
Type Foundry, kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
No upstream code, comments or assets copied. Implementation: Apache-2.0.
"""

import math
from time import monotonic
from typing import Any

TITLE, KEY = "Copy Layers From Font", "copy_layers_from_font"
MODES = ("Overwrite", "Incoming + suffix", "Destination + suffix", "Mask")


def checked_name(name: str) -> str:
    """Reject recipe, temporary and lossy text syntax before any write."""
    if (
        not name.strip()
        or "@" in name
        or "#" in name
        or name.startswith("|temp|")
        or name.casefold().startswith(("mask", "img.", "bw."))
        or any(ord(c) < 32 or c in "\u00a0\u2028\u2029" for c in name)
    ):
        raise ValueError(
            "Use a nonempty layer name without @, #, |temp| or reserved mask/img./bw. prefixes."
        )
    return name


def collision(
    name: str, suffix: str, mode: str, exists: bool
) -> tuple[str, str | None]:
    """Return the incoming name and optional destination backup name."""
    if mode not in MODES:
        raise ValueError("Choose a listed collision mode.")
    if mode in MODES[1:3] and not suffix:
        raise ValueError("Enter a nonempty suffix.")
    if mode == "Incoming + suffix":
        return checked_name(name + suffix), None
    return checked_name(name), checked_name(name + suffix) if mode == MODES[
        2
    ] and exists else None


def registered_fonts() -> dict[int, tuple[str, Any]]:
    """Read registered packages without activating or completing any source font."""
    from fly import fl

    packages = {
        int(p.fgId): p
        for p in (fl.flPackage(item) for item in fl.flWorkspace.instance().packages())
    }
    return {
        int(f.id): (str(f.path) or f"Font {f.id}", packages[int(f.id)])
        for f in fl.AllFonts()
        if int(f.id) in packages
    }


def resolve(source_id: int, destination_id: int) -> tuple[Any, Any]:
    """Require two registered fonts, equal units per em and the current destination."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    fonts, current = registered_fonts(), scripting.current_package()
    if (
        source_id == destination_id
        or source_id not in fonts
        or destination_id not in fonts
        or current is None
        or int(current.fgId) != destination_id
    ):
        raise ValueError(
            "Keep both fonts open and the destination current; choose another source."
        )
    source, destination = fonts[source_id][1], fonts[destination_id][1]
    if float(source.info.unitsPerEm) != float(destination.info.unitsPerEm):
        raise ValueError("Source and destination units per em must match.")
    return source, destination


def layer_data(layer: Any, deadline: float) -> dict[str, Any]:
    """Snapshot each nodes() once; never use Python wrapper identity as a key."""
    shapes = []
    for shape in layer.shapes:
        contours = []
        for contour in shape.contours:
            nodes = tuple(
                (
                    float(n.x),
                    float(n.y),
                    bool(n.isOn()),
                    int(n.nodeState) & ~0x20,
                    str(n.name),
                )
                for n in contour.nodes()
            )
            if monotonic() >= deadline:
                raise TimeoutError("Layer capture expired; select fewer glyphs.")
            contours.append(
                (bool(contour.closed), bool(contour.isTT), str(contour.name), nodes)
            )
        tx = shape.transform
        matrix = tuple(
            float(getattr(tx, f"m{i}{j}")()) for i in (1, 2, 3) for j in (1, 2, 3)
        )
        shapes.append(
            (
                str(shape.name),
                str(shape.shapeData.name),
                str(shape.shapeData.note),
                matrix,
                tuple(contours),
            )
        )
    pins = tuple(
        sorted(
            (str(a.name), float(a.point.x()), float(a.point.y())) for a in layer.anchors
        )
    )
    values = [
        float(layer.advanceWidth),
        *(v for p in pins for v in p[1:]),
        *(v for s in shapes for c in s[4] for n in c[3] for v in n[:2]),
    ]
    if not all(math.isfinite(v) for v in values):
        raise ValueError("Layer coordinates and advance must be finite.")
    return {"width": values[0], "shapes": tuple(shapes), "anchors": pins}


def usable(layer: Any, *, source: bool) -> None:
    """Refuse content the copy cannot preserve, rather than silently dropping it."""
    if layer is None or layer.isNull:
        raise ValueError("layer is missing")
    if layer.autoLayer or layer.isLocked or layer.isService:
        raise ValueError("automatic, locked or service layer")
    if layer.hasHints or layer.hasTTH or layer.guidelines:
        raise ValueError("hints or guides are not transferred")
    if any(
        str(getattr(layer, n)) for n in ("metricsLeft", "metricsRight", "metricsWidth")
    ):
        raise ValueError("metric expressions are not transferred")
    if any(s.isComponent for s in layer.shapes):
        raise ValueError("components are not transferred")
    if source:
        for shape in layer.shapes:
            for contour in shape.contours:
                if contour.getProperties() or any(
                    n.getProperties() or n.getProperty("corner_smooth") is not None
                    for n in contour.nodes()
                ):
                    raise ValueError("custom node or contour properties")
    names = [str(a.name) for a in layer.anchors]
    if len(names) != len(set(names)):
        raise ValueError("repeated anchor names")


def survey(
    source: Any,
    destination: Any,
    names: list[str],
    mappings: list[tuple[str, str]],
    mode: str,
    suffix: str,
    facts: Any,
) -> list[dict[str, Any]]:
    """Keep every refused glyph/layer row; plan only the selected destination names."""
    import fly.ap.anchor_writer as anchors
    import fly.ap.history as history  # noqa: PLR0402

    if not names or not mappings:
        raise ValueError("Select destination glyphs and add mappings.")
    if len({right.casefold() for _, right in mappings}) != len(mappings):
        raise ValueError("Map each destination once.")
    deadline, rows = monotonic() + 3 + len(names) * len(mappings), []
    for name in names:
        a, b = (
            (source.findName(name), destination.findName(name))
            if monotonic() < deadline
            else (None, None)
        )
        for left, right in mappings:
            row = {
                "name": name,
                "source": left,
                "target": right,
                "backup": None,
                "mode": mode,
                "note": "",
                "data": None,
                "before": None,
                "mask_name": "mask." + right if mode == "Mask" else None,
            }
            try:
                if monotonic() >= deadline:
                    raise TimeoutError("Layer capture expired; select fewer glyphs.")
                if not left.strip():
                    raise ValueError("enter a source layer name")
                if a is None or a.isNull or b is None or b.isNull:
                    raise ValueError("glyph missing in source or destination")
                reason = history.refusal(facts, name, "geometry")
                if reason:
                    raise ValueError(reason)
                src, body = a.findLayer(left), b.findLayer(right)
                usable(src, source=True)
                exists = body is not None and not body.isNull
                target, backup = collision(right, suffix, mode, exists)
                row.update(target=target, backup=backup)
                if mode == "Mask":
                    if not exists or body.autoLayer or body.isLocked or body.isService:
                        raise ValueError("missing, automatic, locked or service body")
                    resolved = body.getMaskLayer(False)
                    if (
                        resolved is not None
                        and not resolved.isNull
                        and (str(resolved.name) != row["mask_name"])
                    ):
                        raise ValueError("mask belongs to another layer")
                    dst = b.findLayer(row["mask_name"])
                else:
                    dst = b.findLayer(target)
                if dst is not None and not dst.isNull:
                    usable(dst, source=False)
                if backup is not None and (
                    body.isMasterLayer
                    or backup.casefold()
                    in {str(m).casefold() for m in destination.masters}
                    or any(
                        str(x.name).casefold() == backup.casefold() for x in b.layers
                    )
                ):
                    raise ValueError(
                        "cannot rename a master or replace an existing backup"
                    )
                if mode == MODES[1] and dst is not None and not dst.isNull:
                    raise ValueError("suffixed layer already exists")
                if (
                    (dst is None or dst.isNull)
                    and mode != "Mask"
                    and any(
                        str(x.name).casefold() == target.casefold() for x in b.layers
                    )
                ):
                    raise ValueError("a case-insensitive target name already exists")
                if (
                    (dst is None or dst.isNull)
                    and mode != "Mask"
                    and target.casefold()
                    in {str(m).casefold() for m in destination.masters}
                ):
                    raise ValueError("destination master layer is missing")
                row["data"] = layer_data(src, deadline)
                row["before"] = (
                    layer_data(dst, deadline)
                    if dst is not None and not dst.isNull
                    else None
                )
                if dst is not None and not dst.isNull and backup is None:
                    old = anchors.anchor_points(dst)
                    if any(
                        (x, y) == (0, 0) and old.get(n, (x, y)) != (x, y)
                        for n, x, y in row["data"]["anchors"]
                    ):
                        raise ValueError(
                            "existing anchor would move to origin (fl#8527)"
                        )
            except (ValueError, RuntimeError) as error:
                row["note"] = str(error)
            rows.append(row)
    return rows


def make_plan(
    source_id: int,
    destination_id: int,
    names: list[str],
    mappings: list[tuple[str, str]],
    mode: str,
    suffix: str,
) -> dict[str, Any]:
    """Run one destination dependency scan per explicit Preview."""
    import fly.ap.history as history  # noqa: PLR0402

    source, destination = resolve(source_id, destination_id)
    facts = history.scan_auto_facts(destination)
    return {
        "source_id": source_id,
        "destination_id": destination_id,
        "names": list(names),
        "mappings": mappings,
        "mode": mode,
        "suffix": suffix,
        "rows": survey(source, destination, names, mappings, mode, suffix, facts),
    }


def clone_shapes(layer: Any) -> list[Any]:
    """Restore clone losses through contour_copy before history starts."""
    import fly.ap.contour_copy as copies

    output = []
    for old in layer.shapes:
        new = old.clone()
        new.name, new.shapeData.name, new.shapeData.note = (
            old.name,
            old.shapeData.name,
            old.shapeData.note,
        )
        new.transform, new.selected, new.active = old.transform, False, False
        for before, after in zip(old.contours, new.contours, strict=True):
            after.name = before.name
            copies.repair_nodes(before, after)
            if before.isTT != after.isTT or before.closed != after.closed:
                raise ValueError("Native clone changed contour topology.")
        output.append(new)
    return output


def apply_plan(plan: dict[str, Any], confirmed: bool) -> dict[str, Any]:
    """Recheck the visible plan and write one destination Undo step."""
    import fly.ap.anchor_writer as anchors
    import fly.ap.history as history  # noqa: PLR0402
    import fly.ap.layer_writer as writer
    from fly import fl

    if not confirmed:
        raise ValueError("Preview and confirm the destination changes.")
    source, destination = resolve(plan["source_id"], plan["destination_id"])
    facts = history.scan_auto_facts(destination)
    rows = survey(
        source,
        destination,
        plan["names"],
        plan["mappings"],
        plan["mode"],
        plan["suffix"],
        facts,
    )
    if rows != plan["rows"]:
        raise ValueError("Source or destination changed; Preview again.")
    prepared, existing, owners, retain = [], [], {}, []
    for row in rows:
        if row["note"]:
            continue
        glyph = destination.findName(row["name"])
        body = glyph.findLayer(row["target"])
        target = glyph.findLayer(row["mask_name"]) if row["mode"] == "Mask" else body
        if target is not None and target.isNull:
            target = None
        if row["backup"]:
            existing.append(body)
            target = None
        if target is not None:
            existing.append(target)
            retain.extend(
                obj for s in target.shapes for obj in history.component_history(s)
            )
        if row["mode"] == "Mask" and target is None:
            existing.append(body)
        stage = target if target is not None else fl.flLayer()
        if target is None:
            stage.name = checked_name(row["target"])
        wanted = {n: (x, y) for n, x, y in row["data"]["anchors"]}
        edits = [
            ("remove", n, None) for n in anchors.anchor_points(stage) if n not in wanted
        ]
        old_points = anchors.anchor_points(stage)
        edits += [("set", n, p) for n, p in wanted.items() if old_points.get(n) != p]
        anchors.require_safe([(glyph, stage, edits)], facts)
        steps = anchors.prepare(stage, edits)
        retain.extend(pin for action, pin, _ in steps if action == "remove")
        shapes = clone_shapes(source.findName(row["name"]).findLayer(row["source"]))
        prepared.append((row, glyph, body, target, stage, steps, shapes))
        owners[row["name"]] = glyph
    if not prepared:
        return {"pending_updates": (), "pending_note": "", "changed": 0, "kept": len(rows)}
    made, failures = [], []

    def mutate() -> list[Any]:
        for row, glyph, body, target, stage, steps, shapes in prepared:
            try:
                if row["backup"]:
                    body.name = row["backup"]
                if target is None:
                    try:
                        if row["mode"] == "Mask":
                            body.getMaskLayer(True)
                        else:
                            glyph.addLayer(stage)
                    finally:
                        target = (
                            glyph.findLayer(row["mask_name"])
                            if row["mode"] == "Mask"
                            else glyph.findLayer(row["target"])
                        )
                        if target is not None and not target.isNull:
                            made.append(target)
                    if target is None or target.isNull:
                        raise RuntimeError("FontLab did not attach the target layer.")
                for shape in list(target.shapes):
                    target.removeShape(shape)
                for shape in shapes:
                    target.addShape(shape)
                anchors.write(target, steps)
                target.advanceWidth = row["data"]["width"]
                writer.settle(target)
            except Exception as error:  # noqa: BLE001 - finish history for every attached object
                failures.append(error)
                break
        return made

    def read_back() -> list[str]:
        if failures:
            raise RuntimeError(str(failures[0])) from failures[0]
        missed = []
        for row, glyph, body, _, _, _, _ in prepared:
            target = (
                glyph.findLayer(row["mask_name"])
                if row["mode"] == "Mask"
                else glyph.findLayer(row["target"])
            )
            if (
                target is None
                or target.isNull
                or layer_data(target, monotonic() + 3) != row["data"]
            ):
                missed.append(row["name"] + "/" + row["target"])
            if row["backup"]:
                backup = glyph.findLayer(row["backup"])
                if (
                    backup is None
                    or backup.isNull
                    or layer_data(backup, monotonic() + 3) != row["before"]
                ):
                    missed.append("backup differs: " + row["name"])
            original = source.findName(row["name"]).findLayer(row["source"])
            if layer_data(original, monotonic() + 3) != row["data"]:
                missed.append("source changed: " + row["name"])
        return missed

    done = history.commit(
        TITLE,
        existing,
        list(owners.values()),
        mutate,
        operation="geometry",
        facts=facts,
        retain=retain,
        read_back=read_back,
        window=int(destination.id),
    )
    if done.mismatches:
        raise RuntimeError(
            "Native changes may remain; use Edit > Undo. " + "; ".join(done.mismatches)
        )
    return {"pending_note": done.pending_note, "pending_updates": done.pending_updates, "changed": len(prepared), "kept": sum(bool(r["note"]) for r in rows)}


def panel_type() -> type:
    """Build the non-modal mapping editor; only Preview and Copy scan dependencies."""
    import fly.ap.edit_guards as guards
    import fly.ap.scripting as scripting  # noqa: PLR0402
    from fly import qt

    gui = qt.QtGui

    class CopyPanel(gui.QDialog):
        def __init__(self, parent: Any = None) -> None:
            gui.QDialog.__init__(self, parent)
            self._connections: list[Any] = []
            self.setWindowTitle(TITLE)
            self.resize(850, 640)
            self.stack_box = gui.QVBoxLayout(self)
            self.source_picker, self.mode_picker = gui.QComboBox(), gui.QComboBox()
            self.mode_picker.addItems(list(MODES))
            self.suffix_field = gui.QLineEdit(".copy")
            for label, control in (
                ("Source font", self.source_picker),
                ("Collision", self.mode_picker),
                ("Suffix", self.suffix_field),
            ):
                self.stack_box.addWidget(gui.QLabel(label))
                self.stack_box.addWidget(control)
            self.mapping_table = gui.QTableWidget(1, 2)
            self.mapping_table.setHorizontalHeaderLabels(
                ["Source layer", "Destination layer"]
            )
            self.stack_box.addWidget(self.mapping_table)
            self.preview_field = gui.QPlainTextEdit()
            self.preview_field.setReadOnly(True)
            self.stack_box.addWidget(self.preview_field)
            self.confirm_box = gui.QCheckBox(
                "I confirm the previewed destination changes"
            )
            self.stack_box.addWidget(self.confirm_box)
            self.status = gui.QLabel(
                "Use Selection in the destination Font window, then Preview."
            )
            self.stack_box.addWidget(self.status)
            self.plan_data: Any = None
            self.names: list[str] = []
            self.source_ids: list[int] = []
            self.destination_id: int | None = None
            for label, action in (
                ("Use Selection / Refresh Fonts", self.reload_selection),
                ("Add Mapping", self.add_mapping),
                ("Preview", self.preview_copy),
                ("Copy", self.copy_rows),
            ):
                button = gui.QPushButton(label)
                self.stack_box.addWidget(button)
                scripting.connect_guarded(
                    self, button.clicked, lambda *args, call=action: call()
                )
            for signal in (
                self.source_picker.currentIndexChanged,
                self.mode_picker.currentIndexChanged,
                self.suffix_field.textChanged,
                self.mapping_table.cellChanged,
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
                raise ValueError("Open a destination font first.")
            guards.require_selection_window(int(package.id))
            destination_id = int(package.fgId)
            names = scripting.names_font_window_selection(
                expected_fg_id=destination_id, deadline=monotonic() + 3
            )
            source_fonts = [
                (identity, label)
                for identity, (label, _) in registered_fonts().items()
                if identity != destination_id
            ]
            master = str(package.master)
            self.invalidate()
            self.source_picker.clear()
            for identity, label in source_fonts:
                self.source_picker.addItem(f"{label} [{identity}]")
            self.mapping_table.setItem(0, 0, gui.QTableWidgetItem(master))
            self.mapping_table.setItem(0, 1, gui.QTableWidgetItem(master))
            self.destination_id, self.names = destination_id, names
            self.source_ids = [identity for identity, _ in source_fonts]
            self.status.setText(
                f"{len(self.names)} destination glyphs selected. Edit the mapping names."
            )

        def add_mapping(self) -> None:
            self.invalidate()
            self.mapping_table.setRowCount(self.mapping_table.rowCount + 1)

        def preview_copy(self) -> None:
            self.invalidate()
            index = self.source_picker.currentIndex
            if not 0 <= index < len(self.source_ids):
                raise ValueError("Choose another open source font.")
            mappings = []
            for row in range(self.mapping_table.rowCount):
                items = [self.mapping_table.item(row, col) for col in (0, 1)]
                if any(item is None for item in items):
                    raise ValueError("Fill both layer names in every mapping row.")
                mappings.append(tuple(str(item.text()) for item in items))
            self.plan_data = make_plan(
                self.source_ids[index],
                self.destination_id,
                self.names,
                mappings,
                str(self.mode_picker.currentText),
                str(self.suffix_field.text),
            )
            self.preview_field.setPlainText(
                "\n".join(
                    f"{r['name']} / {r['source']} -> {r['mask_name'] or r['target']}: "
                    + ("Kept: " + r["note"] if r["note"] else "Copy")
                    for r in self.plan_data["rows"]
                )
            )

        def copy_rows(self) -> None:
            if self.plan_data is None:
                raise ValueError("Preview first.")
            try:
                result = apply_plan(self.plan_data, bool(self.confirm_box.isChecked()))
                self.status.setText(
                    f"Copied {result['changed']} layers; kept {result['kept']}. One Undo step."
                    + (" · " + result["pending_note"] if result.get("pending_note") else "")
                )
            finally:
                self.plan_data = None
                self.confirm_box.setChecked(False)

        def closeEvent(self, event: Any) -> None:
            scripting.close_script_dialog(self, event, KEY)

    return CopyPanel


def main() -> None:
    """Contain startup errors; the App guards owned signal callbacks."""
    import fly.ap.scripting as scripting  # noqa: PLR0402

    try:
        scripting.show_script_dialog(panel_type(), KEY)
    except (ValueError, RuntimeError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
