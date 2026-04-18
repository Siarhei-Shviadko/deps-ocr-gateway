from fastapi import APIRouter

from .debug import router as debug_router
from .service_info import service_info_router
from .v1 import router as v1_router
from .v2 import router as v2_router

router = APIRouter()
router.include_router(v2_router, prefix="/v2")
router.include_router(service_info_router)
router.include_router(debug_router, tags=["Debug"])
router.include_router(v1_router, prefix="/v1")
