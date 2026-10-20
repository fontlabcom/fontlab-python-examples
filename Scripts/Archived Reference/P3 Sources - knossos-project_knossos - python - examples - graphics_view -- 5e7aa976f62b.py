# this_file: Scripts/Archived Reference/P3 Sources - knossos-project_knossos - python - examples - graphics_view -- 5e7aa976f62b.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 052c07188fc22262b362d092d7cf85eb17cff0496651b28f609a2cca0963b67c
"""Launch the preserved archive entry: P3 Sources - knossos-project_knossos - python - examples - graphics_view -- 5e7aa976f62b.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/knossos-project_knossos/python/examples/graphics_view.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - knossos-project_knossos - python - examples - graphics_view -- 5e7aa976f62b.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/knossos-project_knossos/python/examples/graphics_view.py'
    )


if __name__ == "__main__":
    main()
