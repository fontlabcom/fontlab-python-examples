# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/8d1557cbfed9c7a0.md
# this_file: ports/quick/pyqt-official/chapter2-methods-8d1557cbfed9c7a0.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
