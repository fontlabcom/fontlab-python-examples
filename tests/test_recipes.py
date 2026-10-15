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
