import io
import json
import os

import pytest

from deps_ocr_engines.domain.constants import OCREngineEnum

PAID_ENGINES = [OCREngineEnum.AWS_TEXTRACT, OCREngineEnum.GCP_VISION]


@pytest.mark.skipif(os.getenv("OCR_ENGINE") in PAID_ENGINES, reason="Paid engines can't pass this tests.")
class TestExtractTextV2View:
    def test_post__valid_body__return_200_response(self, client):
        response = client.post(
            "/api/ocr/v2/extract-text",
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_post__valid_body_metadata_exists__return_200_response(self, client):
        with open("engines_tests/data/metadata_expected_output.json") as f:
            expected_json = json.loads(f.read())
        response = client.post(
            "/api/ocr/v2/extract-text",
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/non_empty_image.png", "rb").read()),
                ),
                "metadata": (
                    "metadata.json",
                    io.BytesIO(open("engines_tests/data/non_empty_image_metadata.json", "rb").read()),
                ),
            },
        )
        assert response.status_code == 200

        result_json = response.json()

        for result_text_line, expected_text_line in zip(result_json, expected_json):
            for result_word_box, expected_word_box in zip(
                result_text_line["wordBoxes"], expected_text_line["wordBoxes"]
            ):
                assert result_word_box["content"] == expected_word_box["content"]

    def test_post_v1__valid_body__return_200_response(self, client):
        response = client.post(
            "/api/ocr/v1/extract-text",
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
        )

        assert response.status_code == 200
        assert response.json() == []
