# MenuTitle: Archived Example Launcher
# this_file: Scripts/Archived Launcher/Archived Example Launcher.py
# preserved-source-sha256: 915eb0d92ab3d33020d4824b151cb0c6066fd323702f9e1073b70fbd6cb20f6e
"""Launch the preserved archive entry: Archived Example Launcher.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part1/launcher.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Launcher > Archived Example Launcher.
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
        Path(__file__).resolve().parents[2] / 'rescued/part1/launcher.py'
    )


if __name__ == "__main__":
    main()
