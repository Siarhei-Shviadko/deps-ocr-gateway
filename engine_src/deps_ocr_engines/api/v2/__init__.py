from fastapi import APIRouter

from .engines import router as engines_router
from .extract_text import router as extract_text_router
from .languages import language_router

router = APIRouter()
router.include_router(extract_text_router, tags=["Text extraction"])
router.include_router(engines_router, tags=["OCR Engines"])
router.include_router(language_router, tags=["Languages"])
