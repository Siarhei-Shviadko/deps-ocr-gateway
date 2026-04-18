# type: ignore
import os

import pytest

from deps_ocr_engines.infrastructure.engines import *


@pytest.fixture(scope="module", autouse=True)
def ocr_config():
    yield {
        "EMPTY_IMAGE_PATH": os.path.join("engines_tests", "data", "empty_image.jpg"),
        "TEST_IMAGE_PATH": os.path.join("engines_tests", "data", "passport_image.jpg"),
    }


@pytest.fixture(scope="module", autouse=False)
def gcpvision_ocr_engine(settings):
    ocr_engine = EngineFactory.get_engine()(auth_key=settings.engine.gcp_vision_auth_key)
    yield ocr_engine


@pytest.fixture(scope="module", autouse=False)
def tesseract_ocr_engine(settings):
    ocr_engine = EngineFactory.get_engine()(lang=settings.engine.default_language)
    yield ocr_engine
