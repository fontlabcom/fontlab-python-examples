# this_file: Scripts/Archived Reference/P3 Sources - openhumanoids_director - src - app - WrapPythonQt -- e1f1724a6b9b.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 72938ac6f0df23b31b8b72cfa851c63649e496c5c84ee4bdfca3d61c4f38b00e
"""Launch the preserved archive entry: P3 Sources - openhumanoids_director - src - app - WrapPythonQt -- e1f1724a6b9b.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/openhumanoids_director/src/app/WrapPythonQt.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - openhumanoids_director - src - app - WrapPythonQt -- e1f1724a6b9b.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/openhumanoids_director/src/app/WrapPythonQt.py'
    )


if __name__ == "__main__":
    main()
