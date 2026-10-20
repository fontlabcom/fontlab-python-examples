# this_file: Scripts/Archived Official/separations-2d36e0fe43f5d49a - 756d7d5b.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f5e1af92ebcf6d666477dc2b3f6d85cd324bc39ea1940982913b60b15c7285c6
"""Launch the preserved archive entry: separations-2d36e0fe43f5d49a - 756d7d5b.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > separations-2d36e0fe43f5d49a - 756d7d5b.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/mainwindows/pyqt-official/separations-2d36e0fe43f5d49a.py'
    )


if __name__ == "__main__":
    main()
