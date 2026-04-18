from dataclasses import asdict
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from deps_ocr_engines.constants import DEFAULT_ENGINE
from deps_ocr_engines.domain.entities_v2 import TextLineEntity

from .extract_text import TextLineModel

__all__ = ["ExtractImagePageRequest", "ExtractImagePageResponse"]


class ExtractImagePageRequest(BaseModel):
    blob_name: str = Field(alias="blobName")
    language: str = DEFAULT_ENGINE


class ExtractImagePageResponse(BaseModel):
    text_lines: List[TextLineModel] = Field(alias="textLines")

    @classmethod
    def from_textlines(cls, text_lines: List[TextLineEntity]) -> "ExtractImagePageResponse":
        return cls(text_lines=[asdict(tl) for tl in text_lines])

    model_config = ConfigDict(populate_by_name=True)
