from operator import attrgetter
from statistics import mean
from typing import List, Tuple

from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)


def extract_area_text(textlines: List[TextLineEntity], area: BboxEntity) -> WordBoxEntity:
    intersected_words = _find_intersected_words(textlines, area)
    content, confidence = compose_text(intersected_words)
    return WordBoxEntity(content=content, bbox=area, confidence=confidence)


def extract_text(textlines: List[TextLineEntity]) -> WordBoxEntity:
    return extract_area_text(textlines, BboxEntity(x=0, y=0, h=1, w=1))


def compose_text(words: List[WordBoxEntity]) -> Tuple[str, float]:
    lines = []

    word_set = words[:]
    mean_confidence = 0
    while len(word_set):
        top_word = min(word_set, key=lambda word: word.bbox.centery)

        intersected_words = [word for word in word_set if _is_intersected_by_y(top_word.bbox, word.bbox)]
        intersected_words = sorted(intersected_words, key=lambda word: word.bbox.centerx)

        line = " ".join([word.content.strip() for word in intersected_words])
        mean_confidence = mean(
            map(attrgetter("confidence"), intersected_words),
        )
        lines.append(line)

        for intersected_word in intersected_words:
            word_set.remove(intersected_word)

    text = "\n".join(lines)

    return text, mean_confidence


def _find_intersected_words(textlines: List[TextLineEntity], area: BboxEntity) -> List[WordBoxEntity]:
    intersected_words = []
    for textline in textlines:
        for word in textline.word_boxes:
            if _is_intersected_by_box(area, word.bbox):
                intersected_words.append(word)
    return intersected_words


def _is_intersected_by_box(b1: BboxEntity, b2: BboxEntity, threshold: float = 0.6) -> bool:
    outer_inter = min(b1.h * b1.w, b2.h * b2.w)

    x_inter = max(0, min(b1.right, b2.right) - max(b1.left, b2.left))
    y_inter = max(0, min(b1.bottom, b2.bottom) - max(b1.top, b2.top))
    inner_inter = x_inter * y_inter

    if outer_inter == 0:
        return False

    intersect_ratio = inner_inter / outer_inter

    return intersect_ratio >= threshold


def _is_intersected_by_y(r1: BboxEntity, r2: BboxEntity, threshold: float = 0.6) -> bool:
    outer_inter = min(r1.h, r2.h)
    inner_inter = max(0, min(r1.bottom, r2.bottom) - max(r1.top, r2.top))

    if outer_inter == 0:
        return False

    intersect_ratio = inner_inter / outer_inter

    return intersect_ratio >= threshold
