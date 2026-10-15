# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/81a6f0d16c203608.md
# this_file: ports/qml/pyqt-official/grouped-81a6f0d16c203608.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
