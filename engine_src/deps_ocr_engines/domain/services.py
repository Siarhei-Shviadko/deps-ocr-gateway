import logging
from io import BytesIO
from typing import Dict, List, Union

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities import OCREngineInitSettings, OCREngineSettings
from deps_ocr_engines.domain.entities_v2 import TextLineEntity
from deps_ocr_engines.domain.interfaces import IOCREngine


class OCRService:
    def __init__(
        self,
        init_engine: bool,
        registered_engine: Dict[str, Union[OCREngineEnum, OCREngineInitSettings]],
    ):
        self._registered_engine = registered_engine
        self._logger = logging.getLogger(self.__class__.__name__)

        if init_engine:
            init_settings = self._registered_engine["init_settings"]
            init_settings.engine_cls(*init_settings.engine_args)  # type: ignore

    def execute(
        self,
        image: BytesIO,
        engine_config: OCREngineSettings,
        language: str = "eng",
    ) -> List[TextLineEntity]:
        ocr_engine = self._initialize_engine()
        ocr_engine.set_language(language)
        ocr_engine.set_config(engine_config)
        self._logger.debug("OCR engine %s setted up." % ocr_engine.__dict__)  # noqa: WPS609
        return ocr_engine.extract_text(image)

    def _initialize_engine(self) -> IOCREngine:
        init_settings = self._registered_engine["init_settings"]
        return init_settings.engine_cls(*init_settings.engine_args)  # type: ignore
