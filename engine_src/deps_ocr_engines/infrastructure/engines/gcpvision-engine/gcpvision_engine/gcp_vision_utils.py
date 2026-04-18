import io
from typing import List

from google.cloud.vision_v1.types.text_annotation import Symbol, Word
from PIL import Image

from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)
from deps_ocr_engines.domain.exceptions import OCRError
from deps_ocr_engines.domain.utils import ocr_utils


def process_response(response, image_content) -> List[TextLineEntity]:
    text_lines: List[TextLineEntity] = []
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                word_boxes = []
                for word in paragraph.words:
                    word_bbox = get_word_bounding_box(word, image_content)
                    word_boxes.append(word_bbox)
                text_line = TextLineEntity(len(text_lines), word_boxes)
                text_lines.append(text_line)

    return text_lines


def get_word_bounding_box(word: Word, image_content: io.BytesIO) -> WordBoxEntity:
    def get_min_x(symbol: Symbol) -> float:
        return min(symbol.bounding_box.vertices, key=lambda vrtc: vrtc.x).x

    def get_max_x(symbol: Symbol) -> float:
        return max(symbol.bounding_box.vertices, key=lambda vrtc: vrtc.x).x

    def get_min_y(symbol: Symbol) -> float:
        return min(symbol.bounding_box.vertices, key=lambda vrtc: vrtc.y).y

    def get_max_y(symbol: Symbol) -> float:
        return max(symbol.bounding_box.vertices, key=lambda vrtc: vrtc.y).y

    word_text = "".join([symbol.text for symbol in word.symbols])
    ascii_text = ocr_utils.to_ascii(word_text)

    bbox_min_x = get_min_x(min(word.symbols, key=get_min_x))
    bbox_max_x = get_max_x(max(word.symbols, key=get_max_x))
    bbox_min_y = get_min_y(min(word.symbols, key=get_min_y))
    bbox_max_y = get_max_y(min(word.symbols, key=get_max_y))

    bbox_width = bbox_max_x - bbox_min_x
    bbox_height = bbox_max_y - bbox_min_y

    image_obj = Image.open(image_content)
    image_width, image_height = image_obj.size
    bounding_box = BboxEntity(
        x=bbox_min_x / image_width,
        y=bbox_min_y / image_height,
        w=bbox_width / image_width,
        h=bbox_height / image_height,
    )

    return WordBoxEntity(ascii_text, bounding_box, word.confidence)


def validate_response_has_no_error(response):
    if response.error is not None and len(response.error.message):
        msg = f"Error recognizing text by Cloud Vision: {response.error.message}"
        details = response.error.details
        if details is not None and len(details):
            msg += f" Details: {details}"  # noqa: WPS336
        raise OCRError(msg)
