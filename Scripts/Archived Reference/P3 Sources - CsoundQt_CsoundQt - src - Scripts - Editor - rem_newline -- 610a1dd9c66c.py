# this_file: Scripts/Archived Reference/P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - rem_newline -- 610a1dd9c66c.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: b8e8d63f9609c10043d7c92a2e0a8141a6deb24f8e400f41fa2134d51e72a057
"""Launch the preserved archive entry: P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - rem_newline -- 610a1dd9c66c.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/rem_newline.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - CsoundQt_CsoundQt - src - Scripts - Editor - rem_newline -- 610a1dd9c66c.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/CsoundQt_CsoundQt/src/Scripts/Editor/rem_newline.py'
    )


if __name__ == "__main__":
    main()
