# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/85a56a1f3c25ccca.md
# this_file: ports/qtdemo/pyqt-official/qtdemo-85a56a1f3c25ccca.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QtQuick/QtQml, external PyQt launchers and documentation remote control are unavailable in FontLab."
    )
