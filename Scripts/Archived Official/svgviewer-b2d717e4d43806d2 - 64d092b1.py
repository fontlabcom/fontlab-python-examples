# this_file: Scripts/Archived Official/svgviewer-b2d717e4d43806d2 - 64d092b1.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: d2ccb421fa24dcc962e4abda1d081a7b5a0a4615a4aef6e1a4d2c8e4490c7665
"""Launch the preserved archive entry: svgviewer-b2d717e4d43806d2 - 64d092b1.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > svgviewer-b2d717e4d43806d2 - 64d092b1.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/svgviewer-b2d717e4d43806d2.py'
    )


if __name__ == "__main__":
    main()
