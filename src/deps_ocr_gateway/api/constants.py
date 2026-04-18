from enum import Enum


class OCREngineEnum(str, Enum):
    TESSERACT = "TESSERACT"
    GCP_VISION = "GCP_VISION"
    AWS_TEXTRACT = "AWS_TEXTRACT"
    AZURE_FORM_RECOGNIZER = "AZURE_FORM_RECOGNIZER"


FREE_OCR_ENGINES = (OCREngineEnum.TESSERACT,)


OCR_ENGINE_NAMES = {  # noqa: WPS407
    OCREngineEnum.TESSERACT: "Tesseract",
    OCREngineEnum.GCP_VISION: "GCP Vision",
    OCREngineEnum.AWS_TEXTRACT: "AWS Textract",
    OCREngineEnum.AZURE_FORM_RECOGNIZER: "Azure Form Recognizer",
}


class LanguagesEnum(str, Enum):
    eng = "English"
    rus = "Russian"
    chi_sim = "Simplified Chinese"
    deu = "German"
    spa = "Spanish"
    ukr = "Ukrainian"
