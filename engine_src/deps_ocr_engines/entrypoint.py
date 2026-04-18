import logging
from http import HTTPStatus
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.responses import Response

from deps_ocr_engines import api, auth
from deps_ocr_engines.containers import Containers
from deps_ocr_engines.domain.exceptions import AuthError
from deps_ocr_engines.error_handlers import json_error_handler, register_error_handlers
from deps_ocr_engines.extras import add_auth_to_openapi
from deps_ocr_engines.infrastructure.access_management.context_vars import user
from deps_ocr_engines.settings import Settings

_logger = logging.getLogger(__name__)


__all__ = ["init_containers", "create_fastapi", "register_auth"]


def init_containers() -> Containers:
    settings = Settings()
    containers = Containers()
    containers.config.from_dict(settings.model_dump())
    containers.init_resources()

    containers.wire(packages=[api], modules=[auth])

    logging.basicConfig(level=containers.config.gunicorn().get("log_level").upper())
    _logger.info("OCR service uses %s engine" % containers.config.engine.ocr_engine().value)

    return containers


def create_fastapi() -> FastAPI:
    containers: Containers = init_containers()

    fastapi_app = FastAPI(
        title=containers.config.project_name(),
        version=containers.config.version(),
        docs_url=f"{containers.config.api_prefix()}{containers.config.swagger_doc_url()}"
        if containers.config.documentation_enabled()
        else None,
        description=containers.config.description(),
        openapi_url=f"{containers.config.api_prefix()}/openapi.json"
        if containers.config.documentation_enabled()
        else None,
    )
    fastapi_app.include_router(api.router, prefix=containers.config.api_prefix())

    register_error_handlers(fastapi_app)

    if containers.config.sentry.enabled():
        import sentry_sdk
        from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

        integrations = []
        if containers.config.sentry.trace_enabled():
            from deps_integrations import SentryPubSubIntegration

            integrations.append(SentryPubSubIntegration())

        sentry_sdk.init(
            dsn=containers.config.sentry.dsn(),
            traces_sample_rate=containers.config.sentry.traces_sample_rate(),
            environment=containers.config.env(),
            integrations=integrations,
            release=containers.config.info.hash(),
            debug=False,
        )
        fastapi_app.add_middleware(SentryAsgiMiddleware)

        _logger.info("SENTRY ENABLED!")

    fastapi_app.app = containers  # type: ignore[attr-defined]
    if containers.config.authentication.enabled():
        register_auth(fastapi_app)
        containers.storage_service().set_user_context(user)

    return fastapi_app


def register_auth(app: FastAPI):
    add_auth_to_openapi(app)

    @app.middleware("http")
    async def handle_authorization(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        try:
            auth.set_user_from_jwt(request)
        except AuthError as err:
            return json_error_handler(err, HTTPStatus.UNAUTHORIZED)
        return await call_next(request)
