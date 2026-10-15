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
    "Foundation",  # PyObjC, inside Glyphs
}
ALLOWED = set(sys.stdlib_module_names) | NATIVE


def test_recipes_when_listed_then_eight_or_more():
    assert len(NAMES) >= 8, NAMES


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
    for path in sorted((RECIPES / name).glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        file = path.name
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
    shapes = [recipe.segments(s, [True] * 4) for s in (outer, counter, island)]
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


class Node:
    def __init__(self, x, y, type="line"):
        self.x, self.y, self.type = x, y, type


class Path:
    def __init__(self, points, closed=True):
        self.nodes, self.closed = [Node(x, y) for x, y in points], closed


class Layer:
    def __init__(self, *paths, width=500):
        self.paths, self.anchors, self.width = list(paths), [], width


def test_tabular_figures_when_layer_then_centred_without_glyphs_app():
    script = load("glyphs_tabular_figures", "tabular_figures.py")
    layer = Layer(Path([(100, 0), (100, 700), (200, 700), (200, 0)]), width=350)
    assert script.centre_in_width(layer, 600) == 150
    assert [n.x for n in layer.paths[0].nodes] == [
        250,
        250,
        350,
        350,
    ] and layer.width == 600
    assert script.centre_in_width(Layer(), 600) is None


def test_path_problems_when_planted_then_each_reported_once():
    problems = load("glyphs_path_report", "path_report.py").path_problems
    assert problems(Layer(Path([(0, 0), (0, 700), (500, 700), (500, 0)]))) == []
    assert problems(Layer(Path([(0, 0), (0, 700), (500, 700)], closed=False))) == [
        "path 1 is open"
    ]
    assert problems(Layer(Path([(-0.0, 0), (-0.0, 0), (500, 700), (500, 0)]))) == [
        "path 1 repeats the point (0, 0)"
    ]
    assert problems(Layer(Path([(0, 0), (500, 700)]))) == [
        "path 1 has only 2 on-curve points"
    ]
    assert problems(Layer(Path([(1, 1), (1, 3), (3, 3)]))) == ["path 1 is tiny (2 x 2)"]


GUARDED = [
    "round_coordinates",
    "contour_direction",
    "anchors_from_bounds",
    "sidebearings_from_reference",
    "kerning_from_text",
    "glyph_actions_batch",
    "glyphs_tabular_figures",
]


@pytest.mark.parametrize("name", GUARDED)
def test_menu_entry_when_constants_empty_then_prints_usage_and_touches_nothing(name):
    code = (
        "import runpy, sys\n"
        f"runpy.run_path({str(RECIPES / name / 'recipe.py')!r}, run_name='__main__')\n"
        f"loaded = sorted(set(sys.modules) & set({sorted(NATIVE)!r}))\n"
        "assert not loaded, loaded\n"
    )
    done = subprocess.run(
        [sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stderr
    assert "first" in done.stdout, done.stdout



def test_contour_direction_when_curved_then_nesting_uses_the_curve_not_its_handles():
    recipe = load("contour_direction")
    # A hump whose curve peaks at y=750 while its handles reach y=1000.
    hump_points = [(0, 0), (0, 1000), (1000, 1000), (1000, 0)]
    hump = recipe.flatten(hump_points, [True, False, False, True])
    assert max(y for _, y in hump) == pytest.approx(750, abs=1)
    curve = recipe.segments(hump_points, [True, False, False, True])
    island = [(450, 800), (550, 800), (550, 900), (450, 900)]  # inside the handles only
    shapes = [curve, recipe.segments(island, [True] * 4)]
    assert recipe.wants_counter_clockwise(shapes, 1) is True, "outside the curve: an outer contour"
    inner = recipe.segments([(450, 300), (550, 300), (550, 400), (450, 400)], [True] * 4)
    assert recipe.wants_counter_clockwise([curve, inner], 1) is False, "inside the curve: a counter"


@pytest.mark.parametrize(
    ("corner", "inside"),
    [
        ((4, 90), True),  # reviewer's case: between the curve and any 16-step chord
        ((1, 20), True),
        ((0.5, -1), False),  # below the base line
        ((10, 760), False),  # above the curve's peak
        ((995, 90), True),
    ],
)
def test_contour_direction_when_point_hugs_the_curve_then_containment_is_exact(corner, inside):
    recipe = load("contour_direction")
    curve = recipe.segments([(0, 0), (0, 1000), (1000, 1000), (1000, 0)], [True, False, False, True])
    x, y = corner
    box = recipe.segments([(x, y), (x + 1, y), (x + 1, y + 1), (x, y + 1)], [True] * 4)
    assert recipe.contains(curve, (x, y)) is inside
    assert recipe.wants_counter_clockwise([curve, box], 1) is (not inside)


def test_contour_direction_contains_when_quadratic_circle_then_exact():
    recipe = load("contour_direction")
    # TrueType all-off-curve square of handles: the curve stays inside the handles.
    circle = recipe.segments([(0, 50), (50, 100), (100, 50), (50, 0)], [False] * 4)
    assert recipe.contains(circle, (50, 50)) is True
    assert recipe.contains(circle, (2, 50)) is False  # inside handles, outside the curve


def test_contour_direction_flatten_when_quadratic_runs_then_implied_on_curve_points():
    recipe = load("contour_direction")
    square = recipe.flatten([(0, 0), (0, 100), (100, 100), (100, 0)], [True, False, False, False])
    assert max(x for x, _ in square) <= 100 and len(square) > 4


class CurveNode:
    def __init__(self, x, y, type):
        self.x, self.y, self.type = x, y, type


def test_tabular_figures_when_handles_overshoot_then_real_curve_bounds_are_used():
    script = load("glyphs_tabular_figures", "tabular_figures.py")
    path = Path([])
    path.nodes = [CurveNode(100, 0, "line"), CurveNode(900, 0, "offcurve"),
                  CurveNode(900, 500, "offcurve"), CurveNode(100, 500, "curve")]
    layer = Layer(path, width=600)
    left, right = script.outline_extent(layer)
    assert left == pytest.approx(100) and right == pytest.approx(700)
    assert script.centre_in_width(layer, 1000) == 100


def test_tabular_figures_when_components_then_refused_before_editing():
    script = load("glyphs_tabular_figures", "tabular_figures.py")
    layer = Layer(Path([(0, 0), (0, 10), (10, 10)]))
    layer.components = ["one.base"]
    with pytest.raises(ValueError, match="component"):
        script.centre_in_width(layer, 600)
    assert [n.x for n in layer.paths[0].nodes] == [0, 0, 10]


class Master:
    def __init__(self, id):
        self.id = id


class Glyph:
    def __init__(self, layers):
        self.layers = layers


class Font:
    def __init__(self, glyphs, masters):
        self.glyphs, self.masters = glyphs, masters


def test_tabular_figures_when_master_given_then_only_that_master_and_empty_list_is_no_work():
    script = load("glyphs_tabular_figures", "tabular_figures.py")
    regular = Layer(Path([(100, 0), (100, 700), (200, 700), (200, 0)]), width=350)
    bold = Layer(Path([(100, 0), (100, 700), (300, 700), (300, 0)]), width=400)
    font = Font({"one": Glyph({"m1": regular, "m2": bold})}, [Master("m1"), Master("m2")])
    assert script.tabular_figures(font, ["one"], 600, master_id="m2") == {"one": 100}
    assert regular.width == 350 and bold.width == 600
    assert script.tabular_figures(font, [], 600, master_id="m1") == {}
    assert regular.width == 350


def test_parse_pairs_when_nonfinite_or_out_of_range_then_reported_not_applied():
    recipe = load("kerning_from_text")
    pairs, problems = recipe.parse_pairs("A V -80\nA W nan\nB C 1e999\nD E 40000\nF G -inf\n")
    assert pairs == [("A", "V", -80.0)]
    assert problems == ["A W nan", "B C 1e999", "D E 40000", "F G -inf"]
