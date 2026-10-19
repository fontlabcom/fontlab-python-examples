# this_file: lessons/src/fontlab_python_lessons/getgo/_shared.py
# SPDX-License-Identifier: Apache-2.0
"""Owned GetGo documents; imports of FontLab stay at the native boundary."""

from typing import Any

import hashlib
import json
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "data"


def fixture(font_id: str) -> tuple[dict, Path]:
    """Resolve a manifest ID and check its immutable source bytes before opening."""
    rows = json.loads((FIXTURES / "manifest.json").read_text())["fonts"]
    record = next((row for row in rows if row["id"] == font_id), None)
    if record is None:
        raise KeyError(font_id)
    source = FIXTURES / record["path"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != record["sha256"]:
        msg = f"GetGo fixture hash differs: {font_id}"
        raise ValueError(msg)
    return record, source


@contextmanager
def owned_font(font_id: str, *, mutates: bool = False) -> Any:
    """Open an absolute temporary VFJ copy, close that exact package in finally.

    No active-font lookup. Even a partially successful open is cleaned up by its
    unique path. A failed close retains the temporary directory for inspection.
    The bridge discards edits without package.close(False)'s modal save prompt.
    """
    import fontlab
    import fontpr

    workspace = fontlab.flWorkspace.instance()
    if mutates:
        others = [fontlab.flPackage(obj) for obj in workspace.packages()]
        if others:
            names = ", ".join(str(p.path or p.name) for p in others)
            msg = (
                f"GetGo mutation requires a dedicated no-document FontLab session; "
                f"close these documents first: {names}. See the installed GetGo README.md."
            )
            raise RuntimeError(
                msg,
            )
    record, source = fixture(font_id)
    directory = Path(tempfile.mkdtemp(prefix="getgo-example-")).resolve()
    copy = directory / source.name

    def matching() -> list:
        # packages() returns flObject wrappers; promote registered objects first.
        packages = [fontlab.flPackage(obj) for obj in workspace.packages()]
        return [p for p in packages if p.path and Path(p.path).resolve() == copy]

    try:
        shutil.copyfile(source, copy)
        reply = fontpr.call("open_font", path=str(copy))
        if reply.get("status") != "ok":
            msg = f"Cannot open owned GetGo copy: {reply}"
            raise RuntimeError(msg)
        packages = matching()
        if len(packages) != 1:
            msg = f"Expected one owned document, found {len(packages)}"
            raise RuntimeError(msg)
        yield packages[0], record
    finally:
        for package in matching():
            # fontpr takes the FontGate ID, not the flObject wrapper's package.id.
            fontpr.call("close_font", font_id=package.fgId, save=False)
        if matching():
            msg = f"Owned document did not close; retained {directory}"
            raise RuntimeError(msg)
        shutil.rmtree(directory)


def unicodes(package: Any) -> list[int]:
    """Read encoding only; avoid glyph/layer/anchor lookups for text coverage."""
    return [int(scalar) for glyph in package.fgPackage for scalar in glyph.unicodes]


def glyph_rows(package: Any) -> list[dict]:
    """Read fgGlyph encoding and flLayer anchors from a registered package."""
    rows = []
    for glyph in package.fgPackage:
        layer = package.findName(glyph.name).findLayer(package.defaultMaster)
        rows.append(
            {
                "name": glyph.name,
                "unicodes": list(glyph.unicodes),
                "anchors": [a.name for a in layer.anchors]
                if layer is not None and not layer.isNull
                else [],
            },
        )
    return rows


def required_layer(package: Any, name: str, master: str | None = None) -> Any:
    """Resolve an explicit glyph and layer; missing data is an error."""
    glyph = package.findName(name)
    if glyph is None:
        raise KeyError(name)
    layer = glyph.findLayer(package.defaultMaster if master is None else master)
    if layer is None or layer.isNull:
        msg = f"Missing layer: {name}/{master}"
        raise KeyError(msg)
    return glyph, layer


def notify(label: str, glyph_layers: list) -> None:
    """Include both layers and glyphs in FontLab's change notification."""
    import fontlab

    objects = [layer for glyph, layer in glyph_layers] + [glyph for glyph, layer in glyph_layers]
    if objects:
        fontlab.flItems().notifyChangesApplied(label, objects)
