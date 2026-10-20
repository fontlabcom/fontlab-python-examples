# MenuTitle: Place Top and Bottom Anchors
# this_file: Scripts/Archived Recipes/Place Top and Bottom Anchors.py
# preserved-source-sha256: 77ed425e774fcf083348cc28eb07eadf5a9bc1a4d6c5e5e7af9616b44a87479e
"""Launch the preserved archive entry: Place Top and Bottom Anchors.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/anchors_from_bounds/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Place Top and Bottom Anchors.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/recipes/anchors_from_bounds/recipe.py'
    )


if __name__ == "__main__":
    main()
