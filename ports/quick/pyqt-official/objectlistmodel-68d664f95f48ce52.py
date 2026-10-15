# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/68d664f95f48ce52.md
# this_file: ports/quick/pyqt-official/objectlistmodel-68d664f95f48ce52.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
