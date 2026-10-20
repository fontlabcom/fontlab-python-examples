# MenuTitle: GetGo - Sidebearings from H
# this_file: Scripts/Archived GetGo/GetGo - Sidebearings from H.py
# preserved-source-sha256: 46819ae9909a25291ca3b9558dbe2a1241e7f504fc1ea113a6679047adba3143
"""Launch the preserved archive entry: GetGo - Sidebearings from H.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/getgo/spacing.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived GetGo > GetGo - Sidebearings from H.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/getgo/spacing.py'
    )


if __name__ == "__main__":
    main()
