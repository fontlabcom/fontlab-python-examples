# this_file: ports/video-overlay/eyllanesc/main-e9392311a500d3dd.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: others/qmlvideoviewer/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt does not export QtQml / QtMultimedia; required native APIs: QAbstractVideoBuffer, QAbstractVideoFilter, QAbstractVideoSurface, QQmlApplicationEngine, QVideoFilterRunnable, QVideoFrame, QVideoSurfaceFormat, qmlRegisterType. The pinned behavior requires these capabilities; no alternate Qt binding or replacement UI is supplied."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("e9392311a500d3dd")
