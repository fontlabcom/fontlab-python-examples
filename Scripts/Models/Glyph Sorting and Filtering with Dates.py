# this_file: Scripts/Models/Glyph Sorting and Filtering with Dates.py
# SPDX-License-Identifier: Apache-2.0
# historical source sha256: 03d3339a55b0edc631e8cce1b3ddf09924fbe4b25ec7e6ca42be092f3788f199
"""Sort and filter a complete real-font glyph metadata snapshot.

Purpose: Adapt the complete part2 custom source/proxy model lesson to
current-font glyph names, all Unicode assignments and local modification dates.
Setup: FontLab9 Python3.11, fontlab-fly and App>=0.2.54.dev0.
Run: Open a font, then run this Models command. Both read-only views share one
captured model. Enter a regular expression, wildcard or fixed string. Toggle
filter and sorting case independently; click a result header to sort.
Custom matches either name or Unicode. Enable Limit dates for inclusive From/To days. The disabled column selector documents the original ignored control.
Result: Inspect matching real glyph metadata without editing a font, changing
selection or touching preferences/Output. Refresh replaces the complete capture;
missing, unreadable, changed or expired reads clear both views and diagnose.
Close releases models, controls, captured data and callbacks.
Compatibility: Native PythonQt callbacks, real metadata/getter/cache/history and
complete persistence/UI acceptance remain pending. Standalone Qt tests do not
qualify the FontLab host. This replaces one preserved-source dispatcher; the
original remains external and is never executed by this adaptation.

Historical source: rescued/part2/ports/itemviews/pyqt-official/customsortfiltermodel-029ea0dabe87ae57.py
The generic UI and query policy live in App. The part3 official versions have
different contracts and remain separate pending entries. Custom date filtering
starts unrestricted rather than limiting real fonts to demonstration-only2026.
"""


def main() -> None:
    """Open the complete owned real-font workflow through the lazy Fly namespace."""
    from fly.ap.glyph_catalog import show_custom

    show_custom()


if __name__ == "__main__":
    main()
