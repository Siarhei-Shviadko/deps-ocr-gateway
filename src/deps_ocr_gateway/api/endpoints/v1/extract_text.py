from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Request, Response, UploadFile
from pydantic import Json

from deps_ocr_gateway.api.constants import OCREngineEnum
from deps_ocr_gateway.containers import Containers
from deps_ocr_gateway.infrastructure import OCRGateway

from ...requests import FormParsedRequestV1
from ..shared import check_permission

__all__ = ["extract_router_v1"]

extract_router_v1 = APIRouter(prefix="/v1", tags=["Version 1"])


@extract_router_v1.post(
    "/extract-text",
    deprecated=True,
    description="Uses only for extract-text from deps-table service.",
)
@inject
async def extract_text(
    request: Request,
    engine: OCREngineEnum,
    language: str = "eng",
    file: UploadFile = File(...),
    engine_settings: Json = Form(str({}), alias="engineSettings"),
    gateway: OCRGateway = Depends(Provide[Containers.ocr_gateway]),
):
    parsed_request = FormParsedRequestV1(request)
    check_permission(await parsed_request.engine)
    response = await gateway.proxy_form_data(parsed_request)
    return Response(**response)
