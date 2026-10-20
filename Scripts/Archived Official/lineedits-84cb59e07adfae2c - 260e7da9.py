# this_file: Scripts/Archived Official/lineedits-84cb59e07adfae2c - 260e7da9.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 79277f27ddb0bbb959fe21aa8202e9ec831dc91bdc178d3b5a987bc50fe1f3ad
"""Launch the preserved archive entry: lineedits-84cb59e07adfae2c - 260e7da9.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/lineedits-84cb59e07adfae2c.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > lineedits-84cb59e07adfae2c - 260e7da9.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/lineedits-84cb59e07adfae2c.py'
    )


if __name__ == "__main__":
    main()
