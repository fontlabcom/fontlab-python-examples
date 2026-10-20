# this_file: Scripts/Archived Official/spinboxes-468179092748a72e - 5895d0ae.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: e25b26cd135fd40ef1ed9316a402483d676ba7606da94007f00078993b5fa54b
"""Launch the preserved archive entry: spinboxes-468179092748a72e - 5895d0ae.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/spinboxes-468179092748a72e.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > spinboxes-468179092748a72e - 5895d0ae.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/spinboxes-468179092748a72e.py'
    )


if __name__ == "__main__":
    main()
