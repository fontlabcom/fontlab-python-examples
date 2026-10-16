# this_file: ports/corelib/eyllanesc/main-24b0b2aa8998d701.py
# SPDX-License-Identifier: GPL-3.0-only
# Adapted from eyllanesc (upstream account; no copyright year inferred), eyllanesc/QtExamples: official/corelib/ipc/sharedmemory/main.py.
# Modified for FontLab PythonQt; see ports/eyllanesc-LICENSE.md and catalog/ports.json.

# -*- coding: utf-8 -*-

from typing import Any

from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    """Reject before touching the injected host or creating native objects."""
    raise NotImplementedError(
        "PythonQt.QtCore.QSharedMemory lacks detach(). The associated Dialog requires native shared-memory image exchange and explicit detach; the generated UI entrypoint launches that same Dialog. An owned segment cannot be implemented and safely released."
    )


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("24b0b2aa8998d701")
