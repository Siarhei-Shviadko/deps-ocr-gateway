import http

__all__ = ["AuthError", "NotFoundError", "OCRGatewayException", "ForbiddenError"]


class OCRGatewayException(Exception):
    code = "ocr_gateway_exception"


class NotFoundError(OCRGatewayException):
    code = "not_found_error"


class ForbiddenError(OCRGatewayException):
    code = "forbidden_error"


class AuthError(OCRGatewayException):
    code = "authentication_error"

    def __init__(self, detail: str, status_code: int = http.HTTPStatus.UNAUTHORIZED):
        super().__init__(detail)
        self.status_code = status_code
