import pytest

from deps_ocr_engines.settings import Settings


@pytest.fixture(scope="module", autouse=True)
def settings():
    yield Settings()
