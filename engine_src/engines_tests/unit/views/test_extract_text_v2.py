import io
import os

import pytest

from deps_ocr_engines.domain.exceptions import OCRError


class TestExtractTextV2View:
    def test_post__valid_body__return_200_response(self, client, ocr_service_mock, text_lines_v2):
        ocr_service_mock.execute.return_value = text_lines_v2

        response = client.post(
            "/api/ocr/v2/extract-text",
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
            data={"engineSettings": '{"psm": "AUTO_ONLY", "oem": "LSTM_ONLY"}'},
        )

        assert response.status_code == 200

    def test_post__specific_config_into_default_config__return_200_response(
        self, client, ocr_service_mock, text_lines_v2
    ):
        ocr_service_mock.execute.return_value = text_lines_v2

        response = client.post(
            "/api/ocr/v2/extract-text",
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
            data={"engineSettings": '{"psm": "SINGLE_LINE", "oem": "TESSERACT_LSTM_COMBINED"}'},
        )

        assert response.status_code == 200

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

    @pytest.mark.skipif(
        os.getenv("OCR_ENGINE") != "TESSERACT", reason="Current ocr engine doesn't support engine settings."
    )
    def test_post__invalid_config__return_400_response(self, client):
        response = client.post(
            "/api/ocr/v2/extract-text",
            files={
                "file": (
                    "test.png",
                    io.BytesIO(open("engines_tests/data/empty_image.jpg", "rb").read()),
                )
            },
            data={"engineSettings": '{"psm": "O_O", "oem": "LSTM_ONLY"}'},
        )

        assert response.json() == {"detail": "Invalid config: `{'psm': 'O_O', 'oem': 'LSTM_ONLY'}`"}
        assert response.status_code == 400

    def test_post__valid_body_wrong_image__return_400_response(self, client, ocr_service_mock):
        ocr_service_mock.execute.side_effect = OCRError

        response = client.post(
            "/api/ocr/v2/extract-text",
            files={"file": ("test.png", io.BytesIO())},
        )

        assert response.status_code == 400

    def test_post__invalid_body__return_422_response(self, client):
        response = client.post(
            "/api/ocr/v2/extract-text",
            files={"file": ("test.png", io.BytesIO())},
            data={"engineSettings": "TEST_ENGINE"},
        )

        assert response.status_code == 422
