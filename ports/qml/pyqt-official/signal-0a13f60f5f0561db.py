# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/0a13f60f5f0561db.md
# this_file: ports/qml/pyqt-official/signal-0a13f60f5f0561db.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
