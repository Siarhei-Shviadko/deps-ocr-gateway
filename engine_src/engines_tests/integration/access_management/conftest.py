import pytest
from deps_core.settings import Settings

from deps_ocr_engines.entrypoint import register_auth


@pytest.fixture
def enable_authorization_for_app(app, containers):
    containers.config.authentication.enabled.override(True)
    register_auth(app)
    yield

    containers.config.authentication.enabled.override(False)


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def storage_service(containers):
    storage = containers.storage_service
    storage.reset()
    yield storage()
