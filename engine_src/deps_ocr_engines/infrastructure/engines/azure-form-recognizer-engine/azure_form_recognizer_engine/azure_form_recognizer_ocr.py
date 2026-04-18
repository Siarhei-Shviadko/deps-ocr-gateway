import io
import logging
from typing import Dict, List, Tuple

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (
    DocumentLine,
    DocumentPage,
    DocumentWord,
)
from azure.core.credentials import AzureKeyCredential

from deps_ocr_engines.domain.entities import OCREngineSettings
from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)
from deps_ocr_engines.domain.interfaces import IOCREngine

Span = Tuple[int, int]

_loger = logging.getLogger(__name__)


class AzureFormRecognizerOCR(IOCREngine):
    def __init__(
        self,
        azure_document_intelligence_api_url: str,
        azure_document_intelligence_api_key: str,
    ):
        self._azure_document_intelligence_api_url = azure_document_intelligence_api_url
        self._azure_document_intelligence_api_key = azure_document_intelligence_api_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = DocumentIntelligenceClient(
                self._azure_document_intelligence_api_url,
                AzureKeyCredential(self._azure_document_intelligence_api_key),
                api_version="2024-02-29-preview",
            )

        return self._client

    def extract_text(self, image_data: io.BytesIO) -> List[TextLineEntity]:
        _loger.info("Extracting image using Azure Form Recognizer")

        page = (
            self.client.begin_analyze_document(
                model_id="prebuilt-read",
                body=image_data,
            )
            .result()
            .pages[0]
        )

        return self._create_text_lines(page)

    def set_config(self, config: OCREngineSettings) -> None:
        """Not required"""
        pass

    def set_language(self, language: str) -> None:
        """Not required"""
        pass

    @classmethod
    def _create_text_lines(cls, page: DocumentPage) -> List[TextLineEntity]:
        if not page.lines:
            return []

        span2word = cls._span_to_word(page)
        text_lines = []
        for line_index, line in enumerate(page.lines):
            text_lines.append(
                TextLineEntity(
                    id=line_index,
                    word_boxes=cls._create_word_boxes(line, span2word, page.width, page.height),
                ),
            )

        return text_lines

    @classmethod
    def _span_to_word(cls, page: DocumentPage) -> Dict[Span, DocumentWord]:
        span2word = dict()
        for word in page.words:
            span2word[(word.span.offset, word.span.length)] = word
        return span2word

    @classmethod
    def _create_word_boxes(
        cls,
        line: DocumentLine,
        span2word: Dict[Span, DocumentWord],
        page_width: float,
        page_height: float,
    ) -> List[WordBoxEntity]:
        word_boxes = []

        content = line.content
        for span in line.spans:
            curr_content = content[: span.length]
            content = content[span.length:].strip()
            offset = span.offset

            for text_word in curr_content.split():
                word = span2word[(offset, len(text_word))]
                offset += len(text_word) + 1
                word_boxes.append(
                    WordBoxEntity(
                        bbox=cls._create_bbox(word.polygon, page_width, page_height),
                        confidence=word.confidence,
                        content=word.content,
                    ),
                )

        return word_boxes

    @classmethod
    def _create_bbox(cls, polygon: List[float], page_width: float, page_height: float) -> BboxEntity:
        xs = polygon[::2]
        ys = polygon[1::2]

        x_min, x_max = min(xs) / page_width, max(xs) / page_width
        y_min, y_max = min(ys) / page_height, max(ys) / page_height
        x_min, x_max = max(0.0, x_min), min(1.0, x_max)
        y_min, y_max = max(0.0, y_min), min(1.0, y_max)

        return BboxEntity(
            x=x_min,
            y=y_min,
            w=x_max - x_min,
            h=y_max - y_min,
        )
