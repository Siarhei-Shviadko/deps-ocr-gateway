from http import HTTPStatus

import pytest

from deps_ocr_gateway.api.constants import (
    FREE_OCR_ENGINES,
    LanguagesEnum,
    OCREngineEnum,
)
from deps_ocr_gateway.constants import API_PREFIX


class TestApiOCRGateway:
    @pytest.mark.usefixtures("enable_paid_engine_restriction")
    def test_get_available_engines__no_superuser__only_free_engines(self, client):
        response = client.get(f"{API_PREFIX}/v2/engines")
        res_json = response.json()
        assert response.status_code == HTTPStatus.OK
        assert len(res_json) == len(FREE_OCR_ENGINES)
        assert all(filter(lambda engine: engine["code"] in FREE_OCR_ENGINES, res_json))

    @pytest.mark.usefixtures("set_super_user")
    def test_get_available_engines__superuser__all_engines(self, client):
        response = client.get(f"{API_PREFIX}/v2/engines")
        res_json = response.json()
        assert response.status_code == HTTPStatus.OK
        all_engines = [el.value for el in OCREngineEnum]
        assert len(res_json) == len(OCREngineEnum)
        assert all(filter(lambda engine: engine["code"] in all_engines, res_json))

    def test_languages__return_all_languages(self, client):
        response = client.get(f"{API_PREFIX}/v1/languages")
        res_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert [{el["code"]: el["name"]} for el in res_json] == [{lang.name: lang.value} for lang in LanguagesEnum]

    def test_routing__extract_text__route_to_the_appropriate_pod(self, client, ocr_engine):
        engine, mocked_requests = ocr_engine
        response = client.post(
            f"{API_PREFIX}/v2/extract-text",
            data={"engine": engine.value},
            files={"file": b"", "metadata": b""},
            headers={"deps-token": b'{"subject": "me"}'},
        )
        assert response.status_code == 200
        assert mocked_requests[engine].called

    def test_routing__extract_area__route_to_the_appropriate_pod(self, client, ocr_engine):
        engine, mocked_requests = ocr_engine
        response = client.post(
            f"{API_PREFIX}/v2/extract-area",
            json={"engine": engine.value, "blobFile": "fake_url", "area": {"x": 0.1, "y": 0, "w": 0.5, "h": 0.5}},
            headers={"deps-token": b'{"subject": "me"}'},
        )
        assert response.status_code == 200
        assert mocked_requests[engine].called

    def test_routing__extract_text_v1__route_to_the_appropriate_pod(self, client, ocr_engine):
        engine, mocked_requests = ocr_engine
        response = client.post(
            f"{API_PREFIX}/v1/extract-text?engine={engine.value}&language=eng",
            data={"engineSettings": "{}"},
            files={"file": b"", "metadata": b""},
            headers={"deps-token": b'{"subject": "me"}'},
        )
        assert response.status_code == 200
        assert mocked_requests[engine].called

    @pytest.mark.usefixtures("enable_only_tesseract_engine")
    def test_routing__engine_is_not_available__400(self, client):
        response = client.post(
            f"{API_PREFIX}/v1/extract-text?engine=AWS_TEXTRACT&language=eng",
            data={"engineSettings": "{}"},
            files={"file": b"", "metadata": b""},
            headers={"deps-token": b'{"subject": "me"}'},
        )

        assert response.status_code == 400

    def test_routing__extract_image_page__route_to_the_appropriate_pod(self, client, ocr_engine):
        engine, mocked_requests = ocr_engine
        response = client.post(
            f"{API_PREFIX}/v2/extract-image-page",
            json={"engine": engine.value, "blobName": "test.png", "language": "eng"},
            headers={"deps-token": b'{"subject": "me"}'},
        )
        assert response.status_code == 200
        assert mocked_requests[engine].called
