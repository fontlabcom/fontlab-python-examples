# this_file: Scripts/Archived Official/dragdroprobot-2cd6ffc2b2ed65bb - 81a228e1.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: c021aba5ca45ca9cf3b0fde77ceb654ff5077191380d83cef5d84c1aec9c8313
"""Launch the preserved archive entry: dragdroprobot-2cd6ffc2b2ed65bb - 81a228e1.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Official > dragdroprobot-2cd6ffc2b2ed65bb - 81a228e1.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/pyqt-official-ports/ports/graphicsview/pyqt-official/dragdroprobot-2cd6ffc2b2ed65bb.py'
    )


if __name__ == "__main__":
    main()
