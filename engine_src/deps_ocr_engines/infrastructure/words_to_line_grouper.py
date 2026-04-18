from dataclasses import dataclass
from typing import List

from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)


@dataclass
class _LineBboxEntity:
    x_min: float
    x_max: float
    y_center: float
    h: float
    textline: TextLineEntity


class TextLinesGrouper:
    ZERO_MARGIN = 0.0001

    def group_lines(
        self,
        textlines: List[TextLineEntity],
        ycenter_ths: float = 0.5,
        height_ths: float = 0.5,
        width_ths: float = 1.0,
        add_margin: float = 0.05,
        sort_output: bool = True,
    ) -> List[TextLineEntity]:
        textlines = self._group_text_box(textlines, ycenter_ths, height_ths, width_ths, add_margin, sort_output)
        return self._group_text_box(
            textlines,
            ycenter_ths - 0.1,
            height_ths - 0.1,
            width_ths,
            add_margin=0,
            sort_output=sort_output,
        )

    @classmethod
    def _add_margin_word_box(cls, word_box: WordBoxEntity, margin: float) -> WordBoxEntity:
        box = word_box.bbox
        x = max(0, box.x - margin)
        w = min(1.0, box.w + 2 * margin)
        y = max(0, box.y - margin)
        h = min(1.0, box.h + 2 * margin)
        return WordBoxEntity(
            content=word_box.content,
            bbox=BboxEntity(x=x, y=y, w=w, h=h),
            confidence=word_box.confidence,
        )

    @classmethod
    def _add_margin(cls, poly: TextLineEntity, margin: float) -> TextLineEntity:
        if margin < 0 or margin > 1:
            raise ValueError(f"margin should be between 0. and 1., actual value {margin}")
        if margin <= cls.ZERO_MARGIN:
            return poly
        word_boxes = [cls._add_margin_word_box(bbox, margin) for bbox in poly.word_boxes]
        return TextLineEntity(id=poly.id, word_boxes=word_boxes)

    def _textlines_to_linebboxes(self, textlines: List[TextLineEntity]) -> List[_LineBboxEntity]:
        horizontal_lines: List[_LineBboxEntity] = []
        for textline in textlines:
            x_min = min([i.bbox.x for i in textline.word_boxes])
            x_max = max([i.bbox.x + i.bbox.w for i in textline.word_boxes])
            y_min = min([i.bbox.y for i in textline.word_boxes])
            y_max = max([i.bbox.y + i.bbox.h for i in textline.word_boxes])
            horizontal_lines.append(
                _LineBboxEntity(
                    x_min=x_min,
                    x_max=x_max,
                    y_center=0.5 * (y_min + y_max),
                    h=y_max - y_min,
                    textline=textline,
                ),
            )
        return horizontal_lines

    def _combine_lines_by_ycenter_height(
        self,
        horizontal_lines: List[_LineBboxEntity],
        ycenter_ths: float = 0.5,
    ) -> List[List[_LineBboxEntity]]:
        # combine box
        combined_lines: List[List[_LineBboxEntity]] = []
        poly = horizontal_lines[0]
        b_height_sum = poly.h
        b_height_num = 1
        b_height_mean = b_height_sum
        b_ycenter_sum = poly.y_center
        b_ycenter_num = 1
        b_ycenter_mean = b_ycenter_sum
        new_box = [poly]
        for poly in horizontal_lines[1:]:  # noqa: WPS440
            # comparable height and comparable y_center level up to ths*height
            if abs(b_ycenter_mean - poly.y_center) < ycenter_ths * b_height_mean:
                b_height_sum += poly.h
                b_height_num += 1
                b_height_mean = b_height_sum / b_height_num
                b_ycenter_sum += poly.y_center
                b_ycenter_num += 1
                b_ycenter_mean = b_ycenter_sum / b_ycenter_num
                new_box.append(poly)
            else:
                combined_lines.append(new_box)
                b_height_sum = poly.h
                b_height_num = 1
                b_height_mean = b_height_sum
                b_ycenter_sum = poly.y_center
                b_ycenter_num = 1
                b_ycenter_mean = b_ycenter_sum
                new_box = [poly]
        combined_lines.append(new_box)

        return combined_lines

    def _combine_lines_by_height_xdistance(
        self,
        lines: List[_LineBboxEntity],
        height_ths: float = 0.5,
        width_ths: float = 0.5,
        ycenter_ths: float = 0.5,
    ) -> List[List[_LineBboxEntity]]:
        merged_lines: List[List[_LineBboxEntity]] = []
        box = lines[0]
        b_height_sum = box.h
        b_height_num = 1
        b_height_mean = b_height_sum
        b_ycenter_sum = box.y_center
        b_ycenter_num = 1
        b_ycenter_mean = b_ycenter_sum
        x_max = box.x_max
        new_box = [box]
        for box in lines[1:]:  # noqa: WPS440
            if (
                (  # noqa: WPS222
                    abs(b_height_mean - box.h) < height_ths * b_height_mean
                    or (abs(box.x_min - x_max) < width_ths * box.h and abs(b_height_mean - box.h) < b_height_mean)
                )
                and abs(b_ycenter_mean - box.y_center) < ycenter_ths * b_height_mean
                and abs(b_height_mean - box.h) < 3 * box.h
            ):
                # merge boxes
                b_height_sum += box.h
                b_height_num += 1
                b_height_mean = b_height_sum / b_height_num
                b_ycenter_sum += box.y_center
                b_ycenter_num += 1
                b_ycenter_mean = b_ycenter_sum / b_ycenter_num
                x_max = box.x_max
                new_box.append(box)
            else:
                merged_lines.append(new_box)
                b_height_sum = box.h
                b_height_num = 1
                b_height_mean = b_height_sum
                b_ycenter_sum = box.y_center
                b_ycenter_num = 1
                b_ycenter_mean = b_ycenter_sum
                x_max = box.x_max
                new_box = [box]
        merged_lines.append(new_box)

        return merged_lines

    def _group_text_box(
        self,
        textlines: List[TextLineEntity],
        ycenter_ths: float = 0.5,
        height_ths: float = 0.5,
        width_ths: float = 1.0,
        add_margin: float = 0.05,
        sort_output: bool = True,
    ) -> List[TextLineEntity]:
        if not textlines:
            return textlines

        horizontal_lines = self._textlines_to_linebboxes(textlines)
        if sort_output:
            horizontal_lines = sorted(horizontal_lines, key=lambda item: item.y_center)

        combined_lines = self._combine_lines_by_ycenter_height(horizontal_lines, ycenter_ths)

        merged_lines: List[TextLineEntity] = []
        # merge list use sort again
        for boxes in combined_lines:
            if len(boxes) == 1:
                # one box per line
                box = boxes[0]
                line = box.textline
                margin = add_margin * min(box.x_max - box.x_min, box.h)
                line = self._add_margin(line, margin)
                merged_lines.append(line)
            else:
                # multiple boxes per line
                boxes = sorted(boxes, key=lambda item: item.x_min)
                merged_box = self._combine_lines_by_height_xdistance(boxes, height_ths, width_ths, ycenter_ths)
                for mbox in merged_box:
                    if len(mbox) == 1:
                        # non adjacent box in same line
                        box = mbox[0]
                        line = box.textline
                        margin = add_margin * min(box.x_max - box.x_min, box.h)
                        line = self._add_margin(line, margin)
                        merged_lines.append(line)
                    else:
                        # adjacent box in same line
                        curr_mbox = []
                        for box in mbox:  # noqa: WPS519, WPS440
                            curr_mbox += box.textline.word_boxes
                        merged_lines.append(TextLineEntity(id=mbox[-1].textline.id, word_boxes=curr_mbox))

        if len(merged_lines) < len(textlines):
            merged_lines = [TextLineEntity(id=i + 1, word_boxes=line.word_boxes) for i, line in enumerate(merged_lines)]
        return merged_lines
