from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.infrastructure.engines.enums import OCREngineMode, PageSegMode


class TesseractSettings(OCREngineSettings):
    psm: PageSegMode = PageSegMode.AUTO
    oem: OCREngineMode = OCREngineMode.DEFAULT
