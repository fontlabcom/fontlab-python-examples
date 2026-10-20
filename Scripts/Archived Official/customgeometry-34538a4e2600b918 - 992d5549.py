# this_file: Scripts/Archived Official/customgeometry-34538a4e2600b918 - 992d5549.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: bb4d545d6ec4dc29a45617e8b45292caa9f3b809e16d9f4940527010960486ea
"""Launch the preserved archive entry: customgeometry-34538a4e2600b918 - 992d5549.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/customgeometry-34538a4e2600b918.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > customgeometry-34538a4e2600b918 - 992d5549.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/quick/pyqt-official/customgeometry-34538a4e2600b918.py'
    )


if __name__ == "__main__":
    main()
