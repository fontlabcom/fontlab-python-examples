# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/3cd3713a5dc9f6dc.md
# this_file: ports/quick/pyqt-official/chapter3-bindings-3cd3713a5dc9f6dc.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
