from deps_ocr_engines.domain.constants import OCREngineEnum

OCR_ENGINE_NAMES = {  # noqa: WPS407
    OCREngineEnum.TESSERACT: "Tesseract",
    OCREngineEnum.GCP_VISION: "GCP Vision",
    OCREngineEnum.AWS_TEXTRACT: "AWS Textract",
}
