import pytest

from deps_ocr_engines.application import Application
from deps_ocr_engines.infrastructure import engines


@pytest.mark.application
def test_application_extract_image_page(
    ocr_service_mock,
    storage_service_mock,
    text_lines_v2,
):
    storage_service_mock.download_content.return_value = b""
    ocr_service_mock.execute.return_value = text_lines_v2
    application = Application(ocr_service_mock, storage_service_mock, engines.EngineFactory.get_engine_settings)

    text_lines = application.extract_image_page("test.png")

    assert text_lines == text_lines_v2
