# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/eb7a89f07f63cca7.md
# this_file: ports/qml/pyqt-official/binding-eb7a89f07f63cca7.py
"""Explicit current-host capability boundary; import and build have no effects."""


def build(qt):
    raise NotImplementedError(
        "FontLab does not expose QtQml; this declarative example cannot start."
    )
