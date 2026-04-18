from enum import Enum

from tesserocr import OEM, PSM


class PageSegMode(Enum):
    OSD_ONLY = "OSD_ONLY"
    AUTO_OSD = "AUTO_OSD"
    AUTO_ONLY = "AUTO_ONLY"
    AUTO = "AUTO"
    SINGLE_COLUMN = "SINGLE_COLUMN"
    SINGLE_BLOCK_VERT_TEXT = "SINGLE_BLOCK_VERT_TEXT"
    SINGLE_BLOCK = "SINGLE_BLOCK"
    SINGLE_LINE = "SINGLE_LINE"
    SINGLE_WORD = "SINGLE_WORD"
    CIRCLE_WORD = "CIRCLE_WORD"
    SINGLE_CHAR = "SINGLE_CHAR"
    SPARSE_TEXT = "SPARSE_TEXT"
    SPARSE_TEXT_OSD = "SPARSE_TEXT_OSD"
    RAW_LINE = "RAW_LINE"
    COUNT = "COUNT"

    @property
    def code(self):
        return getattr(PSM, self.value)


class OCREngineMode(Enum):
    TESSERACT_ONLY = "TESSERACT_ONLY"
    LSTM_ONLY = "LSTM_ONLY"
    TESSERACT_LSTM_COMBINED = "TESSERACT_LSTM_COMBINED"
    DEFAULT = "DEFAULT"

    @property
    def code(self):
        return getattr(OEM, self.value)
