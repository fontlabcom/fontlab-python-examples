# this_file: Scripts/Archived Official/relationaltablemodel-9030a87a532b8d8f - bb5bbd01.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: fa0b65f1ae6d9709f7cb7f9347e5746b087804d5b0c7f041e2b58530b1f5d007
"""Launch the preserved archive entry: relationaltablemodel-9030a87a532b8d8f - bb5bbd01.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > relationaltablemodel-9030a87a532b8d8f - bb5bbd01.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/relationaltablemodel-9030a87a532b8d8f.py'
    )


if __name__ == "__main__":
    main()
