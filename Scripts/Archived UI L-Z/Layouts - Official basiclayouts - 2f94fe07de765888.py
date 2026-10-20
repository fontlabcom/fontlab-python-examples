# this_file: Scripts/Archived UI L-Z/Layouts - Official basiclayouts - 2f94fe07de765888.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 6fa0e1268b7c81dbf6c373ae9ebb98ef86ffa0d7c8207ab78a003e65fc49a00d
"""Launch the preserved archive entry: Layouts - Official basiclayouts - 2f94fe07de765888.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Layouts - Official basiclayouts - 2f94fe07de765888.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/layouts/pyqt-official/basiclayouts-2f94fe07de765888.py'
    )


if __name__ == "__main__":
    main()
