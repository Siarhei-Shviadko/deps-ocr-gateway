from typing import Any, List, Optional

import numpy as np


class Point:
    def __init__(self, x: float, y: float, payload: Optional[Any] = None):
        self.x = x
        self.y = y
        self.payload = payload

    def distance_to(self, other: "Point") -> np.ndarray:
        return np.hypot(self.x - other.x, self.y - other.y)


class Rect:
    def __init__(self, cx: float, cy: float, w: float, h: float):
        self.cx = cx
        self.cy = cy
        self.w = w
        self.h = h

    @property
    def west_edge(self):
        return self.cx - self.w / 2

    @property
    def east_edge(self):
        return self.cx + self.w / 2

    @property
    def north_edge(self):
        return self.cy - self.h / 2

    @property
    def south_edge(self):
        return self.cy + self.h / 2

    def contains(self, point: Point) -> bool:
        return self.west_edge <= point.x <= self.east_edge and self.north_edge <= point.y <= self.south_edge

    def intersects(self, other: "Rect") -> bool:
        return not (
            other.west_edge > self.east_edge
            or other.east_edge < self.west_edge
            or other.north_edge > self.south_edge
            or other.south_edge < self.north_edge
        )

    def get_iou_with(self, other: "Rect") -> float:
        """Jaccard index or Intersection over Union.

        https://en.wikipedia.org/wiki/Jaccard_index
        """

        if not self.intersects(other):
            return 0

        xmin1, ymin1 = self.west_edge, self.north_edge
        xmax1, ymax1 = self.east_edge, self.south_edge
        xmin2, ymin2 = other.west_edge, other.north_edge
        xmax2, ymax2 = other.east_edge, other.south_edge

        x_a, y_a = max(xmin1, xmin2), max(ymin1, ymin2)
        x_b, y_b = min(xmax1, xmax2), min(ymax1, ymax2)

        s = (x_b - x_a) * (y_b - y_a)

        return s / ((xmax1 - xmin1) * (ymax1 - ymin1) + (xmax2 - xmin2) * (ymax2 - ymin2) - s)


# Based on https://scipython.com/blog/quadtrees-2-implementation-in-python/
class QuadTreeNode:  # noqa: WPS230
    def __init__(self, boundary: Rect, max_points: int = 4, depth: int = 0):
        """
        boundary: a Rect object defining the region from which points are
        placed into this node;
        max_points: the maximum number of points the
        node can hold before it must divide (branch into four more nodes);
        depth: keeps track of how deep into the quad tree this node lies.
        """

        self.boundary = boundary
        self.max_points = max_points
        self.points: List[Point] = []
        self.depth = depth
        self.divided = False

    def divide(self) -> None:
        cx, cy = self.boundary.cx, self.boundary.cy
        w, h = self.boundary.w / 2, self.boundary.h / 2

        self.nw = QuadTreeNode(Rect(cx - w / 2, cy - h / 2, w, h), self.max_points, self.depth + 1)
        self.ne = QuadTreeNode(Rect(cx + w / 2, cy - h / 2, w, h), self.max_points, self.depth + 1)
        self.se = QuadTreeNode(Rect(cx + w / 2, cy + h / 2, w, h), self.max_points, self.depth + 1)
        self.sw = QuadTreeNode(Rect(cx - w / 2, cy + h / 2, w, h), self.max_points, self.depth + 1)

        self.divided = True

    def insert_point(self, point: Point) -> bool:
        if not self.boundary.contains(point):
            return False

        if len(self.points) < self.max_points:
            self.points.append(point)
            return True

        if not self.divided:
            self.divide()

        return (
            self.ne.insert_point(point)
            or self.nw.insert_point(point)
            or self.se.insert_point(point)
            or self.sw.insert_point(point)
        )

    def find_points(self, region: Rect, found_points: List[Point]) -> None:
        if not self.boundary.intersects(region):
            return

        found_points.extend([point for point in self.points if region.contains(point)])

        if self.divided:
            self.nw.find_points(region, found_points)
            self.ne.find_points(region, found_points)
            self.se.find_points(region, found_points)
            self.sw.find_points(region, found_points)

    def __len__(self):
        points_number = len(self.points)

        if self.divided:
            points_number += len(self.nw) + len(self.ne) + len(self.se) + len(self.sw)

        return points_number
