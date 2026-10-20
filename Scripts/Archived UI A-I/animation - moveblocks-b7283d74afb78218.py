# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/animation - moveblocks-b7283d74afb78218.py
# preserved-source-sha256: 1ac9db7d122e92313f1e386190eb2c54ad9da2686820a81397759e9e3e1164ec
"""Launch the preserved archive entry: animation - moveblocks-b7283d74afb78218.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > animation - moveblocks-b7283d74afb78218.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/animation/pyqt-official/moveblocks-b7283d74afb78218.py'
    )


if __name__ == "__main__":
    main()
