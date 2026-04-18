import pytest
from starlette.testclient import TestClient

from deps_ocr_gateway.api.constants import OCREngineEnum
from deps_ocr_gateway.entrypoint import create_fastapi
from deps_ocr_gateway.infrastructure.context_vars import user

from .fakes import FakeDomainEventPublisher

PRIVILEGED_ORGANISATION = "deps-admins"


@pytest.fixture(scope="session")
def app():
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture
def containers(app):
    yield app.app


@pytest.fixture(autouse=True)
def disable_paid_engine_restriction(containers):
    with containers.config.paid_engines_restriction_enabled.override(False):
        yield


@pytest.fixture
def enable_paid_engine_restriction(containers):
    with containers.config.paid_engines_restriction_enabled.override(True):
        with containers.config.privileged_group.override(PRIVILEGED_ORGANISATION):
            yield


@pytest.fixture
def enable_only_tesseract_engine(containers):
    with containers.config.engines_settings.enabled_engines.override([OCREngineEnum.TESSERACT]):
        yield


@pytest.fixture
def this_user():
    return {
        "subject": "this_user",
        "organisation": "this_organisation",
        "deps_token": {"subject": "this_user", "organisation": "this_organisation"},
    }


@pytest.fixture
def super_user():
    return {
        "subject": "super_user",
        "organisation": PRIVILEGED_ORGANISATION,
        "roles": ["role"],
        "groups": ["group"],
    }


@pytest.fixture(autouse=True)
def set_this_user(this_user):
    user.set(this_user)


@pytest.fixture
def set_super_user(super_user):
    user.set(super_user)


@pytest.fixture()
def fake_domain_event_publisher(containers):
    with containers.domain_event_publishers.publisher.override(FakeDomainEventPublisher()) as dep:
        yield dep()
        del dep().last_published
