# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/graphicsview - dragdroprobot-2cd6ffc2b2ed65bb.py
# preserved-source-sha256: f1faf59693b2054c207de5811e7d721260755e6a5675f199f3472e3d520204d2
"""Launch the preserved archive entry: graphicsview - dragdroprobot-2cd6ffc2b2ed65bb.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > graphicsview - dragdroprobot-2cd6ffc2b2ed65bb.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py'
    )


if __name__ == "__main__":
    main()
