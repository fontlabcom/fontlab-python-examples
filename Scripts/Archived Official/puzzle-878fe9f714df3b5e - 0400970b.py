# this_file: Scripts/Archived Official/puzzle-878fe9f714df3b5e - 0400970b.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 0d2e4b9b8d16f99f226fd0392076bfead651520d9778c2291daa160b9f6378c5
"""Launch the preserved archive entry: puzzle-878fe9f714df3b5e - 0400970b.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > puzzle-878fe9f714df3b5e - 0400970b.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py'
    )


if __name__ == "__main__":
    main()
