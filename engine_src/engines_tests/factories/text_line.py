import random

import factory.fuzzy
from faker import Faker
from pytest_factoryboy import register

from deps_ocr_engines.domain.entities import Point, Rectangle, TextLine, WordBox

fake = Faker()


@register
class PointFactory(factory.Factory):
    class Meta:
        model = Point

    x = factory.Faker("pyint")
    y = factory.Faker("pyint")


@register
class RectangleFactory(factory.Factory):
    class Meta:
        model = Rectangle

    left_top_point = factory.SubFactory(PointFactory)
    right_bottom_point = factory.SubFactory(PointFactory)


@register
class WordBoxFactory(factory.Factory):
    class Meta:
        model = WordBox

    content = factory.Faker("sentence", nb_words=10)
    bbox = factory.SubFactory(RectangleFactory)
    confidence = factory.Faker("pyfloat", min_value=0, max_value=1)


@register
class TextLineFactory(factory.Factory):
    class Meta:
        model = TextLine

    id = factory.LazyFunction(lambda: fake.pyint())
    word_boxes = factory.LazyFunction(lambda: [WordBoxFactory() for _ in range(random.randint(0, 5))])
