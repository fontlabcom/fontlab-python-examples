# this_file: Scripts/Archived Official/signal-0a13f60f5f0561db - 3240d755.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 4d7ff622b8ddcc9d0050ae6a8d2d17809390adf6f46303e49bab62be08729a2c
"""Launch the preserved archive entry: signal-0a13f60f5f0561db - 3240d755.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/signal-0a13f60f5f0561db.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > signal-0a13f60f5f0561db - 3240d755.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/qml/pyqt-official/signal-0a13f60f5f0561db.py'
    )


if __name__ == "__main__":
    main()
