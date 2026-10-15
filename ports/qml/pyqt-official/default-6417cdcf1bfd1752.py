# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/6417cdcf1bfd1752.md
# this_file: ports/qml/pyqt-official/default-6417cdcf1bfd1752.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
