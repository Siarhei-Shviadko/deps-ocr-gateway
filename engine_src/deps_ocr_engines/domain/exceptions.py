import http


class OCRError(Exception):
    code = "ocr_error"


class OCRLanguageNotSupported(OCRError):
    code = "ocr_language_not_supported_error"


class OCREngineNotFoundError(OCRError):
    code = "ocr_engine_not_found_error"


class ForbiddenError(OCRError):
    code = "forbidden_error"


class AuthError(OCRError):
    code = "authentication_error"

    def __init__(self, detail: str, status_code: int = http.HTTPStatus.UNAUTHORIZED):
        super().__init__(detail)
        self.status_code = status_code
