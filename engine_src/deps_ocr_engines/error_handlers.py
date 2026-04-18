import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette import status
from starlette.requests import Request

from deps_ocr_engines.api.error import ErrorModel
from deps_ocr_engines.domain.exceptions import (
    ForbiddenError,
    OCREngineNotFoundError,
    OCRError,
)
from deps_ocr_engines.extras import FileStorageRequestError

logger = logging.getLogger(__name__)


def json_error_handler(error: OCRError, status_code: int):
    return JSONResponse(
        status_code=status_code,
        content=ErrorModel(code=error.code, message=str(error)).model_dump(),
    )  # noqa: WPS221


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(OCRError)
    def handle_ocr_exception(req: Request, error: OCRError):
        mapper = [
            (OCREngineNotFoundError, HTTPStatus.NOT_FOUND),
            (ForbiddenError, HTTPStatus.FORBIDDEN),
            (OCRError, HTTPStatus.BAD_REQUEST),
        ]

        for error_type, status_code in mapper:
            if issubclass(type(error), error_type):
                return json_error_handler(error, status_code)

    @app.exception_handler(FileStorageRequestError)
    def file_storage_error(req: Request, exc: FileStorageRequestError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorModel(code="file_storage_error", message=str(exc)).model_dump(),
        )

    @app.exception_handler(Exception)
    def handle_all_errors(req: Request, error: Exception):
        logger.error(f"Unhandled error {error}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorModel(code="unhandled_error", message=str(error)).model_dump(),
        )
