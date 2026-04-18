import io
from dataclasses import asdict
from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, HTTPException
from pydantic import Json, ValidationError

from deps_ocr_engines.constants import DEFAULT_ENGINE
from deps_ocr_engines.containers import Containers
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.services import OCRService
from deps_ocr_engines.domain.utils.ocr_utils import (
    convert_relative_entities_to_absolute,
)

from .serializers import TextLineSchema

__all__ = ["router"]

router = APIRouter(tags=["Version 1"])


@inject
def get_engine_config(
    engine_settings: Json = Body(str({}), embed=True),
    init_engine_settings: OCREngineSettings = Depends(Provide[Containers.engine_settings]),
) -> OCREngineSettings:
    try:
        return init_engine_settings()(**engine_settings)
    except NotImplementedError:
        return OCREngineSettings(**engine_settings)
    except ValidationError:
        raise HTTPException(status_code=400, detail=f"Invalid config: `{engine_settings}`")  # noqa: WPS432


@router.post("/extract-text", response_model=List[TextLineSchema])
@inject
def extract_text_from_image(
    language: str = DEFAULT_ENGINE,
    file: bytes = File(...),
    engine_settings: OCREngineSettings = Depends(get_engine_config),
    ocr_service: OCRService = Depends(Provide[Containers.ocr_service]),
):
    with io.BytesIO(file) as in_mem_image:
        response = ocr_service.execute(
            image=in_mem_image,
            language=language or DEFAULT_ENGINE,
            engine_config=engine_settings,
        )

        return [asdict(text_line) for text_line in convert_relative_entities_to_absolute(in_mem_image, response)]
