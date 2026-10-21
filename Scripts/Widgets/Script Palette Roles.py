# this_file: Scripts/Widgets/Script Palette Roles.py
# SPDX-License-Identifier: Apache-2.0
# preserved-source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/stylesheet-876eab33b6a99e31.py
# preserved-source-sha256: 7f520972960792491bfb81a67a5a2553db1bd4f217ef896bccf4da61da76351f
# preserved-source: rescued/part3/pyqt-official-ports/ports/widgets/pyqt-official/styles-9e21c6536fda7a23.py
# preserved-source-sha256: 80d61defa2ad1137e04ee1db8bb2b5e79876d64a034d4537e4c4f879402eaf3a
# preserved-source: rescued/part2/ports/widgets/pyqt-official/stylesheet-876eab33b6a99e31.py
# preserved-source-sha256: 9ad804c861b30854e224744b49f597ece1fc2f27455db148ee18eff7408b85eb
# preserved-source: rescued/part2/ports/widgets/pyqt-official/styles-9e21c6536fda7a23.py
# preserved-source-sha256: f609aa16c374278db565ccbac19409df42928b9515f5dc62ecea00929561c679
"""What: Inspect the live FontLab theme palette for script-panel colours.
How: Read this panel's own palette on Refresh. List all twenty colour roles
for Active, Inactive and Disabled, plus six text/background contrast pairs.
A role missing by name is listed as unavailable; its contrast pairs are omitted.
Why: Role-based colours follow the host theme. Fixed hexadecimal themes do not.
Usage: Refresh after a theme change. Copy the report for diagnosis, or copy the
code below into a panel method. The code reads roles from that panel's palette.
Benefit: Choose readable script colours without changing FontLab preferences.
Contrast composites foreground alpha over opaque backgrounds. A translucent
background has no single ratio and is reported explicitly. Ratios describe
palette values; widget styles can render differently.

Setup: FontLab 9, Python 3.11, Fly and fontlabapp. Modeless, read-only panel.
Independent rewrite of the Qt Styles and Style Sheet example ideas
(Riverbank Computing, Nokia). Based on the author's own FontLab sample,
Apache-2.0. Idea only; no upstream code or assets included.
"""

import math
from typing import Any

GROUPS = ("Active", "Inactive", "Disabled")
ROLES = (
    "WindowText",
    "Button",
    "Light",
    "Midlight",
    "Dark",
    "Mid",
    "Text",
    "BrightText",
    "ButtonText",
    "Base",
    "Window",
    "Shadow",
    "Highlight",
    "HighlightedText",
    "Link",
    "LinkVisited",
    "AlternateBase",
    "ToolTipBase",
    "ToolTipText",
    "PlaceholderText",
)
PAIRS = (
    ("WindowText", "Window"),
    ("Text", "Base"),
    ("ButtonText", "Button"),
    ("HighlightedText", "Highlight"),
    ("ToolTipText", "ToolTipBase"),
    ("PlaceholderText", "Base"),
)
RGBA = tuple[int, int, int, int]


def role_value(palette_type: Any, name: str) -> Any:
    """Use numeric role 20 for PlaceholderText; return None for absent names."""
    if name == "PlaceholderText":
        return 20
    if name not in ROLES:
        raise ValueError(f"Unknown palette role {name}.")
    return getattr(palette_type, name, None)


def contrast(foreground: RGBA, background: RGBA) -> float | None:
    """Compute the sRGB luminance ratio after foreground alpha compositing."""
    for rgba in (foreground, background):
        if len(rgba) != 4 or any(type(v) is not int or not 0 <= v <= 255 for v in rgba):
            raise ValueError("Use four integer colour channels from 0 to 255.")
    if background[3] != 255:
        return None
    alpha = foreground[3] / 255
    front = tuple(
        (a * alpha + b * (1 - alpha)) / 255
        for a, b in zip(foreground[:3], background[:3], strict=True)
    )
    back = tuple(v / 255 for v in background[:3])

    def luminance(rgb: tuple[float, ...]) -> float:
        """Linearize normalized sRGB channels before weighting luminance."""
        channels = [
            v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb
        ]
        return sum(
            a * b for a, b in zip(channels, (0.2126, 0.7152, 0.0722), strict=True)
        )

    first, second = luminance(front), luminance(back)
    ratio = (max(first, second) + 0.05) / (min(first, second) + 0.05)
    if not math.isfinite(ratio):
        raise ValueError("Palette contrast could not be calculated.")
    return ratio


def palette_report(palette: Any, palette_type: Any) -> str:
    """Read available roles once; list missing names and skip affected pairs."""
    sections: list[str] = []
    for group_name in GROUPS:
        if not hasattr(palette_type, group_name):
            raise ValueError(f"The host palette does not expose group {group_name}.")
        group = getattr(palette_type, group_name)
        values: dict[str, RGBA] = {}
        lines = [group_name]
        for role in ROLES:
            value = role_value(palette_type, role)
            if value is None:
                lines.append(f"{role}: unavailable by name")
                continue
            color = palette.color(group, value)
            values[role] = (
                int(color.red()),
                int(color.green()),
                int(color.blue()),
                int(color.alpha()),
            )
            red, green, blue, alpha = values[role]
            lines.append(f"{role}: #{red:02x}{green:02x}{blue:02x} / alpha {alpha}")
        lines.append("Contrast (foreground/background):")
        for foreground, background in PAIRS:
            if foreground not in values or background not in values:
                continue
            ratio = contrast(values[foreground], values[background])
            reading = (
                f"{ratio:.2f}:1"
                if ratio is not None
                else "unavailable: translucent background"
            )
            lines.append(f"{foreground}/{background}: {reading}")
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def role_code() -> str:
    """Return compact role lookup and a concrete house-panel label usage."""
    return "\n".join(
        (
            "# Inside a FontLab panel method; self is the panel.",
            "from fly import qt",
            "PLACEHOLDER_TEXT = 20  # Some FontLab builds omit the enum name.",
            f"roles = {ROLES!r}",
            "palette = self.palette",
            "colors = {}",
            f"for group_name in {GROUPS!r}:",
            "    group = getattr(qt.QtGui.QPalette, group_name)",
            "    colors[group_name] = {}",
            "    for role_name in roles:",
            "        role = PLACEHOLDER_TEXT if role_name == 'PlaceholderText' else getattr(qt.QtGui.QPalette, role_name, None)",
            "        if role is not None:",
            "            colors[group_name][role_name] = palette.color(group, role)",
            "# Use the live foreground role on the house panel's subtitle label.",
            "if hasattr(qt.QtGui.QPalette, 'WindowText'):",
            "    self.subtitle.setForegroundRole(qt.QtGui.QPalette.WindowText)",
            "",
        )
    )


def main() -> Any:
    """Inspect this panel's palette without setting any palette or style."""
    import fly.ap.qt_properties as properties
    import fly.ap.scripting as scripting  # noqa: PLR0402 - Fly requires module imports
    from fly import qt

    g, base = qt.QtGui, scripting.names_dialog_type()

    class Dialog(base):
        """Keep a complete colour report beside reusable role-based Python code."""

        def __init__(self, parent: Any) -> None:
            """Build two selectable text surfaces and explicit Refresh and Close."""
            base.__init__(
                self, parent, "Script Palette Roles", "widgets_script_palette_roles"
            )
            self.subtitle.setText(
                "This panel's palette: all colour groups and available roles. Missing roles are listed; their contrast pairs are skipped. Refresh after theme changes."
            )
            self.report = g.QPlainTextEdit()
            self.output = g.QPlainTextEdit()
            self.report.setReadOnly(True)
            self.output.setReadOnly(True)
            self.status = g.QLabel(
                "Refresh to inspect the colours this panel receives from FontLab."
            )
            self.status.setTextFormat(qt.QtCore.Qt.PlainText)
            self.status.setWordWrap(True)
            self.preview_button, self.close_button = (
                g.QPushButton("Refresh"),
                g.QPushButton("Close"),
            )
            for label, control in (
                ("Live colours and contrast", self.report),
                ("Role-based code for a panel method", self.output),
            ):
                self.root.addWidget(g.QLabel(label))
                self.root.addWidget(control)
            for control in (self.preview_button, self.status, self.close_button):
                self.root.addWidget(control)
            self._connect(self.preview_button.clicked, lambda *args: self.preview())
            self._connect(self.close_button.clicked, lambda *args: self.close())
            self.resize(720, 680)

        def preview(self) -> None:
            """Publish available roles and code; clear both outputs after a failed read."""
            self.output.setPlainText("")
            self.report.setPlainText("")
            try:
                palette = properties.value(self, "palette")
                report = palette_report(palette, g.QPalette)
                code = role_code()
                self.report.setPlainText(report)
                self.output.setPlainText(code)
                if (
                    str(self.report.toPlainText()) != report
                    or str(self.output.toPlainText()) != code
                ):
                    raise ValueError("Qt changed palette output text; Copy refused.")
                self.status.setText(
                    "Palette report and role-based code ready. Select text and Copy."
                )
            except (ValueError, RuntimeError, TimeoutError) as error:
                self.output.setPlainText("")
                self.report.setPlainText("")
                self.status.setText(str(error))

    return scripting.show_script_dialog(Dialog, "widgets_script_palette_roles")


if __name__ == "__main__":
    main()
