# this_file: Scripts/Archived UI L-Z/Richtext - Official textedit - b34b2f696a977e74.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 74dad1c6c8dec850fbe1e21ceb88c0ac46f8dc61d6e7b1cd9cca4f1fd26f4efc
"""Launch the preserved archive entry: Richtext - Official textedit - b34b2f696a977e74.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Richtext - Official textedit - b34b2f696a977e74.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/richtext/pyqt-official/textedit-b34b2f696a977e74.py'
    )


if __name__ == "__main__":
    main()
