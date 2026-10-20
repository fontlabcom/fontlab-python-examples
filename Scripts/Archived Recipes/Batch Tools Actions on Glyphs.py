# MenuTitle: Batch Tools Actions on Glyphs
# this_file: Scripts/Archived Recipes/Batch Tools Actions on Glyphs.py
# preserved-source-sha256: 5c0ccb08425e3b62fb823346a8a6e16d6d38f2898a4e598b20882c9be6a98675
"""Launch the preserved archive entry: Batch Tools Actions on Glyphs.

Purpose: Run this entry's preserved implementation through Fly's shared App
helper. The entry retains its original behavior; it is an archive launcher.

Setup: Use FontLab 9 with Python 3.11, Fly and FontLab App available. Keep the
complete rescued tree beside Scripts. Read the preserved source and its resource
and dependency requirements before use:
rescued/part2/examples/recipes/glyph_actions_batch/recipe.py
Use an owned disposable font copy if the source requires a font.

Run: Select Scripts > Archived Recipes > Batch Tools Actions on Glyphs.
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
        Path(__file__).resolve().parents[2] / 'rescued/part2/examples/recipes/glyph_actions_batch/recipe.py'
    )


if __name__ == "__main__":
    main()
