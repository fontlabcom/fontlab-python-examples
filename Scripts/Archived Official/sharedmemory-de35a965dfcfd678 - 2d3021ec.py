# this_file: Scripts/Archived Official/sharedmemory-de35a965dfcfd678 - 2d3021ec.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: a94737070771a8b73be8b767b0c90e9c0cdeabcce742d53a6eba580624e58e0b
"""Launch the preserved archive entry: sharedmemory-de35a965dfcfd678 - 2d3021ec.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > sharedmemory-de35a965dfcfd678 - 2d3021ec.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/ipc/pyqt-official/sharedmemory-de35a965dfcfd678.py'
    )


if __name__ == "__main__":
    main()
