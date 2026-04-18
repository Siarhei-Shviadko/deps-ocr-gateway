import io
import json
import logging
from typing import List, Optional

from google.cloud.vision import ImageAnnotatorClient
from google.cloud.vision_v1 import types
from google.oauth2.service_account import Credentials

from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.entities_v2 import TextLineEntity
from deps_ocr_engines.domain.exceptions import OCRError
from deps_ocr_engines.domain.interfaces import IOCREngine

from .gcp_vision_utils import process_response, validate_response_has_no_error

logger = logging.getLogger(__name__)


class GCPVisionOCR(IOCREngine):
    def __init__(self, auth_key: str):
        """
        param auth_key: string representation of service account key
        which should be used for authentication to Google Cloud.
        The service account must have enough permissions to invoke Cloud Vision
        """
        self._auth_key = auth_key
        self._ocr_client: Optional[ImageAnnotatorClient] = None

    def set_config(self, config: OCREngineSettings) -> None:
        pass

    def set_language(self, language: str) -> None:
        pass

    def extract_text(self, image_content: io.BytesIO) -> List[TextLineEntity]:
        """
        Extracts text from provided image using Google Cloud Vision

        :param image_content: A bytes-like object.
         The bytes-like object must implement `seek` and `read` methods
        :return: list of found lines of text with bounding boxes per each word
        """
        if self._ocr_client is None:
            self._ocr_client = self._create_client()
        try:
            image_content.seek(0, 0)
            image = types.Image(content=image_content.read())
            logger.info("Extracting text using Cloud Vision")
            response = self._ocr_client.document_text_detection(image=image)
            validate_response_has_no_error(response)
            return process_response(response, image_content)
        except OCRError:  # noqa: WPS329
            raise
        except Exception as e:
            raise OCRError(f"Error extracting text by Cloud Vision: {e}")

    def _create_client(self) -> ImageAnnotatorClient:
        try:
            json_data = json.loads(self._auth_key)
        except json.JSONDecodeError:
            raise OCRError("Authorization key for GCP Vision engine is invalid or missing")
        credentials = Credentials.from_service_account_info(json_data)
        return ImageAnnotatorClient(credentials=credentials)
