# this_file: Scripts/Archived Official/canvas-36246fcbffecdeba - 0173dc35.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: fb7dca9b8bf9d7807cf77bd16fada62a2a66128ea1a986c0ccc3f5257e91ee24
"""Launch the preserved archive entry: canvas-36246fcbffecdeba - 0173dc35.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/canvas-36246fcbffecdeba.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > canvas-36246fcbffecdeba - 0173dc35.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/canvas-36246fcbffecdeba.py'
    )


if __name__ == "__main__":
    main()
