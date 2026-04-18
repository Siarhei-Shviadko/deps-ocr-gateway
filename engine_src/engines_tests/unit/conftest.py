import pytest
from PIL import Image


@pytest.fixture(scope="function", autouse=False)
def passport_image():
    with Image.open("engines_tests/data/passport_image.jpg") as image:
        return image


@pytest.fixture
def ocr_service_mock(mocker, client):
    mock = mocker.Mock(client.app.app.ocr_service.cls)
    with client.app.app.ocr_service.override(mock):
        yield mock


@pytest.fixture
def storage_service_mock(mocker, client):
    mock = mocker.Mock(client.app.app.storage_service.cls)
    with client.app.app.storage_service.override(mock):
        yield mock


@pytest.fixture
def application_mock(mocker, containers):
    mock = mocker.Mock(containers.application.cls)
    with containers.application.override(mock):
        yield mock
