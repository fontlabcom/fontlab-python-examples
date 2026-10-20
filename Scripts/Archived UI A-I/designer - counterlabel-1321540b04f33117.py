# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/designer - counterlabel-1321540b04f33117.py
# preserved-source-sha256: 96f3d82f949777f1d582ac4921169db87ba3d6f7d8195fdaaddce18b0cf788d2
"""Launch the preserved archive entry: designer - counterlabel-1321540b04f33117.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/designer/pyqt-official/counterlabel-1321540b04f33117.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > designer - counterlabel-1321540b04f33117.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/designer/pyqt-official/counterlabel-1321540b04f33117.py'
    )


if __name__ == "__main__":
    main()
