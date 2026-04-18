from pydantic import BaseModel, ConfigDict

from deps_ocr_gateway.api.constants import OCREngineEnum

__all__ = ["OCREngine"]


class OCREngine(BaseModel):
    code: OCREngineEnum
    name: str

    model_config = ConfigDict(from_attributes=True)
