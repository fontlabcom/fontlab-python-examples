# this_file: Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - strset_list -- 81da36a4000a.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: ab94e3837566b26468ce9d0348df4bbad1a3eb58f90cd44b7871a333527af167
"""Launch the preserved archive entry: P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - strset_list -- 81da36a4000a.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/strset_list.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - strset_list -- 81da36a4000a.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/strset_list.py'
    )


if __name__ == "__main__":
    main()
