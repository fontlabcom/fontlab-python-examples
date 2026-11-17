# this_file: src_docs/build.py
"""Build the examples catalogue and standalone documentation site."""

import argparse
import subprocess
from pathlib import Path

from src_docs.current_menus import catalogue

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline", action="store_true", help="use cached dependencies")
    parser.add_argument("--serve", action="store_true", help="preview locally with Markdown editing")
    args = parser.parse_args()
    catalogue(ROOT)
    subprocess.run(
        ["properdocs", "serve" if args.serve else "build", "--strict", "-f", "src_docs/mkdocs.yml"],
        cwd=ROOT,
        check=True,
    )


if __name__ == "__main__":
    main()
