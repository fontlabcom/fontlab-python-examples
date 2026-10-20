# this_file: Scripts/Archived Reference/P3 Sources - hlolli_CsoundQt - src - Scripts - Useful - UI_with_QtDesigner -- 77b62bb6235a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 1b1e67db765f980ecce69ba9fb4fd153127a2f303c76d8b75888f24f0e1c57a6
"""Launch the preserved archive entry: P3 Sources - hlolli_CsoundQt - src - Scripts - Useful - UI_with_QtDesigner -- 77b62bb6235a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Useful/UI_with_QtDesigner.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - hlolli_CsoundQt - src - Scripts - Useful - UI_with_QtDesigner -- 77b62bb6235a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/hlolli_CsoundQt/src/Scripts/Useful/UI_with_QtDesigner.py'
    )


if __name__ == "__main__":
    main()
