# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/6b1f4f5590a5518a.md
# this_file: ports/quick/pyqt-official/chapter1-basics-6b1f4f5590a5518a.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
