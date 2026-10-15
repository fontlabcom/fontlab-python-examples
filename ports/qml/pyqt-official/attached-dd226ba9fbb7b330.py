# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/dd226ba9fbb7b330.md
# this_file: ports/qml/pyqt-official/attached-dd226ba9fbb7b330.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
