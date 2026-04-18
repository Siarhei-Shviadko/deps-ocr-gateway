from abc import ABC, abstractmethod
from typing import List

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.interfaces import IOCREngine


class AbstractEngineFactory(ABC):
    @staticmethod
    @abstractmethod
    def get_engine() -> IOCREngine:  # noqa: WPS605
        pass

    @staticmethod
    @abstractmethod
    def get_engine_name() -> OCREngineEnum:  # noqa: WPS605
        pass

    @staticmethod
    @abstractmethod
    def get_engine_settings() -> OCREngineSettings:  # noqa: WPS605
        pass

    @staticmethod
    @abstractmethod
    def get_engine_config(config) -> List[str]:
        pass
