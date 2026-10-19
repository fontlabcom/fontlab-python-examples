# this_file: lessons/src/fontlab_python_lessons/getgo/__init__.py
# SPDX-License-Identifier: Apache-2.0
"""Run packaged GetGo lessons and show detached reports; native acceptance pending."""

from importlib import import_module
from typing import Any

ENTRIES = {
    "font_audit": "fontlab_python_lessons.getgo.font_audit",
    "unicode_coverage": "fontlab_python_lessons.getgo.unicode_coverage",
    "outline_pens": "fontlab_python_lessons.getgo.outline_pens",
    "naming": "fontlab_python_lessons.getgo.naming",
    "kerning_classes": "fontlab_python_lessons.getgo.kerning_classes",
    "designspace": "fontlab_python_lessons.getgo.designspace",
    "master_compatibility": "fontlab_python_lessons.getgo.master_compatibility",
    "spacing": "fontlab_python_lessons.getgo.spacing",
    "batch_transform": "fontlab_python_lessons.getgo.batch_transform",
    "export_ttf": "fontlab_python_lessons.getgo.export_ttf",
    "export_otf": "fontlab_python_lessons.getgo.export_otf",
    "font_info_ui": "fontlab_python_lessons.getgo.font_info_ui",
    "compare_fonts": "fontlab_python_lessons.getgo.compare_fonts",
}
NATIVE_STATUS = "pending"


def launch(name: str, **kwargs: Any) -> Any:
    """Call one original entry with its defaults and show its detached result.

    Dictionary lessons return their owned App window, whose report is a detached
    snapshot. Call a module's run(**kwargs) directly for its original dictionary.
    font_info_ui retains its documented InfoTool/report/widget/close contract.
    """
    module = import_module(ENTRIES[name])
    if name == "font_info_ui":
        return module.show(**kwargs)
    report = module.run(**kwargs)
    from fly.ap.reports import show_report

    return show_report(
        report, title="GetGo: " + name.replace("_", " ").title(), key="getgo-" + name
    )
