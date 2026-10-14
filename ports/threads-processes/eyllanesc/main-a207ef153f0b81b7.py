# this_file: ports/threads-processes/eyllanesc/main-a207ef153f0b81b7.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "The original launcher spawns sys.executable with a PyQt5/PySide2 binding and launches quickcontrols2/gallery, which requires absent QtQml/QtQuick/QtQuickControls2. PythonQt also has no Python Signal/Slot declaration API. Replacing it with the in-host examples launcher changes its subprocess/binding-selection behavior; it is blocked."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("a207ef153f0b81b7")
