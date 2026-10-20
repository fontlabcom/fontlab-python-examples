# this_file: Scripts/Archived Official/basicdrawing-907f39d8bf387501 - ea433456.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 94c7a27d22a78955265a73c0d98383088c334d50d100eb330b242b84fbee0bab
"""Launch the preserved archive entry: basicdrawing-907f39d8bf387501 - ea433456.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > basicdrawing-907f39d8bf387501 - ea433456.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/basicdrawing-907f39d8bf387501.py'
    )


if __name__ == "__main__":
    main()
