# this_file: Scripts/Archived Reference/P3 Sources - kateliev_TypeRig - Scripts - TypeRig Tools - TR-ImportGlyph -- 7c31a75675c3.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 8dc65caa7b0f06ae94df33ccb80e7a4fe83db302b5d790735a506a37b7dc933d
"""Launch the preserved archive entry: P3 Sources - kateliev_TypeRig - Scripts - TypeRig Tools - TR-ImportGlyph -- 7c31a75675c3.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/kateliev_TypeRig/Scripts/TypeRig Tools/TR-ImportGlyph.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - kateliev_TypeRig - Scripts - TypeRig Tools - TR-ImportGlyph -- 7c31a75675c3.
Result: The helper runs the preserved entry. Its source determines any window,
output or font changes. Missing resources or unsupported APIs can raise errors.

Compatibility: Native FontLab compatibility is pending. Preserved sources have
not been certified by this launcher; Python syntax and route checks do not
establish successful UI behavior or font results.
"""

from pathlib import Path


def main() -> None:
    """Dispatch this preserved entry once when explicitly launched."""
    from fly.ap.rescued_examples import launch

    launch(
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/kateliev_TypeRig/Scripts/TypeRig Tools/TR-ImportGlyph.py'
    )


if __name__ == "__main__":
    main()
