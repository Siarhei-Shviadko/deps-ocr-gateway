from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_ocr_engines.api.constants import OCR_ENGINE_NAMES
from deps_ocr_engines.api.v2.serializers.engines import OCREngineModel
from deps_ocr_engines.containers import Containers
from deps_ocr_engines.domain.constants import OCREngineEnum

router = APIRouter()


@router.get("/engines", response_model=OCREngineModel)
@inject
def get_engine(engine: OCREngineEnum = Depends(Provide[Containers.config.engine.ocr_engine])):
    return OCREngineModel(code=engine, name=OCR_ENGINE_NAMES[engine])
