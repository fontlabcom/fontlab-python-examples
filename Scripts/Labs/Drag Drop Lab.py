# this_file: Scripts/Labs/Drag Drop Lab.py
# SPDX-License-Identifier: Apache-2.0
"""Drag Drop Lab: explore related PythonQt controls beside a live font preview.

Setup: FontLab 9, Fly and the matching App WP09 core PythonQt labs candidate.
Usage: Choose a named profile, inspect its controls and preview, then use the
labelled actions. Refresh captures the current context; Close releases owners.
Credits: FontLab Python examples and App contributors; Apache-2.0.
"""


def main():
    """Open the lab and retain its owned shell handle."""
    from fly.ap.studios.core_pythonqt_labs import show

    return show("E06")


if __name__ == "__main__":
    main()
