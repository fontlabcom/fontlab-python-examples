# MenuTitle: GetGo - Font Info Mini Tool
# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/font_info_ui.py
"""GG Stroke Chan OFL Italic (OFL-1.1): show a detached font-info snapshot.
Source font: https://code.fontlab.com/getgo-fonts/stroke-chan/
Original example code: Apache-2.0. PythonQt.QtGui uses FontLab's existing event loop.
"""

from examples.getgo._shared import owned_font

TOOL = None  # Retained by the canonical module, even if Scripting panel globals vanish.


def info_text(report: dict) -> str:
    """Plain text avoids treating embedded metadata as Qt rich text."""
    return (
        f"{report['family']}\n{report['glyphs']} glyphs | {report['upm']} units/em\n"
        f"Masters: {', '.join(report['masters'])}"
    )


class InfoTool:
    """Retain an owned widget; close/delete it explicitly after native inspection."""

    def __init__(self, widget, report: dict):
        self.widget, self.report = widget, report

    def close(self) -> None:
        """Idempotent cleanup; there are no connected Python signal receivers."""
        if self.widget is not None:
            self.widget.close()
            self.widget.deleteLater()
            self.widget = None


def run() -> InfoTool:
    """Close the font before showing a window; caller retains and closes the tool."""
    from PythonQt import QtGui
    from PythonQt.QtCore import Qt

    with owned_font("stroke-chan") as (package, record):
        report = {
            "family": package.info.familyName,
            "glyphs": package.glyphsCount,
            "upm": package.info.unitsPerEm,
            "masters": list(package.masters),
            "source": record["page_url"],
        }
    widget = QtGui.QDialog()
    try:
        widget.setWindowTitle("GetGo font information")
        layout = QtGui.QVBoxLayout(widget)
        label = QtGui.QLabel(info_text(report), widget)
        label.setTextFormat(Qt.PlainText)
        layout.addWidget(label)
        widget.show()
        return InfoTool(widget, report)
    except BaseException:
        widget.close()
        widget.deleteLater()
        raise


def show() -> InfoTool:
    """Retain the menu-launched tool in the importable module; close its predecessor."""
    global TOOL
    if TOOL is not None:
        TOOL.close()
    TOOL = run()
    return TOOL


if __name__ == "__main__":
    from examples.getgo import font_info_ui

    font_info_ui.show()
