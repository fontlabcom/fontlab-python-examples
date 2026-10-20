# this_file: Scripts/Archived Official/tablemodel-0677ebfd7fa2cc60 - b4800039.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 983329e5248839393d3debd5ee96f588508c0293132094c7f99cb48bd84ddd66
"""Launch the preserved archive entry: tablemodel-0677ebfd7fa2cc60 - b4800039.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > tablemodel-0677ebfd7fa2cc60 - b4800039.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/sql/pyqt-official/tablemodel-0677ebfd7fa2cc60.py'
    )


if __name__ == "__main__":
    main()
