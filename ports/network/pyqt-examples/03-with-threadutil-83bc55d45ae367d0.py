# this_file: ports/network/pyqt-examples/03-with-threadutil-83bc55d45ae367d0.py
# SPDX-License-Identifier: MIT
# Adapted from Michael Herrmann, pyqt/examples: src/11 PyQt Thread example/03_with_threadutil.py.
# Modified for FontLab PythonQt; see ports/pyqt-examples-LICENSE.md and catalog/ports.json.


from typing import Any

from fontlab_python_examples.handle import ExampleHandle
from fontlab_python_examples.official import build_chat


def build(qt: Any) -> ExampleHandle:
    return build_chat(qt, __file__, "83bc55d45ae367d0", "with_threadutil")


if __name__ == "__main__":
    from fontlab_python_examples import launch

    launch("83bc55d45ae367d0")
