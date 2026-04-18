import random

import factory.fuzzy
from faker import Faker
from pytest_factoryboy import register

from deps_ocr_engines.domain.entities_v2 import (
    BboxEntity,
    TextLineEntity,
    WordBoxEntity,
)

fake = Faker()


@register
class BboxFactory(factory.Factory):
    class Meta:
        model = BboxEntity

    x = factory.Faker("pyfloat", min_value=0, max_value=1)
    y = factory.Faker("pyfloat", min_value=0, max_value=1)
    w = factory.Faker("pyfloat", min_value=0, max_value=1)
    h = factory.Faker("pyfloat", min_value=0, max_value=1)


@register
class WordBoxFactory(factory.Factory):
    class Meta:
        model = WordBoxEntity

    content = factory.Faker("sentence", nb_words=10)
    bbox = factory.SubFactory(BboxFactory)
    confidence = factory.Faker("pyfloat", min_value=0, max_value=1)


@register
class TextLineFactory(factory.Factory):
    class Meta:
        model = TextLineEntity

    id = factory.LazyFunction(lambda: fake.pyint())
    word_boxes = factory.LazyFunction(lambda: [WordBoxFactory() for _ in range(random.randint(1, 5))])
