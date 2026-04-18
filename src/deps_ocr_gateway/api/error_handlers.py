import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette import status
from starlette.requests import Request

from deps_ocr_gateway.api.exceptions import (
    ForbiddenError,
    NotFoundError,
    OCRGatewayException,
)
from deps_ocr_gateway.api.serializers import ErrorSerializer

__all__ = ["json_ocr_gateway_error_handler", "register_error_handler"]
logger = logging.getLogger(__name__)


def json_ocr_gateway_error_handler(error: OCRGatewayException, status_code: int):
    error_message = ErrorSerializer(code=error.code, message=str(error)).model_dump()
    return JSONResponse(status_code=status_code, content=error_message)


def register_error_handler(app: FastAPI) -> None:
    @app.exception_handler(OCRGatewayException)
    def handle_ocr_gateway_exception(  # noqa: WPS430
        req: Request,
        error: OCRGatewayException,
    ):
        mapper = [
            (NotFoundError, HTTPStatus.NOT_FOUND),
            (ForbiddenError, HTTPStatus.FORBIDDEN),
            (OCRGatewayException, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_ocr_gateway_error_handler(error, status_code)

    @app.exception_handler(ValidationError)
    def bad_request(req: Request, exc: ValidationError):  # noqa: WPS430
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorSerializer(code="bad_request", message=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):  # noqa: WPS430
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorSerializer(code="unhandled_error", message=str(error)).model_dump(),
        )
