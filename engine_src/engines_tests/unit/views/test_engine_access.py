import io
from http import HTTPStatus

import pytest

from deps_ocr_engines.api.constants import OCR_ENGINE_NAMES
from deps_ocr_engines.domain.constants import OCREngineEnum
from deps_ocr_engines.infrastructure.access_management import user

OCR_ENGINES = [engine.name for engine in OCR_ENGINE_NAMES]


@pytest.fixture(params=OCR_ENGINES)
def set_ocr_engine(request, containers):
    with containers.config.engine.ocr_engine.override(request.param):
        yield


@pytest.mark.usefixtures("set_ocr_engine")
class TestGetAvailableEngines:
    endpoint = "/api/ocr/v2/engines"

    def test_get_engine__returns_only_one_engine(self, regular_user, client):
        user.set(regular_user)
        response = client.get(self.endpoint)
        engine = response.json()

        assert response.status_code == HTTPStatus.OK
        assert engine["code"] in OCR_ENGINES


@pytest.mark.usefixtures("set_ocr_engine")
class TestExtractText:
    endpoint = "/api/ocr/v2/extract-text"

    def test_extract_text__success(self, client, regular_user, ocr_service_mock):
        ocr_service_mock.execute.return_value = []
        user.set(regular_user)

        response = client.post(
            self.endpoint,
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == []

    def test_extract_text_engine_set_up_no_errors(self, client, regular_user, ocr_service_mock):
        ocr_service_mock.execute.return_value = []
        user.set(regular_user)

        response = client.post(
            self.endpoint,
            data={"engine": OCREngineEnum.TESSERACT},
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
        )

        assert response.status_code == HTTPStatus.OK
