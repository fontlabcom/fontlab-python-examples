# this_file: Scripts/Archived Official/pixelator-d50ad6638357e669 - e0e72487.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: dcffd1f6ddaf3cbbe1b72fa90816d42892ce5abccf5ff0098e7e5cc50c9270bb
"""Launch the preserved archive entry: pixelator-d50ad6638357e669 - e0e72487.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > pixelator-d50ad6638357e669 - e0e72487.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/pixelator-d50ad6638357e669.py'
    )


if __name__ == "__main__":
    main()
