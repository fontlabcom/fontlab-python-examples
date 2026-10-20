# this_file: Scripts/Archived Official/chart-306c12d5cc1db46c - 92011e52.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 0bdf280e85649088518dfc0647ad99a46ab7f446eac7b52aed2eee1d25912956
"""Launch the preserved archive entry: chart-306c12d5cc1db46c - 92011e52.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > chart-306c12d5cc1db46c - 92011e52.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/itemviews/pyqt-official/chart-306c12d5cc1db46c.py'
    )


if __name__ == "__main__":
    main()
