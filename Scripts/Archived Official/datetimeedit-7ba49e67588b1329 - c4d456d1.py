# this_file: Scripts/Archived Official/datetimeedit-7ba49e67588b1329 - c4d456d1.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 465bd7c5044e1e51c19b62a764695a8d8d37350c06d831db8fee249c8a5d2de1
"""Launch the preserved archive entry: datetimeedit-7ba49e67588b1329 - c4d456d1.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/designer/pyqt-official/datetimeedit-7ba49e67588b1329.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > datetimeedit-7ba49e67588b1329 - c4d456d1.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/designer/pyqt-official/datetimeedit-7ba49e67588b1329.py'
    )


if __name__ == "__main__":
    main()
