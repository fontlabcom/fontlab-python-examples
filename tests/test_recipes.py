# this_file: tests/test_recipes.py
"""Recipes in examples/recipes: layout, host-free import and their pure helpers.

Native behaviour is checked by each recipe's native.py inside FontLab; these
tests need no FontLab.
"""

import ast
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

RECIPES = Path(__file__).resolve().parents[1] / "examples" / "recipes"
NAMES = sorted(
    p.name
    for p in RECIPES.iterdir()
    if p.is_dir() and not p.name.startswith(("_", "."))
)
NATIVE = {
    "fontlab",
    "fontgate",
    "fontpr",
    "PythonQt",
    "fontlabapp",
    "fontlab_glyport",
    "GlyphsApp",
}
ALLOWED = set(sys.stdlib_module_names) | NATIVE


def load(name, file="recipe.py"):
    spec = importlib.util.spec_from_file_location(
        f"recipe_{name}", RECIPES / name / file
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def imported(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            yield node.module.split(".")[0]


@pytest.mark.parametrize("name", NAMES)
def test_recipe_when_folder_then_script_readme_and_native_driver(name):
    folder = RECIPES / name
    for file in ("recipe.py", "README.md", "native.py"):
        assert (folder / file).is_file(), f"{name} lacks {file}"
    readme = (folder / "README.md").read_text(encoding="utf-8")
    for section in (
        "**Purpose.**",
        "**Provenance.**",
        "**Licence.**",
        "**Native check**",
    ):
        assert section in readme, f"{name}/README.md lacks {section}"
    source = (folder / "recipe.py").read_text(encoding="utf-8")
    assert source.startswith("#MenuTitle: "), f"{name}: FontLab/Glyphs menu title first"
    assert f"# this_file: examples/recipes/{name}/recipe.py" in source


@pytest.mark.parametrize("name", NAMES)
def test_recipe_when_parsed_then_stdlib_and_host_modules_only(name):
    for file in ("recipe.py", "native.py"):
        path = RECIPES / name / file
        tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        extra = {"fontlab_remopy", "_native"} if file == "native.py" else set()
        assert set(imported(tree)) <= ALLOWED | extra, (
            f"{name}/{file} imports {set(imported(tree)) - ALLOWED - extra}"
        )


@pytest.mark.parametrize("name", NAMES)
def test_recipe_when_imported_outside_fontlab_then_no_native_module_and_run_entry(name):
    code = (
        "import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('r', {str(RECIPES / name / 'recipe.py')!r})\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        f"loaded = sorted(set(sys.modules) & set({sorted(NATIVE)!r}))\n"
        "assert not loaded, loaded\n"
        "import inspect\n"
        "params = inspect.signature(m.run).parameters\n"
        "assert 'font_id' in params and 'glyph_names' in params, list(params)\n"
    )
    subprocess.run([sys.executable, "-I", "-c", code], check=True)


def test_layer_backup_name_when_taken_then_next_free():
    backup_name = load("layer_backup").backup_name
    assert backup_name("Regular", ["Regular"]) == "Regular backup"
    assert backup_name("Regular", ["Regular", "Regular backup"]) == "Regular backup 2"
    assert backup_name("Bold", ["Bold backup", "Bold backup 2"], " old") == "Bold old"
    assert backup_name("Bold", ["Bold backup", "Bold backup 2"]) == "Bold backup 3"


def test_round_snap_when_halves_and_grid_then_away_from_zero():
    snap = load("round_coordinates").snap
    assert [snap(v) for v in (0.5, 1.5, -0.5, -2.5, 2.49, 0.0)] == [1, 2, -1, -3, 2, 0]
    assert snap(12.4, 5) == 10 and snap(12.5, 5) == 15
    with pytest.raises(ValueError):
        snap(1, 0)


def test_contour_direction_when_nested_then_outer_ccw_counter_cw():
    recipe = load("contour_direction")
    outer = [(0, 0), (500, 0), (500, 700), (0, 700)]
    counter = [(100, 100), (100, 600), (400, 600), (400, 100)]
    island = [(200, 200), (300, 200), (300, 300), (200, 300)]
    assert recipe.signed_area(outer) > 0 > recipe.signed_area(counter)
    shapes = [outer, counter, island]
    assert [recipe.wants_counter_clockwise(shapes, i) for i in range(3)] == [
        True,
        False,
        True,
    ]
    assert (
        recipe.start_index([(5, 9), (3, 0), (1, 0), (0, 0)], [True, True, True, False])
        == 2
    )


def test_anchor_positions_when_bounds_then_centred_and_rounded():
    positions = load("anchors_from_bounds").anchor_positions
    assert positions(50, 0, 551, 700, 20) == {"top": (300, 720), "bottom": (300, 0)}


def test_respace_when_reference_sidebearings_then_shift_and_width():
    recipe = load("sidebearings_from_reference")
    assert recipe.sidebearings(60, 540, 600) == (60, 60)
    assert recipe.respace(200, 300, 60, 60) == (-140, 220)


def test_parse_pairs_when_comments_classes_and_junk_then_pairs_and_problems():
    recipe = load("kerning_from_text")
    pairs, problems = recipe.parse_pairs(
        "# c\nA V -80\n\n@O_left T -40.5  # x\nbad line\nA B c\n"
    )
    assert pairs == [("A", "V", -80.0), ("@O_left", "T", -40.5)]
    assert problems == ["bad line", "A B c"]
    assert [recipe.whole_units(v) for v in (-75.5, 75.5, -0.4, 12.0)] == [
        -76,
        76,
        0,
        12,
    ]


def test_glyph_actions_batch_when_no_glyph_names_then_refuses_before_fontlab():
    with pytest.raises(ValueError, match="glyph_names"):
        load("glyph_actions_batch").run()
