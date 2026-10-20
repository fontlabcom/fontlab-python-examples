# this_file: Scripts/Archived UI L-Z/Opengl - Official 2dpainting - c82d1af7d1a7b0cf.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f6d04cce9f39c1d796a987e2b3d5c1b24ca3ed5cba5c5d18b79a1909e47cd854
"""Launch the preserved archive entry: Opengl - Official 2dpainting - c82d1af7d1a7b0cf.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Opengl - Official 2dpainting - c82d1af7d1a7b0cf.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/opengl/pyqt-official/2dpainting-c82d1af7d1a7b0cf.py'
    )


if __name__ == "__main__":
    main()
