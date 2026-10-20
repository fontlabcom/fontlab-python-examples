# this_file: Scripts/Archived Official/shapedclock-248e64416b9b218c - b8d5a1b1.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 93afa0ed4b632a251d8e42d0b049f0ed85da736b6f8db42aa874adc0d632f4b0
"""Launch the preserved archive entry: shapedclock-248e64416b9b218c - b8d5a1b1.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > shapedclock-248e64416b9b218c - b8d5a1b1.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/shapedclock-248e64416b9b218c.py'
    )


if __name__ == "__main__":
    main()
