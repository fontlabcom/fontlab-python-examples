# this_file: examples/pythonqt/canvas_overlay_with_menu.py
# SPDX-License-Identifier: Apache-2.0
"""What: Draw the current glyph's name over the editor canvas and toggle it from
a menu item that has a keyboard shortcut.
Shows: flCanvas.appendPythonPainter / removePythonPainter, QPainter text
drawing in viewport coordinates, a QAction added to a FontLab menu with
fontlabapp.owned_menus.OwnedMenus, and a QKeySequence shortcut.
Run: open a font and a glyph window, then run this script. Tools > "Toggle
Glyph Name Overlay" (Ctrl+Alt+Shift+O) appears; use it to switch the overlay on
and off. "Remove Overlay Menu Items" undoes everything; running the script again
replaces the items instead of adding duplicates.
Setup: FontLab 9 builds whose flCanvas has appendPythonPainter; otherwise the
script says so and does nothing. Python 3.11, Fly with App (OwnedMenus).
Nothing is written to any font.

Rules this example follows: the painter belongs to FontLab, so it is never
ended here; the callback never raises; the native painter token is kept so the
exact painter can be removed; menu callbacks never delete their own action
(OwnedMenus defers that).
"""

from __future__ import annotations

import sys
from typing import Any

SHORTCUT = "Ctrl+Alt+Shift+O"
MENU = "Tools"
ACTION_TEXT = "Toggle Glyph Name Overlay"
# FontLab runs a script file as a fresh module every time, so module globals do not
# survive a second run. Keep the state in sys (as App's show_script_dialog does) so a
# later run can find, remove and replace what an earlier run installed.
_STATE: dict[str, Any] = sys.__dict__.setdefault(
    "_fontlab_pythonqt_overlay_example", {"menus": None, "canvas": None, "token": None}
)


def label(glyph_name: str | None) -> str:
    """The text to draw; pure Python."""
    return f"Glyph: {glyph_name}" if glyph_name else "No glyph"


def _paint(painter: Any, canvas: Any) -> None:
    """Native paint callback. Exceptions here can crash the host, so swallow them."""
    try:
        from fly import fl, qt

        glyph = fl.CurrentGlyph()
        name = None if glyph is None else str(getattr(glyph, "name", ""))
        painter.setPen(qt.QtGui.QColor("#d02020"))
        painter.drawText(qt.QtCore.QPointF(16.0, 24.0), label(name))
    except Exception:  # noqa: BLE001, S110 - never unwind through native painting
        pass


def overlay_off() -> None:
    canvas, token = _STATE["canvas"], _STATE["token"]
    _STATE["canvas"] = _STATE["token"] = None
    if canvas is not None and token is not None and not canvas.isNull:
        canvas.removePythonPainter(token)  # Pass the token appendPythonPainter returned.
        canvas.update()


def toggle() -> None:
    from fly import fl

    if _STATE["token"] is not None:
        overlay_off()
        return
    canvas = fl.flWorkspace.instance().getActiveCanvas()
    if canvas is None or canvas.isNull:
        raise RuntimeError("Open a glyph window first.")
    # OverOwner draws above the glyph; UnderOwner would draw beneath it.
    _STATE["token"] = canvas.appendPythonPainter(_paint, canvas.OverOwner)
    _STATE["canvas"] = canvas
    canvas.update()


def install() -> Any:
    from fly import fl, qt
    from fontlabapp.owned_menus import OwnedMenus

    if not hasattr(fl.flCanvas, "appendPythonPainter"):
        raise RuntimeError("This FontLab build has no flCanvas.appendPythonPainter.")
    uninstall()

    def report(error: Exception, owner: object) -> None:
        print(f"Overlay example: {error}")  # Goes to the Output panel.

    menus = OwnedMenus(qt, fl, error_sink=report)
    token = menus.add_action(MENU, ACTION_TEXT, toggle)
    menus.action(token).setShortcut(qt.QtGui.QKeySequence(SHORTCUT))
    menus.add_action(MENU, "Remove Overlay Menu Items", uninstall)  # OwnedMenus defers self-removal.
    _STATE["menus"] = menus
    return menus


def uninstall() -> None:
    overlay_off()
    menus, _STATE["menus"] = _STATE["menus"], None
    if menus is not None:
        menus.close()


def main() -> Any:
    return install()


if __name__ == "__main__":
    main()
