# this_file: ports/matplotlib/eyllanesc/plot-streamplot-19398065f86e2762.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: others/matplotlib/plot_streamplot.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-
# https://matplotlib.org/3.2.1/gallery/images_contours_and_fields/plot_streamplot.html


from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "The original imports matplotlib.backends.backend_qt5agg.FigureCanvas, which requires PyQt/PySide rather than PythonQt. This is not an Agg-only demo. FontLab matplotlib availability is unverified; installing a binding or substituting a static image for the original canvas/event behavior is not performed."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("19398065f86e2762")
