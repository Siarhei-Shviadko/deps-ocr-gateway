# type: ignore
from typing import List

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.interfaces import IOCREngine
from deps_ocr_engines.infrastructure.engines.engine_factory import AbstractEngineFactory

from .azure_form_recognizer_ocr import AzureFormRecognizerOCR


class EngineFactory(AbstractEngineFactory):
    @staticmethod
    def get_engine_name() -> OCREngineEnum:
        return OCREngineEnum.AZURE_FORM_RECOGNIZER

    @staticmethod
    def get_engine() -> IOCREngine:
        return AzureFormRecognizerOCR

    @staticmethod
    def get_engine_settings() -> OCREngineSettings:
        return OCREngineSettings

    @staticmethod
    def get_engine_config(config) -> List[str]:
        return [config["azure_form_recognizer_api_url"], config["azure_form_recognizer_api_key"]]
