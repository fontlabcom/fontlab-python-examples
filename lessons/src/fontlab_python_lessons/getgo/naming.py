# this_file: lessons/src/fontlab_python_lessons/getgo/naming.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Name a Disposable Derivative

"""GG Baar (CC0-1.0): rename only an owned in-memory working copy.
Source font: https://code.fontlab.com/getgo-fonts/baar/
Original example code: Apache-2.0. Source copyright and licence remain intact.
Requires a dedicated FontLab session with no other documents; enforced by owned_font.
"""

import re

from fontlab_python_lessons.getgo._shared import owned_font


def family_names(family: str, style: str) -> dict[str, str]:
    """Deliberately constrain example names to ASCII letters, digits and spaces."""
    if not all(isinstance(s, str) for s in (family, style)):
        msg = "Family and style must be text"
        raise TypeError(msg)
    if not all(s.strip() and re.fullmatch(r"[A-Za-z0-9 ]+", s) for s in (family, style)):
        msg = "Use nonblank ASCII letters, digits and spaces"
        raise ValueError(msg)
    family, style = family.strip(), style.strip()
    ps_name = family.replace(" ", "") + "-" + style.replace(" ", "")
    if len(ps_name) > 63:
        msg = "PostScript name must fit 63 characters"
        raise ValueError(msg)
    return {
        "familyName": family,
        "styleName": style,
        "postscriptFontName": ps_name,
        "openTypeNamePreferredFamilyName": family,
        "openTypeNamePreferredSubfamilyName": style,
    }


def run() -> dict:
    """Read back assigned metadata, then discard the owned derivative."""
    changes = family_names("Scripting Sample", "Regular")
    with owned_font("baar", mutates=True) as (package, record):
        info = package.info
        notices = (info.copyright, info.openTypeNameLicense)
        before = {key: getattr(info, key) for key in changes}
        for key, value in changes.items():
            setattr(info, key, value)
        after_info = package.info
        after = {key: getattr(after_info, key) for key in changes}
        if after != changes or notices != (
            after_info.copyright,
            after_info.openTypeNameLicense,
        ):
            msg = "Metadata readback or retained notices differ"
            raise AssertionError(msg)
        return {"source": record["page_url"], "before": before, "after": after}
