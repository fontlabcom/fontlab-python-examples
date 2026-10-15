# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/b88e7eb0fcb53264.md
# this_file: ports/quick/pyqt-official/chapter5-listproperties-b88e7eb0fcb53264.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
