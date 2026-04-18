import logging
import os
from http import HTTPStatus
from typing import Awaitable, Callable

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import Response

from deps_ocr_gateway import api
from deps_ocr_gateway.api.error_handlers import (
    json_ocr_gateway_error_handler,
    register_error_handler,
)
from deps_ocr_gateway.containers import Containers
from deps_ocr_gateway.extras import add_auth_to_openapi
from deps_ocr_gateway.infrastructure import user
from deps_ocr_gateway.messaging import handlers
from deps_ocr_gateway.settings import Settings

_logger = logging.getLogger(__name__)


__all__ = ["init_containers", "create_fastapi", "register_auth", "run_message_dispatcher", "run_api"]


def init_containers() -> Containers:
    settings = Settings()
    containers = Containers(messaging_driver_settings=settings.messaging_driver_settings)
    containers.config.from_pydantic(settings)
    containers.init_resources()

    containers.message_brokers.broker_client().user_context = user

    containers.wire(packages=[api], modules=[handlers])
    containers.domain_event_publishers.wire(modules=[handlers])

    _logger.info("OCR-Gateway service working ....")

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
    fastapi_app.include_router(api.service_info_router, prefix=containers.config.api_prefix())
    fastapi_app.include_router(api.engines_router, prefix=containers.config.api_prefix())
    fastapi_app.include_router(api.language_router, prefix=containers.config.api_prefix())
    fastapi_app.include_router(api.extract_router, prefix=containers.config.api_prefix())
    fastapi_app.include_router(api.extract_router_v1, prefix=containers.config.api_prefix())

    register_error_handler(fastapi_app)

    fastapi_app.app = containers  # type: ignore[attr-defined]
    register_auth(fastapi_app)

    return fastapi_app


def register_auth(app: FastAPI):
    add_auth_to_openapi(app)

    @app.middleware("http")
    async def handle_authorization(  # noqa: WPS430
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            api.auth.set_user_from_token(request)
        except api.AuthError as err:
            return json_ocr_gateway_error_handler(err, HTTPStatus.UNAUTHORIZED)
        return await call_next(request)


def run_api():
    use_web_concurrency = "WEB_CONCURRENCY" in os.environ
    options = {
        "host": "0.0.0.0",  # noqa: S104
        "port": 8000,
        "log_level": "debug",
        "workers": int(os.getenv("WEB_CONCURRENCY")) if use_web_concurrency else 3,
        "reload": os.getenv("ENV", "prod") == "local",
    }
    uvicorn.run("deps_ocr_gateway.entrypoint:create_fastapi", **options)


def run_message_dispatcher() -> None:
    containers: Containers = init_containers()

    if containers.config.sentry.enabled():
        import sentry_sdk  # noqa: WPS433

        integrations = []
        if containers.config.sentry.trace_enabled:
            from deps_integrations import SentryPubSubIntegration  # noqa: WPS433

            integrations.append(SentryPubSubIntegration())

        sentry_sdk.init(
            dsn=containers.config.sentry.dsn(),
            traces_sample_rate=containers.config.sentry.traces_sample_rate(),
            environment=containers.config.env(),
            integrations=integrations,
            release=containers.config.info.hash(),
            debug=False,
        )

        _logger.info("SENTRY ENABLED!")

    dispatcher = containers.dispatcher()
    dispatcher.start_consuming()
