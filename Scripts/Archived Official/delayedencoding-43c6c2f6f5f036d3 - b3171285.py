# this_file: Scripts/Archived Official/delayedencoding-43c6c2f6f5f036d3 - b3171285.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f422be58b93475a25e7c2843f5e8e7271a8f31158afd21d261e6fdacd82b7af3
"""Launch the preserved archive entry: delayedencoding-43c6c2f6f5f036d3 - b3171285.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > delayedencoding-43c6c2f6f5f036d3 - b3171285.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py'
    )


if __name__ == "__main__":
    main()
