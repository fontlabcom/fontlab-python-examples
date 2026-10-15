# SPDX-License-Identifier: Apache-2.0
# Clean-room implementation from clean-room-specs/ed6d42d4faa7e0bb.md
# this_file: ports/opengl/pyqt-official/textures-ed6d42d4faa7e0bb.py
"""Explicit host capability boundary; importing this module has no effects."""


def build(qt):
    """Reject before inspecting the host or allocating any native object."""
    raise NotImplementedError(
        "QOpenGLContext.versionFunctions and version-specific GL wrappers are unavailable in FontLab."
    )
