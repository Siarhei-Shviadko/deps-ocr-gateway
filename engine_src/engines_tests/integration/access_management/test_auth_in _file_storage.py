import pytest
from deps_core.auth.deps_auth import AUTH_HEADER, JWT_PREFIX

from deps_ocr_engines.infrastructure.access_management.context_vars import (
    user as user_context_var,
)


@pytest.fixture
def test_user():
    return {"subject": "some_user_id", "groups": ["deps-users"], "token": "token", "roles": ["test"]}


@pytest.fixture
def set_test_user(test_user):
    user_context_var.set(test_user)


@pytest.mark.usefixtures("enable_authorization_for_app", "set_test_user")
def test_set_auth_token__auth_enabled__auth_token_is_set(storage_service, test_user, requests_mock, settings):
    file_name = "some_file.png"
    download_url = f"{settings.file_storage_url}/{file_name}"

    requests_mock.get(download_url, status_code=200)
    storage_service.set_user_context(user_context_var)
    storage_service.download_content(file_name)

    request_headers = requests_mock.request_history[0].headers
    assert request_headers[AUTH_HEADER] == f"{JWT_PREFIX}{test_user['token']}"


def test_set_auth_token__auth_disabled__auth_header_not_set(storage_service, requests_mock, settings):
    file_name = "some_file.png"
    download_url = f"{settings.file_storage_url}/{file_name}"

    requests_mock.get(download_url, status_code=200)
    storage_service.download_content(file_name)

    request_headers = requests_mock.request_history[0].headers
    assert AUTH_HEADER not in request_headers
