import json
from http import HTTPStatus
from typing import Any, Dict

from fastapi import Request

from deps_ocr_gateway.infrastructure.context_vars import user

from .exceptions import AuthError

__all__ = ["set_user_from_token", "get_current_user_organisation"]

PUBLIC_ENDPOINTS = (
    "/api/ocr/docs",
    "/api/ocr/openapi.json",
    "/api/ocr/debug/500",
    "/api/ocr/healthcheck",
    "/favicon.ico",
)


def set_user_from_token(
    request: Request,
) -> None:
    if request.url.path in PUBLIC_ENDPOINTS:
        return None

    try:
        deps_token = json.loads(request.headers["deps-token"])
        _validate_deps_token(deps_token)
        deps_token["deps_token"] = request.headers["deps-token"]
        user.set(deps_token)

    except KeyError:
        raise AuthError("Deps-token doesn't provided.")

    except TypeError:
        raise AuthError("Provided deps-token isn't correct.")


def _validate_deps_token(deps_token: Dict[str, Any]) -> None:
    if not deps_token:
        raise AuthError("Deps-token validation fails. Deps-token is invalid.")
    elif not deps_token.get("organisation"):
        raise AuthError(
            detail="User without organisation.",
            status_code=HTTPStatus.FORBIDDEN,
        )


def get_current_user_organisation() -> str:
    return user.get()["organisation"]
