# this_file: lessons/src/fontlab_python_lessons/getgo/font_info_ui.py
# SPDX-License-Identifier: Apache-2.0
# MenuTitle: GetGo - Font Info Mini Tool

"""GG Stroke Chan OFL Italic (OFL-1.1): show a detached font-info snapshot.
Source font: https://code.fontlab.com/getgo-fonts/stroke-chan/
Original example code: Apache-2.0. PythonQt.QtGui uses FontLab's existing event loop.
"""

from typing import Any

from fontlab_python_lessons.getgo._shared import owned_font

TOOL = None  # Retained by the canonical module, even if Scripting panel globals vanish.


def info_text(report: dict) -> str:
    """Plain text avoids treating embedded metadata as Qt rich text."""
    return (
        f"{report['family']}\n{report['glyphs']} glyphs | {report['upm']} units/em\n"
        f"Masters: {', '.join(report['masters'])}"
    )


class InfoTool:
    """Retain an owned widget; close/delete it explicitly after native inspection."""

    def __init__(self: Any, widget: Any, report: dict) -> None:
        self.widget, self.report = widget, report

    def close(self: Any) -> None:
        """Idempotent cleanup; there are no connected Python signal receivers."""
        if self.widget is not None:
            widget = self.widget
            if not getattr(widget, "_released", False):
                if widget.close() is False:
                    raise RuntimeError("The report window refused to close")
                if not hasattr(widget, "_release"):
                    widget.deleteLater()
            self.widget = None


def run() -> InfoTool:
    """Close the font before showing a window; caller retains and closes the tool."""
    from fly.ap.reports import show_report

    with owned_font("stroke-chan") as (package, record):
        report = {
            "family": package.info.familyName,
            "glyphs": package.glyphsCount,
            "upm": package.info.unitsPerEm,
            "masters": list(package.masters),
            "source": record["page_url"],
        }
    widget = show_report(report, title="GetGo font information", key="getgo-font_info_ui")
    return InfoTool(widget, report)


def show() -> InfoTool:
    """Retain the menu-launched tool in the importable module; close its predecessor."""
    global TOOL
    if TOOL is not None:
        TOOL.close()
    TOOL = run()
    return TOOL


if __name__ == "__main__":
    from fontlab_python_lessons.getgo import font_info_ui

    font_info_ui.show()
