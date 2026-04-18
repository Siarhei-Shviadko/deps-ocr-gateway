from typing import Any

from deps_ocr_gateway.domain.entities_v2 import TextLineEntity

__all__ = ["map_textlines_to_ocr_data"]


def map_textlines_to_ocr_data(textlines: list[TextLineEntity], source_id: str) -> list[dict[str, Any]]:
    ocr_data = []
    for tl in textlines:
        word_boxes = []
        for wb in tl.word_boxes:
            word_boxes.append(
                {
                    "value": wb.content,
                    "confidence": wb.confidence,
                    "coordinates": {"x": wb.bbox.x, "y": wb.bbox.y, "w": wb.bbox.w, "h": wb.bbox.h},
                    "sourceId": source_id,
                },
            )
        ocr_data.append({"id": tl.id, "wordBoxes": word_boxes})

    return ocr_data
