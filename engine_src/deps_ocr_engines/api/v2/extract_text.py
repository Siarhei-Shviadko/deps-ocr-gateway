import io
import logging
from dataclasses import asdict
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, HTTPException
from pydantic import Json, ValidationError

from deps_ocr_engines.api.v2.serializers import (
    BboxModel,
    ExtractImagePageRequest,
    ExtractImagePageResponse,
    PdfImageMetaModel,
    TextLineModel,
    WordBoxModel,
)
from deps_ocr_engines.application import Application
from deps_ocr_engines.constants import DEFAULT_ENGINE
from deps_ocr_engines.containers import Containers
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.services import OCRService
from deps_ocr_engines.domain.utils.textlines_utils import (
    ImageSize,
    convert_textlines_area_to_image_coords,
    merge_textlines,
)
from deps_ocr_engines.extras import StorageControllerService
from deps_ocr_engines.infrastructure.textlines import extract_area_text, extract_text
from deps_ocr_engines.infrastructure.transformations import crop_image

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Version 2"])


@inject
def get_engine_config(
    engine_settings: Json = Body(str({}), embed=True, alias="engineSettings"),
    init_engine_settings: OCREngineSettings = Depends(Provide[Containers.engine_settings]),
) -> OCREngineSettings:
    try:
        return init_engine_settings()(**engine_settings)
    except NotImplementedError:
        return OCREngineSettings(**engine_settings)
    except ValidationError:
        raise HTTPException(status_code=400, detail=f"Invalid config: `{engine_settings}`")  # noqa: WPS432


@inject
def get_file_from_storage(
    file_url: str = Body(..., alias="blobFile"),
    file_storage: StorageControllerService = Depends(Provide[Containers.storage_service]),
):
    return file_storage.download_content(file_url)


@inject
def get_metadata_from_storage(
    file_url: str = Body(..., alias="blobFile"),
    force_ocr: bool = Body(default=False, alias="forceOCR"),
    file_storage: StorageControllerService = Depends(Provide[Containers.storage_service]),
):
    if force_ocr:
        return None
    metadata_dict = file_storage.load_metadata(file_url)
    return PdfImageMetaModel.model_validate(metadata_dict) if metadata_dict else None


@router.post("/extract-area", response_model=WordBoxModel)
@inject
def extract_value_from_file_storage(
    ocr_service: OCRService = Depends(Provide[Containers.ocr_service]),
    file: bytes = Depends(get_file_from_storage),
    metadata: Optional[PdfImageMetaModel] = Depends(get_metadata_from_storage),
    language: str = Body(DEFAULT_ENGINE),
    area: BboxModel = Body(
        default=BboxModel(x=0, y=0, w=1, h=1),
        description="Area of image that should be extracted if you need to crop image. Relative coordinates",
    ),
    engine_settings: OCREngineSettings = Depends(get_engine_config),
):
    cropped = crop_image(file, area)
    try:
        ocr_textlines = ocr_service.execute(
            image=cropped,
            language=language or DEFAULT_ENGINE,
            engine_config=engine_settings,
        )
    finally:
        cropped.close()

    if metadata and metadata.textlines_v2:
        meta = metadata.to_domain()

        ocr_textlines = convert_textlines_area_to_image_coords(
            textlines=ocr_textlines,
            area=area.to_domain(),
            image_size=ImageSize(width=meta.width, height=meta.height),
        )

        return asdict(
            extract_area_text(
                textlines=merge_textlines(
                    ocr_textlines,
                    meta.textlines_v2,
                    image_size=ImageSize(width=meta.width, height=meta.height),
                ),
                area=area.to_domain(),
            ),
        )

    return asdict(extract_text(ocr_textlines))


@router.post("/extract-text", response_model=List[TextLineModel])
@inject
def extract_text_from_image(
    file: bytes = File(...),
    metadata: Optional[bytes] = File(None),
    language: str = Body(DEFAULT_ENGINE),
    ocr_service: OCRService = Depends(Provide[Containers.ocr_service]),
    engine_settings: OCREngineSettings = Depends(get_engine_config),
):
    with io.BytesIO(file) as in_memory_image:
        textlines = ocr_service.execute(
            image=in_memory_image,
            language=language or DEFAULT_ENGINE,
            engine_config=engine_settings,
        )

    if metadata:
        metadata_entity = PdfImageMetaModel.model_validate_json(metadata).to_domain()

        if metadata_entity.textlines_v2:
            textlines = merge_textlines(
                textlines,
                metadata_entity.textlines_v2,
                image_size=ImageSize(width=metadata_entity.width, height=metadata_entity.height),
            )

    return list(map(asdict, textlines))


@router.post("/extract-image-page", response_model=ExtractImagePageResponse)
@inject
def extract_image_page(
    extract_image_request: ExtractImagePageRequest,
    application: Application = Depends(Provide[Containers.application]),
):
    text_lines = application.extract_image_page(
        blob_name=extract_image_request.blob_name,
        language=extract_image_request.language or DEFAULT_ENGINE,
    )
    return ExtractImagePageResponse.from_textlines(text_lines)
