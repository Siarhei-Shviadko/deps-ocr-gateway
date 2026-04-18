from io import BytesIO

from PIL import Image

from deps_ocr_engines.api.v2.serializers.extract_text import BboxModel


def crop_image(image: bytes, area: BboxModel) -> BytesIO:
    with BytesIO(image) as bytes_stream:
        with Image.open(bytes_stream) as img:
            width, height = img.size

            x = area.x * width
            y = area.y * height
            right = x + area.w * width
            bottom = y + area.h * height
            result = img.crop((x, y, right, bottom))
            img_byte_arr = BytesIO()
            result.save(img_byte_arr, format="PNG")
            img_byte_arr.seek(0)
    return img_byte_arr
