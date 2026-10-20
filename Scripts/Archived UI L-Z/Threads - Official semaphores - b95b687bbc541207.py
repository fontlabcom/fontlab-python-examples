# this_file: Scripts/Archived UI L-Z/Threads - Official semaphores - b95b687bbc541207.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 1a82b277e5e459b1ab17380c23be1364399449be1db325f9cd0f0d7aa4161144
"""Launch the preserved archive entry: Threads - Official semaphores - b95b687bbc541207.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/threads/pyqt-official/semaphores-b95b687bbc541207.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Threads - Official semaphores - b95b687bbc541207.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/threads/pyqt-official/semaphores-b95b687bbc541207.py'
    )


if __name__ == "__main__":
    main()
