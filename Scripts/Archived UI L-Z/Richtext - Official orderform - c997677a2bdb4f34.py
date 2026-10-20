# this_file: Scripts/Archived UI L-Z/Richtext - Official orderform - c997677a2bdb4f34.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 05648294ef7afc8ec0778362266046e2af2d2c7b5072d2a8307b0a85882cce91
"""Launch the preserved archive entry: Richtext - Official orderform - c997677a2bdb4f34.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Richtext - Official orderform - c997677a2bdb4f34.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/richtext/pyqt-official/orderform-c997677a2bdb4f34.py'
    )


if __name__ == "__main__":
    main()
