from random import randint
from uuid import uuid4

import pytest
from deps_message_flow.commands.consumer import CommandMessage

from .test_ocr_image_command_handler import OCR_RESPONSE


@pytest.fixture
def ocr_image_command(mocker, this_user):
    extraction_params = {"ner": True, "ocr": True, "tables": True, "ocr_engine": "TESSERACT", "language": "eng"}

    cm = mocker.Mock(CommandMessage)
    cm.command.document_id = randint(1, 10)
    cm.command.source_id = "ae205e40bf5f495f93b601fecb203673"
    cm.command.file_path = f"{uuid4().hex}.pdf"
    cm.command.extraction_params = extraction_params
    cm.command.identify_document = True
    cm.command.extract_data = True
    cm.command.document_type = uuid4().hex

    return cm


@pytest.fixture
def success_requests_mock(requests_mock, ocr_image_command):
    file_path = ocr_image_command.command.file_path
    file_name = file_path.split(".")[0]
    metadata_path = f"metadata_{file_name}.json"
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{file_path}",
        content=b"document_image",
    )
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{metadata_path}",
        content=b"document_metadata",
    )
    requests_mock.register_uri(
        "POST",
        "http://ocr-gateway:8000/api/ocr/v2/extract-text",
        json=OCR_RESPONSE,
    )

    yield requests_mock


@pytest.fixture
def ocr_gateway_failure_requests_mock(requests_mock, ocr_image_command):
    file_path = ocr_image_command.command.file_path
    file_name = file_path.split(".")[0]
    metadata_path = f"metadata_{file_name}.json"
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{file_path}",
        content=b"document_image",
    )
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{metadata_path}",
        content=b"document_metadata",
    )
    requests_mock.register_uri(
        "POST",
        "http://ocr-gateway:8000/api/ocr/v2/extract-text",
        status_code=404,
    )

    yield requests_mock


@pytest.fixture
def file_storage_failure_requests_mock(requests_mock, ocr_image_command):
    file_path = ocr_image_command.command.file_path
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{file_path}",
        status_code=404,
    )

    yield requests_mock


@pytest.fixture
def metadata_failure_requests_mock(requests_mock, ocr_image_command):
    file_path = ocr_image_command.command.file_path
    file_name = file_path.split(".")[0]
    metadata_path = f"metadata_{file_name}.json"
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{file_path}",
        content=b"document_image",
    )
    requests_mock.register_uri(
        "GET",
        f"http://deps-file-storage:8004/api/storage/v1/file/{metadata_path}",
        status_code=404,
    )
    requests_mock.register_uri(
        "POST",
        "http://ocr-gateway:8000/api/ocr/v2/extract-text",
        json=OCR_RESPONSE,
    )

    yield requests_mock


@pytest.fixture()
def disable_all_engines(containers):
    with containers.config.engines_settings.enabled_engines.override([]):
        yield
