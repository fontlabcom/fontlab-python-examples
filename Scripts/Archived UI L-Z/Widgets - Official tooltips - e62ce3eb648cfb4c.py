# this_file: Scripts/Archived UI L-Z/Widgets - Official tooltips - e62ce3eb648cfb4c.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 698bd103c2938c32d97ee15e5243f50e708f5064e2fe6e9bb8d2684350bfdf01
"""Launch the preserved archive entry: Widgets - Official tooltips - e62ce3eb648cfb4c.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-official/tooltips-e62ce3eb648cfb4c.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - Official tooltips - e62ce3eb648cfb4c.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-official/tooltips-e62ce3eb648cfb4c.py'
    )


if __name__ == "__main__":
    main()
