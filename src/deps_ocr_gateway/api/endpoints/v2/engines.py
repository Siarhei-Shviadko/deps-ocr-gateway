from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_ocr_gateway.api import auth
from deps_ocr_gateway.api.constants import (
    FREE_OCR_ENGINES,
    OCR_ENGINE_NAMES,
    OCREngineEnum,
)
from deps_ocr_gateway.api.serializers import OCREngine
from deps_ocr_gateway.containers import Containers

__all__ = ["engines_router"]

engines_router = APIRouter(prefix="/v2", tags=["Version 2"])


@engines_router.get("/engines", response_model=List[OCREngine])
@inject
def get_available_engines(
    engines: List[OCREngineEnum] = Depends(Provide[Containers.config.engines_settings.enabled_engines]),
    restriction_enabled: bool = Depends(
        Provide[Containers.config.paid_engines_restriction_enabled],
    ),
    privileged_group: bool = Depends(Provide[Containers.config.privileged_group]),
):
    current_user_organisation = auth.get_current_user_organisation()
    if restriction_enabled and current_user_organisation != privileged_group:
        engines = [e for e in engines if e in FREE_OCR_ENGINES]

    return [OCREngine(code=engine, name=OCR_ENGINE_NAMES[engine]) for engine in engines]
