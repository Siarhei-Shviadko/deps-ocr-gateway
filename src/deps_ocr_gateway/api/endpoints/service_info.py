from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_ocr_gateway.api.serializers import BuildInfo
from deps_ocr_gateway.containers import Containers

__all__ = ["service_info_router"]

service_info_router = APIRouter(prefix="/service-info")


@service_info_router.get("/version", tags=["Service Info"], response_model=BuildInfo)
@inject
def get_build_info(build_info=Depends(Provide[Containers.core.build_info])):
    return BuildInfo(**build_info)
