# this_file: tools/source_analysis.py
"""Read source structure without importing or executing third-party code."""

import ast
import io
import re
import tokenize
from pathlib import PurePosixPath

BINDINGS = {"PyQt4", "PyQt5", "PyQt6", "PySide", "PySide2", "PySide6", "Qt"}
TEXT_SUFFIXES = {
    ".py",
    ".qml",
    ".ui",
    ".qrc",
    ".md",
    ".txt",
    ".js",
    ".css",
    ".html",
    ".xml",
    ".pro",
    ".json",
    ".svg",
    ".ini",
    ".qss",
}


def source_text(path: str, data: bytes) -> str:
    """Honor Python encoding cookies; binary resources are not decoded."""
    if path.endswith(".py"):
        try:
            encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
            return data.decode(encoding)
        except (SyntaxError, UnicodeError, LookupError):
            return data.decode("utf-8", errors="replace")
    if PurePosixPath(path).suffix.lower() in TEXT_SUFFIXES or PurePosixPath(
        path
    ).name in {"LICENSE", "COPYING", "NOTICE"}:
        return data.decode("utf-8", errors="replace")
    return ""


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def python_analysis(text: str, path: str) -> dict:
    result = {
        "parse": {"state": "parsed"},
        "imports": [],
        "local_import_names": [],
        "qt_bindings": [],
        "api_calls": [],
        "qt_symbols": [],
        "entrypoint_evidence": [],
        "role": "ambiguous",
    }
    try:
        tree = ast.parse(text, filename=path)
    except (SyntaxError, ValueError) as error:
        result["parse"] = {
            "state": "syntax-error",
            "line": getattr(error, "lineno", None),
            "reason": getattr(error, "msg", "invalid source"),
        }
        result["qt_bindings"] = sorted(
            set(re.findall(r"\b(?:from|import)\s+(PyQt[456]|PySide[26]?|Qt)\b", text))
        )
        return result
    aliases, imports, calls, symbols = {}, set(), set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
                aliases[alias.asname or alias.name.split(".")[0]] = (
                    alias.name if alias.asname else alias.name.split(".")[0]
                )
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            imports.add(module)
            for alias in node.names:
                if alias.name != "*":
                    result["local_import_names"].append(f"{module}.{alias.name}")
                aliases[alias.asname or alias.name] = f"{module}.{alias.name}"
                if module.split(".")[0] in BINDINGS:
                    symbols.add(f"{module}.{alias.name}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = dotted(node.func)
            first, _, rest = name.partition(".")
            calls.add(aliases.get(first, first) + ("." + rest if rest else ""))
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
            comparison = node.test
            if (
                dotted(comparison.left) == "__name__"
                and len(comparison.ops) == 1
                and isinstance(comparison.ops[0], ast.Eq)
                and any(
                    isinstance(c, ast.Constant) and c.value == "__main__"
                    for c in comparison.comparators
                )
            ):
                result["entrypoint_evidence"].append(
                    {"kind": "main-guard", "line": node.lineno}
                )
    # Only calls outside function/class definitions establish module execution.
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for node in ast.walk(statement):
            if not isinstance(node, ast.Call):
                continue
            name = dotted(node.func)
            if name.split(".")[-1] in {
                "QApplication",
                "QGuiApplication",
                "QCoreApplication",
                "exec",
                "exec_",
                "show",
            }:
                result["entrypoint_evidence"].append(
                    {"kind": "module-launch-call", "name": name, "line": node.lineno}
                )
    result.update(
        imports=sorted(imports),
        api_calls=sorted(calls),
        qt_symbols=sorted(symbols),
        qt_bindings=sorted({i.split(".")[0] for i in imports} & BINDINGS),
    )
    result["local_import_names"] = sorted(set(result["local_import_names"]))
    filename = PurePosixPath(path).name
    if result["entrypoint_evidence"]:
        result["role"] = "entrypoint"
    elif (
        filename == "__init__.py"
        or filename.startswith("ui_")
        or filename.endswith(("_rc.py", "_ui.py"))
    ):
        result["role"] = "auxiliary"
    return result
