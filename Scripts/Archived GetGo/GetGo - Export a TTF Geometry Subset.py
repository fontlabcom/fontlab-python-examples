# MenuTitle: GetGo - Export a TTF Geometry Subset
# this_file: Scripts/Archived GetGo/GetGo - Export a TTF Geometry Subset.py
# preserved-source-sha256: f06122a7a4d65a3d410057339fa5fc7c2b19312d69e355c0a225f4ca29446de0
"""Launch the preserved archive entry: GetGo - Export a TTF Geometry Subset.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/getgo/export_ttf.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived GetGo > GetGo - Export a TTF Geometry Subset.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/getgo/export_ttf.py'
    )


if __name__ == "__main__":
    main()
