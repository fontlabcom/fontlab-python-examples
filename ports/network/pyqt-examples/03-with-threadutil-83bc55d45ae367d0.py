# this_file: ports/network/pyqt-examples/03-with-threadutil-83bc55d45ae367d0.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/11 PyQt Thread example/03_with_threadutil.py.
# See ports/pyqt-examples-LICENSE.md and catalog/ports.json for provenance.
from typing import Any

from fontlab_python_examples.chat import build_chat
from fontlab_python_examples.handle import ExampleHandle


def build(qt: Any) -> ExampleHandle:
    return build_chat(qt, "with_threadutil")


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("83bc55d45ae367d0")
