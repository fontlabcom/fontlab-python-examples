# this_file: Scripts/Archived UI L-Z/Threads - Official mandelbrot - 0788354954c8e613.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: b58d3caa4e80202c5067b4e7b86eabc46b7dd92ae61a3da7f6be28bc28f43414
"""Launch the preserved archive entry: Threads - Official mandelbrot - 0788354954c8e613.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Threads - Official mandelbrot - 0788354954c8e613.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/threads/pyqt-official/mandelbrot-0788354954c8e613.py'
    )


if __name__ == "__main__":
    main()
