# this_file: ports/insights/owned-repl.py
# SPDX-License-Identifier: Apache-2.0
# Original code; inspiration only (source grant unresolved; no code copied):
# _reference/Belsepubi_naali/bin/pymodules/usr/command.py:1510
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.insights import owned


def build(qt: Any) -> ExampleHandle:
    gui = qt.QtGui
    with owned(gui.QWidget(), "Owned sample-data console") as handle:
        window = handle.widget
        entry = gui.QLineEdit(window)
        entry.setText("advance")
        run = gui.QPushButton("Run short expression / statement", window)
        reset = gui.QPushButton("Reset owned namespace", window)
        output = gui.QPlainTextEdit(window)
        output.setReadOnly(True)
        output.setMaximumBlockCount(200)
        layout = gui.QVBoxLayout(window)
        for control in (entry, run, reset, output):
            layout.addWidget(control)
        namespace, state = {}, {"executions": 0, "error": ""}

        def print_owned(*values: Any, sep: str = " ", end: str = "\n") -> None:
            output.appendPlainText(sep.join(map(str, values)) + end.rstrip("\n"))

        def reset_namespace() -> None:
            namespace.clear()
            namespace.update(
                advance=600,
                glyph_names=["A", "H", "O"],
                __builtins__={
                    "len": len,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "round": round,
                    "str": str,
                    "int": int,
                    "float": float,
                    "sorted": sorted,
                    "print": print_owned,
                },
            )
            state.update(executions=0, error="")
            output.clear()

        def execute() -> None:
            source = str(entry.text)
            output.appendPlainText(">>> " + source)
            try:
                try:
                    compiled = compile(source, "<owned-console>", "eval")
                except SyntaxError:
                    exec(compile(source, "<owned-console>", "exec"), namespace)  # noqa: S102 — explicit owned console input
                else:
                    result = eval(compiled, namespace)
                    if result is not None:
                        output.appendPlainText(repr(result))
            except Exception as error:  # noqa: BLE001 — display arbitrary console input errors locally
                state["error"] = f"{type(error).__name__}: {error}"
                output.appendPlainText(state["error"])
            else:
                state["error"] = ""
            state["executions"] += 1

        reset_namespace()
        handle.connect_old(run, "clicked()", execute)
        handle.connect(entry.returnPressed, execute)
        handle.connect_old(reset, "clicked()", reset_namespace)
        handle.release.append(namespace.clear)
        handle.controls.update(input=entry, run=run, reset=reset, output=output)
        handle.inspect_ui = lambda: {
            **state,
            "namespace_keys": sorted(k for k in namespace if k != "__builtins__"),
            "output": str(output.toPlainText()),
            "scope": "owned globals; no host imports",
        }
        return handle


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("owned-repl")
