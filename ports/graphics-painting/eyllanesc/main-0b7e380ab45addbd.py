# this_file: ports/graphics-painting/eyllanesc/main-0b7e380ab45addbd.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/qpa/qrasterwindow/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt.QtGui.QMatrix4x4 exposes neither __mul__ nor a matrix-product method. PaintedWindow.paintEvent requires projection * view * model; wrapper arithmetic is forbidden in FontLab. QRasterWindow exists, but numeric matrix replacement is not implemented."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("0b7e380ab45addbd")
