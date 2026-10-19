# this_file: lessons/src/fontlab_python_lessons/getgo/unicode_coverage.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Arabic Text Coverage

"""Zoto Kufi Arabic (Apache-2.0): check a short text's Unicode coverage.
Source font: https://code.fontlab.com/getgo-fonts/zoto-kufiarabic/
Original example code: Apache-2.0. Coverage does not test Arabic shaping.
"""

from fontlab_python_lessons.getgo._shared import owned_font, unicodes


def coverage(text: str, unicodes: list[int]) -> dict:
    """Report unique covered/missing code points, including supplementary planes."""
    wanted, available = {ord(c) for c in text}, set(unicodes)
    return {
        "covered": [f"U+{n:04X}" for n in sorted(wanted & available)],
        "missing": [f"U+{n:04X}" for n in sorted(wanted - available)],
    }


def run(text: str = "مرحبا بالعالم 123") -> dict:
    """Read native encodings from an owned Arabic font, then close it."""
    with owned_font("zoto-kufiarabic") as (package, record):
        return {
            "source": record["page_url"],
            "text": text,
            **coverage(text, unicodes(package)),
        }
