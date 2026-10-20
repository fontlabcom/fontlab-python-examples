# SPDX-License-Identifier: Apache-2.0
# this_file: Scripts/Archived UI A-I/insights - owned-repl.py
# preserved-source-sha256: 3b5fb1184dd28f2caa23b1e90eb53308a0d77ead01f5a0bc4fd3cc62bf7d95df
"""Launch the preserved archive entry: insights - owned-repl.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/insights/owned-repl.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI A-I > insights - owned-repl.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/insights/owned-repl.py'
    )


if __name__ == "__main__":
    main()
