# this_file: tests/test_owned_file_regressions.py
"""Native file-boundary regressions using the exported PythonQt doubles."""

import ast
from pathlib import Path

from fontlab_python_examples.official import Demo
from tests.port_state import require_current
from tests.test_official_batch import official_qt as official_qt  # noqa: PLC0414


def owner(h):
    return next(
        f.__self__ for f in h.release if isinstance(getattr(f, "__self__", None), Demo)
    )


def test_all_ports_convert_settings_list_defaults_before_use():
    from tests.test_official_batch import records

    require_current(next(r for r in records() if r["name"] == "Official recentfiles"))
    root = Path(__file__).resolve().parents[1]
    for path in (root / "ports").rglob("*.py"):
        tree = ast.parse(path.read_text())
        parents = {
            child: node
            for node in ast.walk(tree)
            for child in ast.iter_child_nodes(node)
        }
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "value"
                and len(node.args) == 2
                and isinstance(node.args[1], ast.List)
            ):
                continue
            parent = parents[node]
            assert (
                isinstance(parent, ast.Call)
                and isinstance(parent.func, ast.Name)
                and parent.func.id == "list"
            ), f"Normalize PythonQt tuple/list settings at {path.name}:{node.lineno}"


def test_all_port_open_and_load_methods_avoid_write_ownership_checks():
    root = Path(__file__).resolve().parents[1]
    paths = list((root / "ports").rglob("*.py"))
    paths.append(root / "fontlab_python_examples" / "editor.py")
    for path in paths:
        for function in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(
                function, ast.FunctionDef
            ) or not function.name.startswith(("open", "load")):
                continue
            assert not any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "owned_path"
                for node in ast.walk(function)
            ), f"Read method must not enforce write ownership: {path}:{function.lineno}"
