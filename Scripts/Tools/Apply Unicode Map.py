# this_file: Scripts/Tools/Apply Unicode Map.py
# SPDX-License-Identifier: Apache-2.0
"""What: Add explicit Unicode values to selected glyphs in the current font.
How: Paste a JSON object of glyph names and code points. Integers are decimal;
strings are hexadecimal, with optional U+ or 0x prefix. A value can be a list. Existing codes stay in place.
Why: Font > Generate Unicodes derives values from names. This map also encodes
custom names and assigns several explicit values to one glyph.
Usage: Select glyphs in the Font window and close Glyph editors. Paste a map,
inspect the live table, then Apply Map. Use Selection reloads the glyph scope.
Each Apply is recorded as one Undo step. Auto-layer owners, bases of automatic
composites, unknown names and conflicting codes remain as named kept rows.
Benefit: Apply a reusable character map without renaming outlines.

Example: {"A": "0041", "space": [32, "00A0"]}. Repeated JSON keys and invalid
Unicode scalars are refused. Several map rows cannot claim the same code.
Only selected glyphs can change. Typing uses a detached font snapshot. Use Selection
reloads it. Apply scans the font once and compares with the displayed preview;
native read-back checks every changed list. A partial write directs you to
Edit > Undo. JSON is pasted; NAM files and font-library maps are not loaded.
Setup: FontLab 9, Python 3.11, Fly and App>=0.2.150.dev0. Modeless panel.

Independent behaviour rewrite of TR-EncodeGlyphs.py by Vassil Kateliev,
kateliev/TypeRig, MPL-2.0. https://github.com/kateliev/TypeRig
No TypeRig code, private identifiers, comments or resources are copied.
"""

import json
import re
from types import SimpleNamespace
from typing import Any

TITLE = "Apply Unicode Map"


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject repeated JSON keys instead of silently taking the last value."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Repeated glyph name: {key}")
        result[key] = value
    return result


def parse_map(text: str) -> dict[str, tuple[int, ...]]:
    """Parse a nonempty map into scalar tuples before any native access."""
    if any(char in text for char in "\0\u00a0\u2028\u2029"):
        raise ValueError("Remove NUL, NBSP and Unicode line separators.")
    raw = json.loads(text, object_pairs_hook=unique_object)
    if not isinstance(raw, dict) or not raw:
        raise ValueError("Paste a nonempty JSON object of glyph names and codes.")
    result = {}
    for name, values in raw.items():
        if not name or any(char.isspace() or ord(char) < 32 for char in name):
            raise ValueError("Glyph names must be nonempty tokens.")
        try:
            name.encode("utf-8")
        except UnicodeError as error:
            raise ValueError("Glyph name contains an invalid surrogate.") from error
        items = values if isinstance(values, list) else [values]
        codes = []
        if not items:
            raise ValueError(f"{name}: supply at least one code.")
        for value in items:
            if type(value) not in (int, str):
                raise ValueError(f"{name}: use integers or hexadecimal strings.")
            if isinstance(value, str):
                digits = re.sub(r"^(?:U\+|0[xX])", "", value)
                if re.fullmatch(r"[0-9A-Fa-f]{1,6}", digits) is None:
                    raise ValueError(
                        f"{name}: use 1–6 hexadecimal digits, optionally U+ or 0x."
                    )
                code = int(digits, 16)
            else:
                code = value
            if not 0 <= code <= 0x10FFFF or 0xD800 <= code <= 0xDFFF:
                raise ValueError(f"{name}: not a Unicode scalar.")
            if code not in codes:
                codes.append(code)
        result[name] = tuple(codes)
    return result


def code_owners(facts: Any) -> dict[int, set[str]]:
    """Index existing codes once per captured facts object."""
    owners: dict[int, set[str]] = {}
    for name, entry in facts.entries.items():
        for code in entry.record.unicodes:
            owners.setdefault(int(code), set()).add(name)
    return owners


def snapshot_facts(facts: Any) -> Any:
    """Detach Unicode lists and layer membership for cheap, stable typing previews."""
    entries = {
        name: SimpleNamespace(
            record=SimpleNamespace(unicodes=tuple(entry.record.unicodes)),
            glyph=SimpleNamespace(layers=tuple(entry.glyph.layers)),
        )
        for name, entry in facts.entries.items()
    }
    cached = SimpleNamespace(
        entries=entries, autos=facts.autos, package_id=facts.package_id
    )
    cached.code_owners = code_owners(cached)
    return cached


def plan_map(
    facts: Any, selected: list[str], mapping: dict[str, tuple[int, ...]]
) -> list[dict[str, Any]]:
    """Keep each refused item visible; preserve codes and reject shared claims."""
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - preserve module import

    owners = getattr(facts, "code_owners", None)
    if owners is None:
        owners = code_owners(facts)
    claims: dict[int, set[str]] = {}
    for name, codes in mapping.items():
        if name in selected and name in facts.entries:
            for code in codes:
                claims.setdefault(code, set()).add(name)
    rows = []
    for name, codes in mapping.items():
        entry = facts.entries.get(name)
        before = tuple(int(code) for code in entry.record.unicodes) if entry else ()
        note = names_edit.refusal(facts, name, "unicode")
        if not note and name not in selected:
            note = "not selected"
        if not note and any(
            (owners.get(code, set()) | claims.get(code, set())) - {name}
            for code in codes
        ):
            note = "Unicode claimed by another glyph or map row"
        after = tuple(dict.fromkeys((*before, *codes))) if not note else before
        if not note and after == before:
            note = "already present"
        rows.append({"name": name, "before": before, "after": after, "note": note})
    return rows


class StalePreviewError(ValueError):
    """Carry fresh detached facts so the panel can replace its stale preview."""

    def __init__(self, facts: Any) -> None:
        super().__init__("The font changed; inspect the refreshed preview.")
        self.facts = snapshot_facts(facts)


def write_map(
    package_id: int,
    selected: list[str],
    mapping: dict[str, tuple[int, ...]],
    preview: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replan with fresh facts; write safe rows through the shared Unicode writer."""
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - preserve module import

    facts = names_edit.fresh_facts(package_id)
    rows = plan_map(facts, selected, mapping)
    if rows != preview:
        raise StalePreviewError(facts)
    ready = [row for row in rows if not row["note"]]
    if not ready:
        return {"changed": 0, "facts": snapshot_facts(facts)}

    def mutate() -> None:
        for row in ready:
            facts.entries[row["name"]].record.unicodes = list(row["after"])

    def read_back() -> list[str]:
        return [
            row["name"]
            for row in ready
            if tuple(facts.entries[row["name"]].record.unicodes) != row["after"]
        ]

    result = names_edit.commit(
        TITLE,
        [facts.entries[r["name"]] for r in ready],
        mutate,
        operation="unicode",
        facts=facts,
        read_back=read_back,
        window=facts.package_id,
    )
    if result.mismatches:
        raise RuntimeError(
            "Unicode values differ. Native changes may remain; use Edit > Undo."
        )
    return {"changed": len(ready), "facts": snapshot_facts(facts)}


def panel_type() -> type:
    """Build only inside FontLab; the shared base owns signals and refusals."""
    import fly.ap.names_edit as names_edit  # noqa: PLR0402 - preserve module import
    import fly.ap.selection_panel as selection_panel  # noqa: PLR0402 - preserve module import
    from fly import qt

    class MapPanel(selection_panel.panel_type()):
        """Keep the map editable while the live table shows every kept item."""

        TITLE, KEY, ACTION = "Apply Unicode Map", "apply_unicode_map", "Apply Map"
        HEADERS = ("Glyph", "Before", "After", "Result")
        SCOPE, CONSENT, ALIGN = False, "", False

        def build_controls(self) -> None:
            self.facts_cache: Any = None
            self.map_input = qt.QtGui.QPlainTextEdit()
            self.map_input.setPlainText('{"A": "0041"}')
            self.add_row("JSON map", self.map_input)
            self.watch(self.map_input.textChanged)

        def plan_rows(self, package: Any, masters: list[str]) -> list[dict[str, Any]]:
            mapping = parse_map(str(self.map_input.toPlainText()))
            if self.facts_cache is None:
                self.facts_cache = snapshot_facts(names_edit.scan())
            if self.facts_cache.package_id != int(package.id):
                raise ValueError("The font changed; use selection again.")
            return plan_map(self.facts_cache, self.names, mapping)

        def on_reselect(self) -> None:
            """Explicit selection reload captures the font once, outside typing."""
            self.facts_cache = snapshot_facts(names_edit.scan())

        def on_result(self, result: dict[str, Any]) -> None:
            """Reuse the write's fresh facts after successful read-back."""
            self.facts_cache = result["facts"]

        def cells(self, row: dict[str, Any]) -> list[str]:
            return [
                row["name"],
                " ".join(f"U+{c:04X}" for c in row["before"]),
                " ".join(f"U+{c:04X}" for c in row["after"]),
                "Kept: " + row["note"] if row["note"] else "Add codes",
            ]

        def is_ready(self, row: dict[str, Any]) -> bool:
            return not row["note"]

        def write(self, package: Any, rows: list[dict[str, Any]]) -> dict[str, Any]:
            try:
                return write_map(
                    int(package.id),
                    self.names,
                    parse_map(str(self.map_input.toPlainText())),
                    self.rows,
                )
            except StalePreviewError as error:
                self.facts_cache = error.facts
                self.rows = []
                raise

        def result_text(self, result: dict[str, Any]) -> str:
            return f"Changed {result['changed']} glyphs. Each Apply is recorded as one Undo step."

    return MapPanel


def main() -> None:
    """Contain startup errors; the shared panel contains slot errors."""
    import fly.ap.scripting as scripting  # noqa: PLR0402 - preserve module import

    try:
        scripting.show_script_dialog(panel_type(), "apply_unicode_map")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print(f"{TITLE}: {error}")


if __name__ == "__main__":
    main()
