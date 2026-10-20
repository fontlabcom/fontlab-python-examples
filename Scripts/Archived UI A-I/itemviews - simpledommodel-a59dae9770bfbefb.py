# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/itemviews - simpledommodel-a59dae9770bfbefb.py
# preserved-source-sha256: c17809b93a3fff1601c20e15f233edbf687f023430e86bf1986772e38bf712d6
"""Launch the preserved archive entry: itemviews - simpledommodel-a59dae9770bfbefb.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > itemviews - simpledommodel-a59dae9770bfbefb.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/itemviews/pyqt-official/simpledommodel-a59dae9770bfbefb.py'
    )


if __name__ == "__main__":
    main()
