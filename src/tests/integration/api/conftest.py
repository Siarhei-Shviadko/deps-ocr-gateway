import pytest

from deps_ocr_gateway.api import auth
from deps_ocr_gateway.api.constants import OCREngineEnum


@pytest.fixture(autouse=True)
def mocked_middleware(monkeypatch, mocker):
    monkeypatch.setattr(auth, "set_user_from_token", mocker.Mock({}))


@pytest.fixture
def mocked_request_to_engine_pod(mocker):
    mocks = {
        OCREngineEnum.TESSERACT: mocker.patch(
            "deps_ocr_gateway.infrastructure.proxies.tesseract.TesseractProxy.request",
            return_value={"content": b"", "status_code": 200, "headers": {}},
        ),
        OCREngineEnum.AWS_TEXTRACT: mocker.patch(
            "deps_ocr_gateway.infrastructure.proxies.aws_textract.AWSTextractProxy.request",
            return_value={"content": b"", "status_code": 200, "headers": {}},
        ),
        OCREngineEnum.GCP_VISION: mocker.patch(
            "deps_ocr_gateway.infrastructure.proxies.gcp_vision.GCPVisionProxy.request",
            return_value={"content": b"", "status_code": 200, "headers": {}},
        ),
        OCREngineEnum.AZURE_FORM_RECOGNIZER: mocker.patch(
            "deps_ocr_gateway.infrastructure.proxies.azure.AzureFormRecognizerProxy.request",
            return_value={"content": b"", "status_code": 200, "headers": {}},
        ),
    }
    return mocks


@pytest.fixture(
    params=(
        OCREngineEnum.TESSERACT,
        OCREngineEnum.GCP_VISION,
        OCREngineEnum.AWS_TEXTRACT,
        OCREngineEnum.AZURE_FORM_RECOGNIZER,
    )
)
def ocr_engine(request, mocked_request_to_engine_pod):
    return request.param, mocked_request_to_engine_pod
