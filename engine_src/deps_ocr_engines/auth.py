from http import HTTPStatus
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import Request

from deps_ocr_engines.containers import Containers
from deps_ocr_engines.domain.exceptions import AuthError
from deps_ocr_engines.extras import (
    DepsAuthError,
    DepsAuthService,
    EmptyAuthorizationHeader,
    InvalidAuthorizationHeaderFormat,
    InvalidJWTError,
)
from deps_ocr_engines.infrastructure.access_management.context_vars import user

PUBLIC_ENDPOINTS = (
    "/api/ocr/docs",
    "/api/ocr/openapi.json",
    "/api/ocr/debug/500",
    "/api/ocr/healthcheck",
    "/favicon.ico",
)


@inject
def set_user_from_jwt(
    request: Request,
    auth_service: DepsAuthService = Provide[Containers.deps_auth_service],
) -> None:
    if request.url.path in PUBLIC_ENDPOINTS:
        return None

    try:
        user_credentials = auth_service.authorize(request.headers)
        user.set(user_credentials)
    except (EmptyAuthorizationHeader, InvalidAuthorizationHeaderFormat) as e:
        raise AuthError(
            detail=str(e),
            status_code=HTTPStatus.UNAUTHORIZED,
        )
    except InvalidJWTError:
        raise AuthError(
            detail="Invalid JWT",
            status_code=HTTPStatus.UNAUTHORIZED,
        )
    except DepsAuthError as e:
        raise AuthError(
            detail=str(e),
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def get_current_user_organisation() -> Optional[str]:
    current_user = user.get(None)

    if current_user is None:
        return None

    if not current_user.get("groups", []):
        return None

    return current_user["groups"][0]
