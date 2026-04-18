import io
import unicodedata
from typing import List

from PIL import Image

from deps_ocr_engines.domain.entities import Point, Rectangle, TextLine, WordBox
from deps_ocr_engines.domain.entities_v2 import TextLineEntity


def to_ascii(text: str) -> str:
    return unicodedata.normalize("NFKD", text)


def convert_relative_entities_to_absolute(
    image: io.BytesIO,
    relative_text_line_entities: List[TextLineEntity],
) -> List[TextLine]:
    image_obj = Image.open(image)
    image_width, image_height = image_obj.size

    return [
        TextLine(
            id=text_line.id,
            word_boxes=[
                WordBox(
                    content=word_box.content,
                    bbox=Rectangle(
                        left_top_point=Point(
                            int(word_box.bbox.x * image_width),
                            int(word_box.bbox.y * image_height),
                        ),
                        right_bottom_point=Point(
                            int((word_box.bbox.x + word_box.bbox.w) * image_width),
                            int((word_box.bbox.h + word_box.bbox.y) * image_height),
                        ),
                    ),
                    confidence=word_box.confidence,
                )
                for word_box in text_line.word_boxes
            ],
        )
        for text_line in relative_text_line_entities
    ]
