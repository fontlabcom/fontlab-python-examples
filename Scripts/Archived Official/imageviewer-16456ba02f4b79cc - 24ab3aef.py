# this_file: Scripts/Archived Official/imageviewer-16456ba02f4b79cc - 24ab3aef.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: a56d05bd0de0204bb29e96995d043b9054104eb370fc80a36bc398db77a29bac
"""Launch the preserved archive entry: imageviewer-16456ba02f4b79cc - 24ab3aef.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > imageviewer-16456ba02f4b79cc - 24ab3aef.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/imageviewer-16456ba02f4b79cc.py'
    )


if __name__ == "__main__":
    main()
