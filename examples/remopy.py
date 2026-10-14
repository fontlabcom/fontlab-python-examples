#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fontlab-remopy"]
# ///
# this_file: examples/remopy.py
"""Launch, inspect or close a named example in an already configured FontLab."""

import argparse
from pathlib import Path


def main() -> None:
    from fontlab_remopy import FontLab

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("launch", "inspect", "close"))
    parser.add_argument("name", nargs="?", default="QLabel")
    args = parser.parse_args()
    root = str(Path(__file__).resolve().parents[1])
    code = """import sys
if examples_root not in sys.path:
    sys.path.insert(0, examples_root)
import fontlab_python_examples as examples
if action == 'launch':
    examples.launch(name)
result = examples.close(name) if action == 'close' else examples.inspect(name)
"""
    with FontLab() as fl:
        print(
            fl.run(code, examples_root=root, action=args.action, name=args.name).value
        )


if __name__ == "__main__":
    main()
