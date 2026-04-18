import json
import os
from dataclasses import asdict

import pytest

from deps_ocr_engines.domain.exceptions import OCREngineNotFoundError, OCRError
from engines_tests.factories.entities_v2 import PdfImageMetaEntityFactory
from engines_tests.factories.text_line_v2 import TextLineFactory as TextLineFactory_v2

with open("engines_tests/data/empty_image.jpg", "rb") as f:
    file = f.read()


@pytest.fixture
def file_storage_mock(mocker, client):
    mock = mocker.Mock(client.app.app.storage_service.cls)
    mock.download_content.return_value = file
    mock.load_metadata.return_value = {}
    client.app.app.storage_service.override(mock)
    return mock


class TestExtractAreaV2View:
    endpoint = "/api/ocr/v2/extract-area"
    request_data = {
        "blobFile": "some_file.png",
        "engine": "TESSERACT",
        "engineSettings": '{"psm": "AUTO_ONLY", "oem": "LSTM_ONLY"}',
        "area": {"x": 0, "y": 0, "w": 1, "h": 1},
    }
    page_width = 2480
    page_height = 3509

    def test_post__valid_body_no_metadata__return_200_response(
        self, client, ocr_service_mock, file_storage_mock, text_lines_v2
    ):
        ocr_service_mock.execute.return_value = text_lines_v2
        response = client.post(
            self.endpoint,
            data=json.dumps(self.request_data),
        )
        assert response.status_code == 200
        ocr_service_mock.execute.assert_called_once()

    @pytest.mark.skipif(
        os.getenv("OCR_ENGINE") != "TESSERACT", reason="Current engine doesn't supprot engine_settings."
    )
    def test_post__invalid_config__return_400_response(self, client):
        request_data = self.request_data.copy()
        request_data["engineSettings"] = '{"psm": "O_O", "oem": "LSTM_ONLY"}'
        response = client.post(
            self.endpoint,
            data=json.dumps(request_data),
        )
        assert response.json() == {"detail": "Invalid config: `{'psm': 'O_O', 'oem': 'LSTM_ONLY'}`"}
        assert response.status_code == 400

    def test_post__valid_body_wrong_image__return_400_response(self, client, ocr_service_mock, file_storage_mock):
        ocr_service_mock.execute.side_effect = OCRError

        response = client.post(
            self.endpoint,
            data=json.dumps(self.request_data),
        )
        assert response.status_code == 400
        ocr_service_mock.execute.assert_called_once()

    def test_post__valid_body_valid_engine_is_not_registered__return_404_response(self, client, ocr_service_mock):
        ocr_service_mock.execute.side_effect = OCREngineNotFoundError
        request_data = self.request_data.copy()
        request_data["engine"] = "GCP_VISION"
        response = client.post(
            self.endpoint,
            data=json.dumps(request_data),
        )
        assert response.status_code == 404

    def test_post__valid_body_existing_metadata__return_200_right_text(
        self, client, ocr_service_mock, file_storage_mock, metadata_text_lines_v2, ocr_text_lines_v2
    ):
        file_storage_mock.load_metadata.return_value = asdict(
            PdfImageMetaEntityFactory(
                textlines_v2=metadata_text_lines_v2, width=self.page_width, height=self.page_height
            )
        )
        ocr_service_mock.execute.return_value = ocr_text_lines_v2
        response = client.post(
            self.endpoint,
            data=json.dumps(self.request_data),
        )
        assert response.status_code == 200
        ocr_service_mock.execute.assert_called_once()
        assert response.json()["content"] == "Hello World\n!"

    def test_post__valid_body_existing_metadata_force_ocr__return_200_ocr_textlines(
        self, client, ocr_service_mock, file_storage_mock, metadata_text_lines_v2, ocr_text_lines_v2
    ):
        file_storage_mock.load_metadata.return_value = asdict(
            PdfImageMetaEntityFactory(
                textlines_v2=metadata_text_lines_v2, width=self.page_width, height=self.page_height
            )
        )
        ocr_service_mock.execute.return_value = ocr_text_lines_v2

        request_data = self.request_data.copy()
        request_data["forceOCR"] = "true"
        response = client.post(self.endpoint, data=json.dumps(request_data))

        assert response.status_code == 200
        ocr_service_mock.execute.assert_called_once()
        assert response.json()["content"] == "Helloo World\n!"
