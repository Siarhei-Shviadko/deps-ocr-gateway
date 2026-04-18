from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import Depends

from deps_ocr_gateway.api.constants import FREE_OCR_ENGINES, OCREngineEnum
from deps_ocr_gateway.api.exceptions import ForbiddenError, OCRGatewayException
from deps_ocr_gateway.containers import Containers

from ..auth import get_current_user_organisation

__all__ = ["check_permission"]


@inject
def _is_engine_available_for_organisation(
    engine,
    privileged_group: str = Depends(Provide[Containers.config.privileged_group]),
) -> bool:
    if engine not in FREE_OCR_ENGINES:
        return get_current_user_organisation() == privileged_group
    return True


@inject
def _is_engine_available(
    engine: str,
    available_engines: List[OCREngineEnum] = Depends(Provide[Containers.config.engines_settings.enabled_engines]),
) -> None:
    if engine in available_engines:
        return
    raise OCRGatewayException(f"Engine {engine} is not available")


@inject
def check_permission(
    engine: str,
    restriction_enabled: bool = Depends(
        Provide[Containers.config.paid_engines_restriction_enabled],
    ),
) -> None:
    _is_engine_available(engine)
    if restriction_enabled and not _is_engine_available_for_organisation(engine):
        raise ForbiddenError(
            f"Engine {engine} is not free and current user has no permission for using it.",
        )
