from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from deps_ocr_engines.api.serializers import BuildInfoModel
from deps_ocr_engines.containers import Containers

service_info_router = APIRouter(prefix="/service-info")


@service_info_router.get("/version", tags=["Service Info"], response_model=BuildInfoModel)
@inject
def get_build_info(build_info=Depends(Provide[Containers.build_info])):
    return BuildInfoModel(**build_info)
