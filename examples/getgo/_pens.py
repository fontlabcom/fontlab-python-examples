# SPDX-License-Identifier: Apache-2.0
# this_file: examples/getgo/_pens.py
"""Adapt FontLab's QPointF segment operands to the FontTools pen protocol."""


def tuple_point(point) -> tuple | None:
    """Detach QPointF coordinates; preserve tuples and qCurveTo's None sentinel."""
    if point is None or isinstance(point, tuple):
        return point
    return point.x(), point.y()


class TuplePen:
    """Forward segment operations with ordinary, host-free coordinate tuples."""

    def __init__(self, pen):
        self.pen = pen

    def moveTo(self, point) -> None:
        self.pen.moveTo(tuple_point(point))

    def lineTo(self, point) -> None:
        self.pen.lineTo(tuple_point(point))

    def curveTo(self, *points) -> None:
        self.pen.curveTo(*(tuple_point(point) for point in points))

    def qCurveTo(self, *points) -> None:
        self.pen.qCurveTo(*(tuple_point(point) for point in points))

    def closePath(self) -> None:
        self.pen.closePath()

    def endPath(self) -> None:
        self.pen.endPath()

    def addComponent(self, name: str, transformation: tuple) -> None:
        self.pen.addComponent(name, transformation)
