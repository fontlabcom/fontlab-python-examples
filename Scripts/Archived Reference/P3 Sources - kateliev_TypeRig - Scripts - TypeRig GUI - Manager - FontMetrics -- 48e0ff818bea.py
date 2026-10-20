# this_file: Scripts/Archived Reference/P3 Sources - kateliev_TypeRig - Scripts - TypeRig GUI - Manager - FontMetrics -- 48e0ff818bea.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: 238b24fa473a611284513bd1314d68503b1d6ccf3900f139da793f51df840281
"""Launch the preserved archive entry: P3 Sources - kateliev_TypeRig - Scripts - TypeRig GUI - Manager - FontMetrics -- 48e0ff818bea.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/kateliev_TypeRig/Scripts/TypeRig GUI/Manager/FontMetrics.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - kateliev_TypeRig - Scripts - TypeRig GUI - Manager - FontMetrics -- 48e0ff818bea.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/kateliev_TypeRig/Scripts/TypeRig GUI/Manager/FontMetrics.py'
    )


if __name__ == "__main__":
    main()
