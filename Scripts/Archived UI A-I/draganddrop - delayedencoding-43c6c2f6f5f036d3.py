# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/draganddrop - delayedencoding-43c6c2f6f5f036d3.py
# preserved-source-sha256: e2f83fc8e2a0ae2bf783f0f773fa0c088f01a20482a31d41adbb958f97ab4d34
"""Launch the preserved archive entry: draganddrop - delayedencoding-43c6c2f6f5f036d3.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > draganddrop - delayedencoding-43c6c2f6f5f036d3.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/draganddrop/pyqt-official/delayedencoding-43c6c2f6f5f036d3.py'
    )


if __name__ == "__main__":
    main()
