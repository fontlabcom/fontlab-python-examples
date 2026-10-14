# this_file: ports/network/eyllanesc/main-eea833917398267a.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/network/googlesuggest/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt.QtCore has no QXmlStreamReader, required by GSuggestCompletion.handleNetworkData to parse suggestions. A stdlib XML parser plus owned localhost suggestion/search server is a possible behavior-preserving future adaptation; this record does not claim that substitution is implemented."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("eea833917398267a")
