import logging
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, Request, Response, UploadFile
from pydantic import Json

from deps_ocr_gateway.api.constants import OCREngineEnum
from deps_ocr_gateway.api.serializers.extract_text import BboxModel
from deps_ocr_gateway.containers import Containers
from deps_ocr_gateway.infrastructure import OCRGateway

from ...requests import BodyParsedRequest, FormParsedRequest
from ..shared import check_permission

__all__ = ["extract_router"]

logger = logging.getLogger(__name__)

extract_router = APIRouter(prefix="/v2", tags=["Version 2"])


@extract_router.post("/extract-area")
@inject
async def extract_area(
    request: Request,
    engine: OCREngineEnum = Body(...),
    file_url: str = Body(..., alias="blobFile"),
    force_ocr: bool = Body(False, alias="forceOCR"),  # noqa: WPS425
    language: str = Body("eng"),
    area: BboxModel = Body(
        default=BboxModel(x=0, y=0, w=1, h=1),
        description="Area of image that should be extracted if you need to crop image. Relative coordinates",
    ),
    engine_settings: Json = Body(str({}), embed=True, alias="engineSettings"),
    gateway: OCRGateway = Depends(Provide[Containers.ocr_gateway]),
):
    parsed_request = BodyParsedRequest(request)
    check_permission(await parsed_request.engine)
    response = await gateway.proxy(parsed_request)

    return Response(**response)


@extract_router.post("/extract-text")
@inject
async def extract_text(
    request: Request,
    file: UploadFile = File(...),
    metadata: Optional[UploadFile] = File(None),
    engine: OCREngineEnum = Body(...),
    language: str = Body("eng"),
    engine_settings: Json = Body(str({}), embed=True, alias="engineSettings"),
    gateway: OCRGateway = Depends(Provide[Containers.ocr_gateway]),
):
    parsed_request = FormParsedRequest(request)
    check_permission(await parsed_request.engine)
    response = await gateway.proxy_form_data(parsed_request)
    return Response(**response)


@extract_router.post("/extract-image-page")
@inject
async def extract_image_page(
    request: Request,
    blob_name: str = Body(..., alias="blobName"),
    engine: OCREngineEnum = Body(...),
    language: str = Body("eng"),
    gateway: OCRGateway = Depends(Provide[Containers.ocr_gateway]),
):
    parsed_request = BodyParsedRequest(request)
    check_permission(await parsed_request.engine)
    response = await gateway.proxy(parsed_request)
    return Response(**response)
