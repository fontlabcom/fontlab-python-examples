# this_file: Scripts/Archived UI L-Z/Multimedia - QPainter - 1151b1cb878f192a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 1b1bb01481bf852d248c294262da0aa4b9d951612f54d67e3dc911ec2ce5f4a5
"""Launch the preserved archive entry: Multimedia - QPainter - 1151b1cb878f192a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/multimedia/pyqt-examples/main-1151b1cb878f192a.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Multimedia - QPainter - 1151b1cb878f192a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/multimedia/pyqt-examples/main-1151b1cb878f192a.py'
    )


if __name__ == "__main__":
    main()
