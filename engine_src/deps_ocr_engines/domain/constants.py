from enum import Enum


class OCREngineEnum(str, Enum):
    TESSERACT = "TESSERACT"
    GCP_VISION = "GCP_VISION"
    AWS_TEXTRACT = "AWS_TEXTRACT"
    AZURE_FORM_RECOGNIZER = "AZURE_FORM_RECOGNIZER"


PROJECT_NAME = "DEPS OCR Service"
PROJECT_DESCRIPTION = "OCR service for extracting text from image using different OCR engines."
API_PREFIX = "/api/ocr"
SWAGGER_DOC_URL = "/docs"

# Default language for engines if language wasn't set manually
OCR_DEFAULT_LANGUAGE = "eng"
