from dataclasses import dataclass
from typing import Any, Iterable, List, Type

from pydantic import BaseModel


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Rectangle:
    left_top_point: Point
    right_bottom_point: Point


@dataclass
class WordBox:
    content: str
    bbox: Rectangle
    confidence: float = 1.0


@dataclass
class TextLine:
    id: int
    word_boxes: List[WordBox]


@dataclass
class OCREngineInitSettings:
    engine_cls: Type[Any]
    engine_args: Iterable[Any]


class OCREngineSettings(BaseModel):
    """
    class for indicating that we're working with engine configuration
    """
