# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/75ca5ac77ecefd6d.md
# this_file: ports/qml/pyqt-official/methods-75ca5ac77ecefd6d.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
