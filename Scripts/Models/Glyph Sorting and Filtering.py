# this_file: Scripts/Models/Glyph Sorting and Filtering.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: 4c46c9af9db4321d45690cc5cb82e3c0d60454d0ed3123d0f9a8c5f002980d39
"""Sort and filter a complete real-font glyph metadata snapshot.

Purpose: Adapt the complete part2 basic source/proxy model lesson to
current-font glyph names, all Unicode assignments and local modification dates.
Setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.54.dev0.
Run: Open a font, then run this Models command. Both read-only views share one
captured model. Enter a regular expression, wildcard or fixed string. Toggle
filter and sorting case independently; click a result header to sort.
Choose a filter column: name, Unicode or modification date. Basic retains native Qt QRegExp matching; Custom has different Python matching semantics.
Result: Inspect matching real glyph metadata without editing a font, changing
selection or touching preferences/Output. Refresh replaces the complete capture;
missing, unreadable, changed or expired reads clear both views and diagnose.
Close releases models, controls, captured data and callbacks.
Compatibility: Native PythonQt callbacks, real metadata/getter/cache/history and
complete persistence/UI acceptance remain pending. Standalone Qt tests do not
qualify the FontLab host. This replaces one preserved-source dispatcher; the
original remains external and is never executed by this adaptation.

Historical source: rescued/part2/ports/itemviews/pyqt-official/basicsortfiltermodel-9dab02b61cebbdb7.py
The generic UI and query policy live in App. The part3 official versions have
different contracts and remain separate pending entries. Custom date filtering
starts unrestricted rather than limiting real fonts to demonstration-only2026.
"""


def main() -> None:
    """Open the complete owned real-font workflow through the lazy Fly namespace."""
    from fly.ap.glyph_catalog import show_basic

    show_basic()


if __name__ == "__main__":
    main()
