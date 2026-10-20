# this_file: Scripts/Archived Reference/P3 Sources - Bluscream_pyTSon_plugins - scripts - channelGroupManager - __init__ -- a53d1119bebc.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source-sha256: f99c70b0e11c813defa7e12e0dcfe9084ac0a995431dfdc72da910caa55a8f85
"""Launch the preserved archive entry: P3 Sources - Bluscream_pyTSon_plugins - scripts - channelGroupManager - __init__ -- a53d1119bebc.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part3/sources/Bluscream_pyTSon_plugins/scripts/channelGroupManager/__init__.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Reference > P3 Sources - Bluscream_pyTSon_plugins - scripts - channelGroupManager - __init__ -- a53d1119bebc.
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
        Path(__file__).resolve().parents[2] / 'rescued/part3/sources/Bluscream_pyTSon_plugins/scripts/channelGroupManager/__init__.py'
    )


if __name__ == "__main__":
    main()
