from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    PdfImageMetaEntity,
    TextLineEntity,
    WordBoxEntity,
)

__all__ = ["ExtractTextRequestModel", "BboxModel", "WordBoxModel", "TextLineModel", "PdfImageMetaModel"]


class ExtractTextRequestModel(BaseModel):
    engine: OCREngineEnum
    language: Optional[str] = None


class BboxModel(BaseModel):
    x: float = Field(..., ge=0, le=1)
    y: float = Field(..., ge=0, le=1)
    w: float = Field(..., ge=0, le=1)
    h: float = Field(..., ge=0, le=1)

    def to_domain(self) -> BboxEntity:
        return BboxEntity(**self.model_dump())


class WordBoxModel(BaseModel):
    content: str
    bbox: BboxModel
    confidence: float = Field(1.0, ge=0, le=1.0)

    def to_domain(self) -> WordBoxEntity:
        return WordBoxEntity(content=self.content, confidence=self.confidence, bbox=self.bbox.to_domain())


class TextLineModel(BaseModel):
    id: int
    word_boxes: List[WordBoxModel] = Field(..., alias="wordBoxes")

    model_config = ConfigDict(populate_by_name=True)

    def to_domain(self) -> TextLineEntity:
        return TextLineEntity(id=self.id, word_boxes=[wb.to_domain() for wb in self.word_boxes])


class PdfImageMetaModel(BaseModel):
    width: int
    height: int
    textlines_v2: Optional[List[TextLineModel]]

    def to_domain(self) -> PdfImageMetaEntity:
        return PdfImageMetaEntity(
            width=self.width,
            height=self.height,
            textlines_v2=[text_line.to_domain() for text_line in self.textlines_v2] if self.textlines_v2 else None,
        )
