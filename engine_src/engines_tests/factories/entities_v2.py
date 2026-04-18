from random import randint

import factory
from pytest_factoryboy import register

from deps_ocr_engines.domain.entities_v2 import PdfImageMetaEntity
from engines_tests.factories.text_line_v2 import TextLineFactory


@register
class PdfImageMetaEntityFactory(factory.Factory):
    class Meta:
        model = PdfImageMetaEntity

    width = factory.Faker("pyint")
    height = factory.Faker("pyint")
    textlines_v2 = factory.LazyFunction(lambda: [TextLineFactory() for _ in range(randint(1, 5))])
