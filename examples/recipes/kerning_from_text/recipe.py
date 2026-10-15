#MenuTitle: Kerning Pairs from Text
# this_file: examples/recipes/kerning_from_text/recipe.py
"""Set kerning pairs from a plain-text list, one pair per line.

    # left right value    (comments and blank lines are ignored)
    A V -80
    @O_left T -40         (@ marks a kerning class, as in FontLab)

Each pair goes through FontLab's own kerning tool on the current master. FontLab stores whole units, so values are
rounded first (halves away from zero, as FontLab does) and the stored value is
reported. Lines that can't be read are reported, not guessed at.
"""

import math


def parse_pairs(text: str) -> tuple[list[tuple[str, str, float]], list[str]]:
    """([(left, right, value)], [unreadable lines]) from 'left right value' lines."""
    pairs, problems = [], []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        try:
            left, right, value = parts
            pairs.append((left, right, float(value)))
        except ValueError:
            problems.append(line)
    return pairs, problems


def whole_units(value: float) -> int:
    """Round half away from zero: -75.5 -> -76, 75.5 -> 76."""
    return int(math.copysign(math.floor(abs(value) + 0.5), value))


def run(font_id=None, glyph_names=None, text="", master=None) -> dict:
    """Apply the pairs (only those touching ``glyph_names``, when given)."""
    import fontpr

    if font_id is None:
        font_id = fontpr.call("get_active_font")["id"]
    pairs, problems = parse_pairs(text)
    if glyph_names is not None:
        keep = set(glyph_names)
        pairs = [p for p in pairs if p[0] in keep or p[1] in keep]
    options = {"font_id": font_id}
    if master:
        options["master_name"] = master
    applied = []
    for left, right, value in pairs:
        stored = whole_units(value)
        fontpr.call("set_kerning_pair", left=left, right=right, value=stored, **options)
        applied.append([left, right, stored])
    return {"applied": applied, "unreadable": problems}


# Menu use: paste pairs here, then run the script. Nothing happens while PAIRS is empty.
PAIRS = """
"""

if __name__ == "__main__":
    if PAIRS.strip():
        print(run(text=PAIRS))
    else:
        print("Kerning Pairs from Text: paste 'left right value' lines into PAIRS first.")
