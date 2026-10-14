# this_file: ports/graphics-painting/eyllanesc/main-3525151ac8d550f5.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/gui/rasterwindow/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt.QtGui.QGradient lacks the NightFade preset and its preset constructor overload, required by RasterWindow.renderNow for its exact background. QWindow/QBackingStore exist, but a replacement gradient is not supplied."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("3525151ac8d550f5")
