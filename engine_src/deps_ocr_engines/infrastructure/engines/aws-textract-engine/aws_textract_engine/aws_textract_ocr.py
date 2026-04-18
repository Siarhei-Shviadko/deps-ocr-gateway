import io
import logging
from itertools import chain
from typing import List

import boto3

from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)
from deps_ocr_engines.domain.interfaces import IOCREngine

_loger = logging.getLogger(__name__)


class AWSTextractOCR(IOCREngine):
    def __init__(self, aws_region_name: str, aws_access_key_id: str, aws_secret_access_key: str):
        self._region = aws_region_name
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client(
                "textract",
                region_name=self._region,
                aws_access_key_id=self._aws_access_key_id,
                aws_secret_access_key=self._aws_secret_access_key,
            )

        return self._client

    def extract_text(self, image_data: io.BytesIO) -> List[TextLineEntity]:  # noqa: WPS210
        _loger.info("Extracting image using AWS Textract")
        ocr_response = self.client.detect_document_text(Document={"Bytes": image_data.getvalue()})

        text_lines = []
        lines = [block for block in ocr_response["Blocks"] if block["BlockType"] == "LINE"]
        words = {i["Id"]: i for i in ocr_response["Blocks"] if i["BlockType"] == "WORD"}
        for line_num, line in enumerate(lines):
            wordboxes = []

            word_ids = chain.from_iterable(
                relation["Ids"] for relation in line["Relationships"] if relation["Type"] == "CHILD"
            )
            for word_id in word_ids:
                word = words.get(word_id)
                if not word:
                    continue

                left = word["Geometry"]["BoundingBox"]["Left"]
                top = word["Geometry"]["BoundingBox"]["Top"]
                width = word["Geometry"]["BoundingBox"]["Width"]
                height = word["Geometry"]["BoundingBox"]["Height"]
                text = word["Text"]
                confidence = word["Confidence"] / 100

                bbox = BboxEntity(
                    y=top,
                    x=left,
                    w=width,
                    h=height,
                )

                wordbox = WordBoxEntity(content=text, bbox=bbox, confidence=confidence)

                wordboxes.append(wordbox)

            text_lines.append(TextLineEntity(id=line_num, word_boxes=wordboxes))

        return text_lines

    def set_config(self, config: OCREngineSettings) -> None:
        """Not required"""
        pass

    def set_language(self, language: str) -> None:
        """Not required"""
        pass
