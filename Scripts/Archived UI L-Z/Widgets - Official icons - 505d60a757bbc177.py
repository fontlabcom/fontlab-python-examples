# this_file: Scripts/Archived UI L-Z/Widgets - Official icons - 505d60a757bbc177.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 68749115c6766e274fc7114a18ab9ef26a1cd0434241b6abab5ddb6eeed00010
"""Launch the preserved archive entry: Widgets - Official icons - 505d60a757bbc177.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/widgets/pyqt-official/icons-505d60a757bbc177.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Widgets - Official icons - 505d60a757bbc177.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/widgets/pyqt-official/icons-505d60a757bbc177.py'
    )


if __name__ == "__main__":
    main()
