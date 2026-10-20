# this_file: Scripts/Archived UI L-Z/Widgets - Official movie - a3b3cbe51c1506c6.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 2e54c5e62a39611be5244888127c8a36bec8461a8f1af584aeb56b3e2ce05e39
"""Launch the preserved archive entry: Widgets - Official movie - a3b3cbe51c1506c6.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-official/movie-a3b3cbe51c1506c6.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - Official movie - a3b3cbe51c1506c6.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-official/movie-a3b3cbe51c1506c6.py'
    )


if __name__ == "__main__":
    main()
