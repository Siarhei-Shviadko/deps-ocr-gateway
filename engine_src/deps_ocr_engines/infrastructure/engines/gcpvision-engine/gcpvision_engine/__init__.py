# type: ignore
from typing import List

from gcpvision_engine.gcp_vision_ocr import GCPVisionOCR

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.interfaces import IOCREngine
from deps_ocr_engines.infrastructure.engines.engine_factory import AbstractEngineFactory


class EngineFactory(AbstractEngineFactory):
    @staticmethod
    def get_engine_name() -> OCREngineEnum:
        return OCREngineEnum.GCP_VISION

    @staticmethod
    def get_engine() -> IOCREngine:
        return GCPVisionOCR

    @staticmethod
    def get_engine_settings() -> OCREngineSettings:
        return OCREngineSettings

    @staticmethod
    def get_engine_config(config) -> List[str]:
        return [config["gcp_vision_auth_key"]]
