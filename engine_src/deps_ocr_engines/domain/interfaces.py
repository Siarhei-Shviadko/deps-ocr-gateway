import io
from abc import ABCMeta, abstractmethod
from typing import List

from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.entities_v2 import TextLineEntity


class IOCREngine(metaclass=ABCMeta):
    @abstractmethod
    def extract_text(self, image_data: io.BytesIO) -> List[TextLineEntity]:
        pass

    @abstractmethod
    def set_config(self, config: OCREngineSettings) -> None:
        """
        update engine configuration
        """

    @abstractmethod
    def set_language(self, language: str) -> None:
        """
        Update language in OCR engine.
        If language could be autodetected (e.g. for cloud engines), implementation of this method should be skipped.
        """
