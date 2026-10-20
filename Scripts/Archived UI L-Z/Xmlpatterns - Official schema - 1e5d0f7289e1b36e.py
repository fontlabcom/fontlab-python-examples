# this_file: Scripts/Archived UI L-Z/Xmlpatterns - Official schema - 1e5d0f7289e1b36e.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 1070c8a653367f30da3a68b3454adafcafd8d620b0fd1140033c43b2b1b73830
"""Launch the preserved archive entry: Xmlpatterns - Official schema - 1e5d0f7289e1b36e.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived UI L-Z > Xmlpatterns - Official schema - 1e5d0f7289e1b36e.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/ports/xmlpatterns/pyqt-official/schema-1e5d0f7289e1b36e.py'
    )


if __name__ == "__main__":
    main()
