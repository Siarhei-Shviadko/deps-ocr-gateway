import io
import logging
import time
from typing import List, Tuple

import cv2
import numpy as np
from PIL import Image
from tesserocr import RIL, PyResultIterator, PyTessBaseAPI, iterate_level

from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)
from deps_ocr_engines.domain.exceptions import OCRError
from deps_ocr_engines.domain.interfaces import IOCREngine
from deps_ocr_engines.domain.utils import ocr_utils

from .settings import TesseractSettings

logger = logging.getLogger(__name__)


class TesseractOCR(IOCREngine):
    LEVEL = RIL.WORD
    BORDER_PERCENT = 0.05

    def __init__(self, lang: str, config: TesseractSettings = TesseractSettings()):
        """
        TesseractOCR is designed for batch image processing.
        :param lang: language code(s) to init Tesseract
        :param config: tesseract specific init settings like like psm and oem, etc.
        """
        self._language: str = lang
        self._config: TesseractSettings = config

    def set_config(self, config: TesseractSettings) -> None:  # type: ignore  # noqa: WPS615
        self._config = config

    def set_language(self, language: str) -> None:  # noqa: WPS615
        self._language = language

    def extract_text(self, image_content: io.BytesIO) -> List[TextLineEntity]:
        """
        Extracts text from provided image using Tesseract

        :param image_content: A bytes-like object.
        :return: list of found lines of text with bounding boxes per each word
        """

        try:
            with PyTessBaseAPI(  # noqa: WPS316
                lang=self._language,
                oem=self._config.oem.code,
                psm=self._config.psm.code,
            ) as api, Image.open(image_content) as image:
                logger.info("Extracting text using Tesseract")
                start = time.time()
                image = self._convert_mode(image)
                image_size = image.size
                image, image_border = self._add_border(image)  # noqa: WPS440
                api.SetImage(image)
                api.SetSourceResolution(70)  # noqa: WPS432
                api.Recognize()
                result = self._process_ocr_data(api.GetIterator(), image_size, image_border)
                logger.info(f"Extracted text using Tesseract {round(time.time() - start, 4)} seconds")
        except Exception as e:
            raise OCRError(f"Error extracting text: {e}")

        return result

    @classmethod
    def _add_border(
        cls,
        image: Image.Image,
        border_percent: float = BORDER_PERCENT,
    ) -> Tuple[Image.Image, Tuple[int, int]]:
        image_np_array = np.array(image)
        border_color = cls._calculate_border_color(image_np_array)
        vertical_border = int(border_percent * image_np_array.shape[0])
        horizontal_border = int(border_percent * image_np_array.shape[1])
        image_np_array = cv2.copyMakeBorder(
            image_np_array,
            vertical_border,
            vertical_border,
            horizontal_border,
            horizontal_border,
            cv2.BORDER_CONSTANT,
            value=[border_color, border_color, border_color],
        )
        image = Image.fromarray(image_np_array)
        return image, (horizontal_border, vertical_border)

    @staticmethod
    def _convert_mode(image: Image.Image) -> Image.Image:
        """Converts image from one mode to another to improve extraction quality"""
        if image.mode == "P":
            logger.info("Image mode was changed from P to RGB")
            return image.convert("RGB")
        elif image.mode == "PA":
            logger.info("Image mode was changed from PA to RGBA")
            return image.convert("RGBA")
        return image

    @staticmethod
    def _calculate_border_color(image: np.ndarray) -> int:
        return int(np.mean(image))

    def _process_ocr_data(  # noqa: WPS210 - should be removed after refactoring
        self,
        ri: PyResultIterator,
        image_size: Tuple[int, int],
        image_border: Tuple[int, int],
    ) -> List[TextLineEntity]:
        line_num = 0
        text_lines: List[TextLineEntity] = []
        word_boxes: List[WordBoxEntity] = []
        horizontal_border, vertical_border = image_border
        image_width, image_height = image_size

        for ri in iterate_level(ri, self.LEVEL):  # noqa: WPS440
            if ri.IsAtBeginningOf(RIL.TEXTLINE):  # new line started
                if line_num:
                    text_lines.append(TextLineEntity(line_num, word_boxes))
                line_num += 1
                word_boxes = []
            bbox = ri.BoundingBox(self.LEVEL)
            if bbox is not None:
                ocr_result = ocr_utils.to_ascii(ri.GetUTF8Text(self.LEVEL))
                if self._filter_out_wrong_bbox(bbox, image_width, image_height, horizontal_border, vertical_border):
                    logger.info(f"Content with wrong bounding box was excluded, content: {ocr_result}, bbox: {bbox}")
                    continue

                # get absolute coordinates without border
                bbox = (
                    bbox[0] - horizontal_border,
                    bbox[1] - vertical_border,
                    bbox[2] - horizontal_border,
                    bbox[3] - vertical_border,
                )

                # check if coordinates are outside of original image (without borders)
                if not (
                    0 <= bbox[0] < bbox[2] <= image_width and 0 <= bbox[1] < bbox[3] <= image_height  # noqa: WPS221
                ):
                    # use boundary values for coordinates
                    bbox = (
                        max(0, bbox[0]),
                        max(0, bbox[1]),
                        min(image_width, bbox[2]),
                        min(image_height, bbox[3]),
                    )

                # calculate bbox width and height
                bbox_left_x = bbox[0]
                bbox_width = bbox[2] - bbox_left_x
                bbox_top_y = bbox[1]
                bbox_height = bbox[3] - bbox_top_y

                # convert absolute coordinates to relative
                bbox_entity = BboxEntity(
                    x=bbox_left_x / image_width,
                    y=bbox_top_y / image_height,
                    w=bbox_width / image_width,
                    h=bbox_height / image_height,
                )
                word = WordBoxEntity(ocr_result, bbox_entity, ri.Confidence(self.LEVEL) / 100)
                word_boxes.append(word)

        if word_boxes:
            text_lines.append(TextLineEntity(line_num, word_boxes))

        return self._delete_full_image_and_empty_boxes(text_lines)

    @staticmethod
    def _filter_out_wrong_bbox(
        bbox: Tuple[int, int, int, int],
        image_width: int,
        image_height: int,
        horizontal_border: int,
        vertical_border: int,
    ) -> bool:
        """Filters out wrong calculated Tesseract bounding boxes"""
        return not (
            0 <= bbox[0] < bbox[2] <= image_width + 2 * horizontal_border  # noqa: WPS228
            and 0 <= bbox[1] < bbox[3] <= image_height + 2 * vertical_border  # noqa: WPS228
        )

    @staticmethod
    def _delete_full_image_and_empty_boxes(
        text_lines: List[TextLineEntity],
    ) -> List[TextLineEntity]:
        """Filter boxes with empty content and boxes which coordinates are whole image"""

        def _full_image_box(box: BboxEntity):  # noqa: WPS430
            return box.x == 0 and box.y == 0 and box.w == 1 and box.h == 1

        line_num = 0
        new_lines = []
        # do not delete full image size box if Tesseract used for small area OCR
        delete_full_image_size_boxes = False
        total_boxes = sum([len(line.word_boxes) for line in text_lines])
        if total_boxes > 1:
            delete_full_image_size_boxes = True

        for line in text_lines:
            word_boxes = [box for box in line.word_boxes if box.content.strip()]
            if delete_full_image_size_boxes:
                word_boxes = [box for box in word_boxes if not _full_image_box(box.bbox)]
            if word_boxes:
                new_lines.append(TextLineEntity(id=line_num, word_boxes=word_boxes))
                line_num += 1

        return new_lines
