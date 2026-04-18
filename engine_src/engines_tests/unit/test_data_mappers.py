import uuid
from dataclasses import asdict

from deps_ocr_engines.domain.utils.textlines_utils import (
    map_meta_textlines_to_entities,
    map_textlines_to_ocr_data,
)

from ..factories.text_line_v2 import TextLineFactory


def test_map_textlines_to_ocr_data__correct_ocr_data_returned():
    textlines = [TextLineFactory() for _ in range(5)]
    source_id = uuid.uuid4().hex

    ocr_data = map_textlines_to_ocr_data(textlines, source_id)

    for tl1, tl2 in zip(ocr_data, textlines):
        assert tl1["id"] == tl2.id
        for wb1, wb2 in zip(tl1["wordBoxes"], tl2.word_boxes):
            assert wb1["value"] == wb2.content
            assert wb1["confidence"] == wb2.confidence
            assert wb1["coordinates"] == {"x": wb2.bbox.x, "y": wb2.bbox.y, "w": wb2.bbox.w, "h": wb2.bbox.h}
            assert wb1["sourceId"] == source_id


def test_map_meta_textlines_to_entities(metadata_text_lines_v2):
    meta_textlines = [asdict(item) for item in metadata_text_lines_v2]
    result = map_meta_textlines_to_entities(meta_textlines)

    assert result == metadata_text_lines_v2
