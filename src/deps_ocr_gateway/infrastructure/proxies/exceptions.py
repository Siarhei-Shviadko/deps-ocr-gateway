from deps_ocr_gateway.api.exceptions import OCRGatewayException

__all__ = ["OcrGatewayRequestError"]


class OcrGatewayRequestError(OCRGatewayException):
    code = "ocr_gateway_request_error"
