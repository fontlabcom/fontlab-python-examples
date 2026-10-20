# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/itemviews - puzzle-878fe9f714df3b5e.py
# preserved-source-sha256: f118f4ca17619e41d7d940d1a49524d07a7e6bdae3bfa14dee4fd930ba5dfd8c
"""Launch the preserved archive entry: itemviews - puzzle-878fe9f714df3b5e.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > itemviews - puzzle-878fe9f714df3b5e.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/itemviews/pyqt-official/puzzle-878fe9f714df3b5e.py'
    )


if __name__ == "__main__":
    main()
