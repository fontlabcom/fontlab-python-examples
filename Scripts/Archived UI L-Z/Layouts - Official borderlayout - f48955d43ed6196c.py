# this_file: Scripts/Archived UI L-Z/Layouts - Official borderlayout - f48955d43ed6196c.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 61dce583b8707e5724dc6e28f4f86b2b32884dd9af5f4a25a3a145a54d146dd4
"""Launch the preserved archive entry: Layouts - Official borderlayout - f48955d43ed6196c.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Layouts - Official borderlayout - f48955d43ed6196c.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/layouts/pyqt-official/borderlayout-f48955d43ed6196c.py'
    )


if __name__ == "__main__":
    main()
