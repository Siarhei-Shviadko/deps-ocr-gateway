import pytest


@pytest.fixture
def ocr_service_mock(mocker, client):
    mock = mocker.Mock(client.app.app.ocr_service.cls)
    with client.app.app.ocr_service.override(mock):
        yield mock
