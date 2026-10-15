# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/36246fcbffecdeba.md
# this_file: ports/quick/pyqt-official/canvas-36246fcbffecdeba.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
