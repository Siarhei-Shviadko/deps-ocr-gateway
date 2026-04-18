# type: ignore
import io
import os
from http import HTTPStatus

import pytest

PAID_ENGINES = ["AWS_TEXTRACT", "GCP_VISION"]


class TestGetAvailableEngines:
    endpoint = "/api/ocr/v2/engines"

    def test_get_available_engines__success(self, client):
        response = client.get(self.endpoint)

        assert response.status_code == HTTPStatus.OK


@pytest.mark.skipif(os.getenv("OCR_ENGINE") in PAID_ENGINES, reason="Can't extract text using paid engine.")
class TestExtractText:
    endpoint = "/api/ocr/v2/extract-text"

    def test_extract_text__success(self, client):
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
