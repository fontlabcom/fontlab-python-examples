# this_file: Scripts/Archived Official/classwizard-035f3fbd2b81479a - 3a59c388.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 93b55b89157b47b8676db5ce9e9a64641bf7d6290bc576f2c5af16079beef92d
"""Launch the preserved archive entry: classwizard-035f3fbd2b81479a - 3a59c388.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > classwizard-035f3fbd2b81479a - 3a59c388.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/dialogs/pyqt-official/classwizard-035f3fbd2b81479a.py'
    )


if __name__ == "__main__":
    main()
