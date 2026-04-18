import random

import pytest
from fastapi.testclient import TestClient
from pytest_factoryboy import register

from deps_ocr_engines.__main__ import create_fastapi
from engines_tests.factories.text_line import TextLineFactory
from engines_tests.factories.text_line_v2 import BboxFactory
from engines_tests.factories.text_line_v2 import TextLineFactory as TextLineFactory_v2
from engines_tests.factories.text_line_v2 import WordBoxFactory

register(TextLineFactory_v2, "text_line_v2")
register(TextLineFactory)


@pytest.fixture(scope="module")
def app():
    fastapi_app = create_fastapi()
    yield fastapi_app


@pytest.fixture(scope="module")
def containers(app):
    yield app.app


@pytest.fixture(scope="module")
def client(app):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="function")
def text_lines():
    return [TextLineFactory() for _ in range(random.randint(1, 5))]


@pytest.fixture(scope="function")
def text_lines_v2():
    return [TextLineFactory_v2() for _ in range(random.randint(1, 5))]


@pytest.fixture(autouse=True)
def disable_paid_engine_restriction(containers):
    with containers.config.engines.paid_engines_restriction_enabled.override(False):
        yield


@pytest.fixture
def regular_user():
    return {
        "subject": "regular",
        "roles": [],
        "groups": ["deps-users"],
        "token": "token",
        "email": "example@mail.com",
        "first_name": "John",
        "last_name": "Doe",
    }


@pytest.fixture
def privileged_user():
    return {
        "subject": "privileded",
        "roles": [],
        "groups": ["deps-admins"],
        "token": "token",
        "email": "example@mail.com",
        "first_name": "John",
        "last_name": "Doe",
    }


@pytest.fixture(scope="function")
def metadata_text_lines_v2():
    return [
        TextLineFactory_v2(
            id=22,
            word_boxes=[
                WordBoxFactory(
                    content="Hello",
                    bbox=BboxFactory(
                        x=0.11899155047761292,
                        y=0.07824268476980033,
                        w=0.27241095534893645,
                        h=0.05887408947434958,
                        page=1,
                    ),
                    confidence=1.0,
                ),
                WordBoxFactory(
                    content="World",
                    bbox=BboxFactory(
                        x=0.40820161194360555,
                        y=0.07824268476980033,
                        w=0.16469924029181984,
                        h=0.05887408947434958,
                        page=1,
                    ),
                    confidence=1.0,
                ),
            ],
        )
    ]


@pytest.fixture(scope="function")
def ocr_text_lines_v2():
    return [
        TextLineFactory_v2(
            id=0,
            word_boxes=[
                WordBoxFactory(
                    content="Helloo",
                    bbox=BboxFactory(
                        x=0.12338709677419354,
                        y=0.09290396124251923,
                        w=0.2661290322580645,
                        h=0.031917925334853235,
                        page=1,
                    ),
                    confidence=0.9241379547119141,
                ),
                WordBoxFactory(
                    content="World",
                    bbox=BboxFactory(
                        x=0.4104838709677419,
                        y=0.09233399829011114,
                        w=0.16129032258064516,
                        h=0.032487888287261325,
                        page=1,
                    ),
                    confidence=0.9250420379638672,
                ),
            ],
        ),
        TextLineFactory_v2(
            id=1,
            word_boxes=[
                WordBoxFactory(
                    content="!",
                    bbox=BboxFactory(
                        x=0.23830645161290323,
                        y=0.3977941176470588,
                        w=0.07056451612903226,
                        h=0.03235294117647059,
                        page=1,
                    ),
                    confidence=0.9258494567871094,
                )
            ],
        ),
    ]
