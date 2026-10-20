# this_file: Scripts/Archived UI L-Z/Mainwindows - Official mdi - 1415facde30a25cf.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 4a7cab42d4c0c13dd09e5c098e6758007f81371fbb90b832d25c1f44e055609c
"""Launch the preserved archive entry: Mainwindows - Official mdi - 1415facde30a25cf.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/mainwindows/pyqt-official/mdi-1415facde30a25cf.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Mainwindows - Official mdi - 1415facde30a25cf.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/mainwindows/pyqt-official/mdi-1415facde30a25cf.py'
    )


if __name__ == "__main__":
    main()
