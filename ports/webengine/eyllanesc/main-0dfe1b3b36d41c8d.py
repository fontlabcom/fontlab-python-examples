# this_file: ports/webengine/eyllanesc/main-0dfe1b3b36d41c8d.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/webenginewidgets/cookiebrowser/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt does not export QtWebEngineCore / QtWebEngineWidgets; required native APIs: QWebEngineCookieStore, QWebEngineView. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("0dfe1b3b36d41c8d")
