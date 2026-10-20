# MenuTitle: GetGo - Compare Master Topology
# this_file: Scripts/Archived GetGo/GetGo - Compare Master Topology.py
# preserved-source-sha256: fcf75898a46cca80ed0f7e36627864c18a2a9c8e781793fcd70d43fd7a74015e
"""Launch the preserved archive entry: GetGo - Compare Master Topology.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/getgo/master_compatibility.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived GetGo > GetGo - Compare Master Topology.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/getgo/master_compatibility.py'
    )


if __name__ == "__main__":
    main()
