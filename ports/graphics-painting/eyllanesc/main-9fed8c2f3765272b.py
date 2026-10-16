# this_file: ports/graphics-painting/eyllanesc/main-9fed8c2f3765272b.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/charts/barchart/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt does not export QtCharts (QtChart); required native APIs: QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QValueAxis. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("9fed8c2f3765272b")
