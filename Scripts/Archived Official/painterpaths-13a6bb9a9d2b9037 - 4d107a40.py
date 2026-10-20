# this_file: Scripts/Archived Official/painterpaths-13a6bb9a9d2b9037 - 4d107a40.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: ae79ea27f4bb5bb28912a0d9c5ceb8524f3f1c09ca7161bd408bc0e6ca88efb3
"""Launch the preserved archive entry: painterpaths-13a6bb9a9d2b9037 - 4d107a40.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > painterpaths-13a6bb9a9d2b9037 - 4d107a40.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/painting/pyqt-official/painterpaths-13a6bb9a9d2b9037.py'
    )


if __name__ == "__main__":
    main()
