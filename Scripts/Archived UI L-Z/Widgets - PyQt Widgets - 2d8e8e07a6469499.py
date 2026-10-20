# this_file: Scripts/Archived UI L-Z/Widgets - PyQt Widgets - 2d8e8e07a6469499.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 9555034b87536005ea521dc9070c5359454aff7d408d63341e62b106e01ad980
"""Launch the preserved archive entry: Widgets - PyQt Widgets - 2d8e8e07a6469499.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-examples/main-2d8e8e07a6469499.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - PyQt Widgets - 2d8e8e07a6469499.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-examples/main-2d8e8e07a6469499.py'
    )


if __name__ == "__main__":
    main()
