# type: ignore
import os

from deps_ocr_engines.domain.constants import OCREngineEnum

if (engine := OCREngineEnum(os.getenv("OCR_ENGINE"))) == OCREngineEnum.TESSERACT:
    from tesseract_engine import *
elif engine == OCREngineEnum.AWS_TEXTRACT:
    from aws_textract_engine import *
elif engine == OCREngineEnum.GCP_VISION:
    from gcpvision_engine import *
elif engine == OCREngineEnum.AZURE_FORM_RECOGNIZER:
    from azure_form_recognizer_engine import *
else:
    raise NotImplementedError(f"OCR engine {engine} doesn't imlemented.")
