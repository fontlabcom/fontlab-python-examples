# this_file: ports/embedded/eyllanesc/main-631cc1bc310c00b9.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/embedded/styleexample/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-


from pathlib import Path
from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import Demo, read


def build(qt: Any) -> ExampleHandle:
    demo = Demo(qt, __file__, "631cc1bc310c00b9")
    try:
        window = demo.load_ui("stylewidget.ui")
        state = {"style": "nostyle"}

        def apply_style(name: str) -> None:
            sheet = Path(demo.asset("files/" + name + ".qss")).read_text(
                encoding="utf-8"
            )
            # Rewrite only the in-memory stylesheet; assets stay byte-identical.
            sheet = sheet.replace(":/files/", str(demo.assets / "files") + "/")
            window.setStyleSheet(sheet)
            state["style"] = name

        for control, name in (
            ("blueStyle", "blue"),
            ("khakiStyle", "khaki"),
            ("transparentStyle", "transparent"),
            ("noStyle", "nostyle"),
        ):
            demo.connect(
                demo.controls[control], "clicked()", lambda name=name: apply_style(name)
            )
        demo.connect(demo.controls["close"], "clicked()", window.close)
        return demo.finish(
            window,
            lambda: {
                **state,
                "value": int(read(demo.controls["spinBox"], "value")),
                "stylesheet": str(read(window, "styleSheet")),
            },
        )
    except BaseException:
        demo.abort()
        raise


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("631cc1bc310c00b9")
