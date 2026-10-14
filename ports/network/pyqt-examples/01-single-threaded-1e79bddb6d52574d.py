# this_file: ports/network/pyqt-examples/01-single-threaded-1e79bddb6d52574d.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/11 PyQt Thread example/01_single_threaded.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from typing import Any

from fontlab_python_examples.chat import build_chat
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    return build_chat(qt, "single_threaded")


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("1e79bddb6d52574d")
