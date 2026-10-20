# this_file: Scripts/Archived UI L-Z/Mainwindows - Official menus - 60d40ce5671653cf.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 5db7de5bb81c11df39be0c6e83c9a39d1f42463982413e62eb27253f0efb58a6
"""Launch the preserved archive entry: Mainwindows - Official menus - 60d40ce5671653cf.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Mainwindows - Official menus - 60d40ce5671653cf.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/mainwindows/pyqt-official/menus-60d40ce5671653cf.py'
    )


if __name__ == "__main__":
    main()
