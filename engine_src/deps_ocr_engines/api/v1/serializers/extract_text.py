from typing import List

from pydantic import BaseModel, Field

__all__ = ["TextLineSchema"]


class PointSchema(BaseModel):
    x: int
    y: int


class RectangleSchema(BaseModel):
    left_top_point: PointSchema
    right_bottom_point: PointSchema


class WordBoxSchema(BaseModel):
    content: str
    bbox: RectangleSchema
    confidence: float = Field(1.0, ge=0, le=1.0)


class TextLineSchema(BaseModel):
    id: int
    word_boxes: List[WordBoxSchema]
