from fastapi import APIRouter

from deps_ocr_gateway.api.constants import LanguagesEnum

__all__ = ["language_router"]

language_router = APIRouter(prefix="/v1", tags=["Version 1"])


@language_router.get("/languages", response_model=list[dict[str, str]])
def get_languages():
    return [{"code": elem.name, "name": elem.value} for elem in LanguagesEnum]
