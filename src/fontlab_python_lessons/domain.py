# this_file: src/fontlab_python_lessons/domain.py
# SPDX-License-Identifier: Apache-2.0
"""Keep lesson data immutable; delegate all native reads to existing App APIs.

Snapshots hold plain values, never native wrappers. Read selected names in Font
window order without the false-y CurrentGlyph fallback. Capture the native master
before any data read. Recheck it before returning or acting on a snapshot.
"""
import math
from dataclasses import dataclass
from typing import Any, Literal

Mode = Literal["names", "metrics", "form"]


@dataclass(frozen=True)
class Metric:
    """One measured layer; None is missing data, while zero remains a number."""
    name: str
    advance: float | None
    lsb: float | None


@dataclass(frozen=True)
class Snapshot:
    """Bind ordered plain values to one package, master and lesson scope."""
    mode: Mode
    package_id: int
    master: str
    names: tuple[str, ...]
    selected: tuple[str, ...]
    rows: tuple[Metric, ...]


def capture(api: Any, mode: Mode, name: str | None = None) -> Snapshot:
    """Read a complete source snapshot through fly.ap.scripting, without edits.

    Names mode needs no metrics. Metrics mode reads the exact Font window
    selection. Form mode reads one existing glyph, defaulting to the first
    selected name or first font name. Missing layers remain explicit rows.
    """
    if mode not in ("names", "metrics", "form"):
        raise ValueError("Unknown lesson mode.")
    package = api.current_package()
    if package is None:
        raise ValueError("Open a font, then click Refresh.")
    package_id, master = package.id, package.master
    names = tuple(n for n, _unicodes in api.names_font_glyphs())
    selected_set = set(api.names_font_window_selection())
    selected = tuple(n for n in names if n in selected_set)
    targets = selected if mode == "metrics" else ()
    if mode == "form" and names:
        name = name if name is not None else (selected or names)[0]
        if name not in names:
            raise ValueError("The chosen glyph is missing. Click Refresh.")
        targets = (name,)
    values = api.inspectors_api().layout(package, targets, master) if targets else []
    metrics = {n: Metric(n, advance, lsb) for n, _x, advance, lsb, _rsb in values}
    rows = tuple(metrics.get(n, Metric(n, None, None)) for n in targets)
    active = api.current_package(package_id)
    if active is None or active.master != master:
        raise ValueError("Font or master changed during the read. Click Refresh.")
    return Snapshot(mode, package_id, master, names, selected, rows)


def ensure_current(api: Any, scanned: Snapshot) -> None:
    """Reject stale font, master, membership and displayed metric values.

    Metrics also bind the selected names. Names/form lessons allow selection
    changes, since only their explicit Select action changes Font selection.
    """
    name = scanned.rows[0].name if scanned.mode == "form" and scanned.rows else None
    actual = capture(api, scanned.mode, name)
    common = ("package_id", "master", "names", "rows")
    changed = any(getattr(actual, field) != getattr(scanned, field) for field in common)
    if changed or (scanned.mode == "metrics" and actual.selected != scanned.selected):
        raise ValueError("The font data changed. Click Refresh before continuing.")


def filtered(names: tuple[str, ...], prefix: str) -> tuple[str, ...]:
    """Filter names case-insensitively, preserving their original font order."""
    return tuple(n for n in names if n.casefold().startswith(prefix.casefold()))


def preview(row: Metric, hypothetical: float) -> str:
    """Compare a hypothetical width in plain data; never call a native setter."""
    if row.advance is None:
        raise ValueError("This glyph has no current-master layer.")
    if not math.isfinite(hypothetical):
        raise ValueError("Enter a finite preview width.")
    delta = hypothetical - row.advance
    return (f"{row.name}: actual {row.advance:g}; preview {hypothetical:g}; "
            f"change {delta:+g} font units. No font edit.")
