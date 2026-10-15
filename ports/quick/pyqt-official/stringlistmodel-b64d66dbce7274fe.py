# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b64d66dbce7274fe.md
# this_file: ports/quick/pyqt-official/stringlistmodel-b64d66dbce7274fe.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
