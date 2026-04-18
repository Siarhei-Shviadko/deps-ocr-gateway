# type: ignore
from typing import List

from tesseract_engine.settings import TesseractSettings
from tesseract_engine.tesseract_ocr import TesseractOCR

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.interfaces import IOCREngine
from deps_ocr_engines.infrastructure.engines.engine_factory import AbstractEngineFactory


class EngineFactory(AbstractEngineFactory):
    @staticmethod
    def get_engine_name() -> OCREngineEnum:
        return OCREngineEnum.TESSERACT

    @staticmethod
    def get_engine() -> IOCREngine:
        return TesseractOCR

    @staticmethod
    def get_engine_settings() -> OCREngineSettings:
        return TesseractSettings

    @staticmethod
    def get_engine_config(config) -> List[str]:
        return [config["default_language"]]
