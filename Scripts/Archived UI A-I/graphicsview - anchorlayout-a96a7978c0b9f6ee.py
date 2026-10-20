# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/graphicsview - anchorlayout-a96a7978c0b9f6ee.py
# preserved-source-sha256: 4de40f5bc168015793f3529ef70f2e69dc46be41b38d17afb29f7e34ef8d717f
"""Launch the preserved archive entry: graphicsview - anchorlayout-a96a7978c0b9f6ee.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > graphicsview - anchorlayout-a96a7978c0b9f6ee.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/graphicsview/pyqt-official/anchorlayout-a96a7978c0b9f6ee.py'
    )


if __name__ == "__main__":
    main()
