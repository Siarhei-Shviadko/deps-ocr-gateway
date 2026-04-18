from pydantic import BaseModel, ConfigDict

from deps_ocr_engines.domain.constants import OCREngineEnum


class OCREngineModel(BaseModel):
    code: OCREngineEnum
    name: str

    model_config = ConfigDict(from_attributes=True)
