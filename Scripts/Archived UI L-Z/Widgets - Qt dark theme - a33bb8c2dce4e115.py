# this_file: Scripts/Archived UI L-Z/Widgets - Qt dark theme - a33bb8c2dce4e115.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f42a89468298fbbba6432ccc349fc4baf5b78e1988f10a11c5eb545cbb81d299
"""Launch the preserved archive entry: Widgets - Qt dark theme - a33bb8c2dce4e115.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-examples/main-a33bb8c2dce4e115.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - Qt dark theme - a33bb8c2dce4e115.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-examples/main-a33bb8c2dce4e115.py'
    )


if __name__ == "__main__":
    main()
