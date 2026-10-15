# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/831ac8ea61da03f3.md
# this_file: ports/quick/pyqt-official/chapter4-custompropertytypes-831ac8ea61da03f3.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQuick and QtQml; this declarative example cannot start."
    )
