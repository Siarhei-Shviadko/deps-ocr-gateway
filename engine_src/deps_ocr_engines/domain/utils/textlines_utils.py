import copy
import itertools
from collections import namedtuple
from operator import attrgetter
from typing import Any, Dict, List, Set

from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)
from deps_ocr_engines.infrastructure.words_to_line_grouper import TextLinesGrouper

from .quad_tree import Point, QuadTreeNode, Rect

ImageSize = namedtuple("ImageSize", "width height")


def merge_textlines(
    textlines1: List[TextLineEntity],
    textlines2: List[TextLineEntity],
    image_size: ImageSize,
    iou_thresh: float = 0.2,
) -> List[TextLineEntity]:
    word_boxes1 = [word_box for line in textlines1 for word_box in line.word_boxes]
    word_boxes2 = [word_box for line in textlines2 for word_box in line.word_boxes]

    matched_indices_sets: List[Set[int]] = match_overlapping_word_boxes(
        word_boxes1,
        word_boxes2,
        image_size=image_size,
        iou_thresh=iou_thresh,
    )

    non_matched_words_indices = [i for i, matched_indices in enumerate(matched_indices_sets) if not matched_indices]
    word_boxes2.extend([word_boxes1[i] for i in non_matched_words_indices])

    return TextLinesGrouper().group_lines(
        [TextLineEntity(id=idx, word_boxes=[word_box]) for idx, word_box in enumerate(word_boxes2, 1)],
    )


def match_overlapping_word_boxes(
    word_boxes1: List[WordBoxEntity],
    word_boxes2: List[WordBoxEntity],
    image_size: ImageSize,
    iou_thresh: float = 0.2,
) -> List[Set[int]]:
    """
    Returns indices of bboxes from the second set that match according bboxes from the first set.
    Length of indices equal to length of first bboxes set. Unmatched bboxes have empty index set
    """
    bboxes1 = [word_box.bbox for word_box in word_boxes1]
    bboxes2 = [word_box.bbox for word_box in word_boxes2]

    boundary = Rect(image_size.width / 2, image_size.height / 2, image_size.width, image_size.height)

    indices1 = match_overlapping_bboxes_internal(bboxes1, bboxes2, boundary, iou_thresh)
    indices2 = match_overlapping_bboxes_internal(bboxes2, bboxes1, boundary, iou_thresh)

    for j, indices_group in enumerate(indices2):
        for i in indices_group:
            indices1[i].add(j)

    return indices1


def match_overlapping_bboxes_internal(
    bboxes1: List[BboxEntity],
    bboxes2: List[BboxEntity],
    boundary: Rect,
    iou_thresh: float,
) -> List[Set[int]]:
    """
    Returns indices of bboxes from the second set that have at least one point inside according bbox from the first set
    """
    indices: List[Set[int]] = [set() for _ in range(len(bboxes1))]
    qtree = QuadTreeNode(boundary, max_points=4)
    populate_qtree_with_bboxes(qtree, bboxes2)
    qtree_len = len(qtree)

    for bbox1_index, bbox1 in enumerate(bboxes1):
        bbox1_rect = Rect(bbox1.centerx, bbox1.centery, bbox1.w, bbox1.h)
        found_points: List[Point] = []
        qtree.find_points(region=bbox1_rect, found_points=found_points)
        overlapping_bboxes_indices = set()
        grouped_by_bbox_points = itertools.groupby(
            sorted(found_points, key=attrgetter("payload")),
            key=attrgetter("payload"),
        )

        for bbox2_index, bbox2_points in grouped_by_bbox_points:
            bbox2 = bboxes2[bbox2_index]
            bbox2_rect = Rect(bbox2.centerx, bbox2.centery, bbox2.w, bbox2.h)
            bbox_points_len = len(list(bbox2_points))

            if bbox_points_len == qtree_len // len(bboxes2) or bbox1_rect.get_iou_with(bbox2_rect) > iou_thresh:
                overlapping_bboxes_indices.add(bbox2_index)

        indices[bbox1_index] |= overlapping_bboxes_indices

    return indices


def populate_qtree_with_bboxes(qtree: QuadTreeNode, bboxes: List[BboxEntity]) -> None:
    for i, bbox in enumerate(bboxes):
        qtree.insert_point(Point(x=bbox.left, y=bbox.top, payload=i))
        qtree.insert_point(Point(x=bbox.right, y=bbox.bottom, payload=i))
        qtree.insert_point(Point(x=bbox.left, y=bbox.bottom, payload=i))
        qtree.insert_point(Point(x=bbox.right, y=bbox.top, payload=i))
        qtree.insert_point(Point(x=bbox.centerx, y=bbox.centery, payload=i))


def convert_textlines_area_to_image_coords(
    textlines: List[TextLineEntity],
    area: BboxEntity,
    image_size: ImageSize,
) -> List[TextLineEntity]:
    absolute_area_width = area.w * image_size.width
    absolute_area_height = area.h * image_size.height
    absolute_area_x = area.x * image_size.width
    absolute_area_y = area.y * image_size.height

    textlines = copy.deepcopy(textlines)

    for textline in textlines:
        for word_box in textline.word_boxes:
            word_box.bbox.y = (word_box.bbox.y * absolute_area_height + absolute_area_y) / image_size.height
            word_box.bbox.x = (word_box.bbox.x * absolute_area_width + absolute_area_x) / image_size.width
            word_box.bbox.w *= area.w
            word_box.bbox.h *= area.h

    return textlines


def map_textlines_to_ocr_data(textlines: List[TextLineEntity], source_id: str) -> List[Dict[str, Any]]:
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


def map_meta_textlines_to_entities(textlines: List[Dict[str, Any]]) -> List[TextLineEntity]:
    entities = []
    for textline in textlines:
        word_boxes = []
        for word_box in textline["word_boxes"]:
            d_bbox = word_box["bbox"]
            bbox = BboxEntity(x=d_bbox["x"], y=d_bbox["y"], w=d_bbox["w"], h=d_bbox["h"])
            wb_entity = WordBoxEntity(content=word_box["content"], bbox=bbox, confidence=word_box["confidence"])
            word_boxes.append(wb_entity)
        entity = TextLineEntity(id=textline["id"], word_boxes=word_boxes)
        entities.append(entity)
    return entities
