from dataclasses import dataclass
from typing import List


@dataclass
class BboxEntity:
    x: float
    y: float
    w: float
    h: float
    page: int = 1

    def __post_init__(self):
        if not (0 <= self.x <= 1 and 0 <= self.y <= 1 and 0 <= self.w <= 1 and 0 <= self.h <= 1):  # noqa: WPS221
            raise ValueError(
                "BBoxEntity relative coordinates must be greater or equal than 0 and less "
                + f"or equal than 1.0: x={self.x}, y={self.y}, w={self.w}, h={self.h}",
            )

    @property
    def top(self) -> float:
        return self.y

    @property
    def left(self) -> float:
        return self.x

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def centerx(self) -> float:
        return self.x + self.w / 2

    @property
    def centery(self) -> float:
        return self.y + self.h / 2


@dataclass
class WordBoxEntity:
    content: str
    bbox: BboxEntity
    confidence: float = 1.0

    def __post_init__(self):
        if self.confidence < 0 or self.confidence > 1:
            raise ValueError(
                "WordBoxEntity confidence value must be greater or equal than 0 and less or equal "
                + f"than 1.0: confidence={self.confidence}",
            )


@dataclass
class TextLineEntity:
    id: int
    word_boxes: List[WordBoxEntity]


@dataclass
class PointEntity:
    x: float
    y: float


@dataclass
class PdfImageMetaEntity:
    width: int
    height: int
    textlines_v2: List[TextLineEntity]
