import io
import os

import pytest

from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.domain.entities_v2 import TextLineEntity
from deps_ocr_engines.domain.exceptions import OCRError

OCR_ENGINE = "OCR_ENGINE"


@pytest.mark.skipif(os.getenv(OCR_ENGINE) != OCREngineEnum.TESSERACT, reason="TESSERACT engnine doesn't installed.")
class TestTesseractOCR:
    def test__recognize_image_with_some_text(self, ocr_config, settings, tesseract_ocr_engine):
        if not settings.engine.default_language:
            pytest.skip("Tesseract settings are not set")
        image_to_test = self._get_binary_file_content(ocr_config.get("TEST_IMAGE_PATH"))
        ocr_result = tesseract_ocr_engine.extract_text(image_to_test)

        assert len(ocr_result) > 5
        assert isinstance(ocr_result[0], TextLineEntity)

    def test__invalid_image(self, ocr_config, settings, tesseract_ocr_engine):
        if not settings.engine.default_language:
            pytest.skip("Tesseract settings are not set")

        with pytest.raises(OCRError):
            tesseract_ocr_engine.extract_text(io.BytesIO())

    def test__recognize_empty_image(self, ocr_config, settings, tesseract_ocr_engine):
        if not settings.engine.default_language:
            pytest.skip("Tesseract settings are not set")
        image_to_test = self._get_binary_file_content(ocr_config.get("EMPTY_IMAGE_PATH"))
        ocr_result = tesseract_ocr_engine.extract_text(image_to_test)

        assert len(ocr_result) == 0

    @staticmethod
    def _get_binary_file_content(file_path):
        with open(file_path, "br+") as f:
            file_content = io.BytesIO(f.read())
            file_content.seek(0, 0)
        return file_content
