# this_file: Scripts/Archived Reference/P3 Sources - kateliev_TypeRig - Lib - typerig - proxy - fl - objects - sampler -- b36197a778e8.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 0abf8fb676a055dd7b55e0d05a9536fc920040a438b6559b9049dd605ca2dbe8
"""Launch the preserved archive entry: P3 Sources - kateliev_TypeRig - Lib - typerig - proxy - fl - objects - sampler -- b36197a778e8.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/kateliev_TypeRig/Lib/typerig/proxy/fl/objects/sampler.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - kateliev_TypeRig - Lib - typerig - proxy - fl - objects - sampler -- b36197a778e8.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/kateliev_TypeRig/Lib/typerig/proxy/fl/objects/sampler.py'
    )


if __name__ == "__main__":
    main()
