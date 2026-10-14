# this_file: ports/network/pyqt-examples/02-multithreaded-88fa78cafb505cfa.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/11 PyQt Thread example/02_multithreaded.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from typing import Any

from fontlab_python_examples.chat import build_chat
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    return build_chat(qt, "multithreaded")


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("88fa78cafb505cfa")
