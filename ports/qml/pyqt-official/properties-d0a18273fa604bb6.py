# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/d0a18273fa604bb6.md
# this_file: ports/qml/pyqt-official/properties-d0a18273fa604bb6.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
