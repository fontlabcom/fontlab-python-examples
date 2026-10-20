# this_file: Scripts/Archived Official/adding-8847cbce50b72500 - b3713f5c.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: c066dac22e9f3718b16a497ca4bbcfbaa846963d0b1f0a0e9c8cb0d46f976054
"""Launch the preserved archive entry: adding-8847cbce50b72500 - b3713f5c.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/adding-8847cbce50b72500.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > adding-8847cbce50b72500 - b3713f5c.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/adding-8847cbce50b72500.py'
    )


if __name__ == "__main__":
    main()
