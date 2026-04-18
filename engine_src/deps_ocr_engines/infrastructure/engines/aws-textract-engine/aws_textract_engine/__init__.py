# type: ignore
from typing import List

from aws_textract_engine.aws_textract_ocr import AWSTextractOCR

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.interfaces import IOCREngine
from deps_ocr_engines.infrastructure.engines.engine_factory import AbstractEngineFactory


class EngineFactory(AbstractEngineFactory):
    @staticmethod
    def get_engine_name() -> OCREngineEnum:
        return OCREngineEnum.AWS_TEXTRACT

    @staticmethod
    def get_engine() -> IOCREngine:
        return AWSTextractOCR

    @staticmethod
    def get_engine_settings() -> OCREngineSettings:
        return OCREngineSettings

    @staticmethod
    def get_engine_config(config) -> List[str]:
        return [config["aws_region_name"], config["aws_access_key_id"], config["aws_secret_access_key"]]
