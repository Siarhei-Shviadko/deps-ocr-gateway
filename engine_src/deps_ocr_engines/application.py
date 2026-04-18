import io
from typing import Callable, List, Type

from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.entities_v2 import TextLineEntity
from deps_ocr_engines.domain.services import OCRService
from deps_ocr_engines.extras import StorageControllerService

__all__ = ["Application"]


class Application:
    def __init__(
        self,
        ocr_service: OCRService,
        storage_service: StorageControllerService,
        engine_settings: Callable[[], Type[OCREngineSettings]],
    ) -> None:
        self._ocr_service = ocr_service
        self._storage_service = storage_service
        self._engine_settings = engine_settings()()

    def extract_image_page(
        self,
        blob_name: str,
        language: str = "eng",
    ) -> List[TextLineEntity]:
        blob = self._storage_service.download_content(blob_name)
        with io.BytesIO(blob) as buffer:
            return self._ocr_service.execute(image=buffer, language=language, engine_config=self._engine_settings)
