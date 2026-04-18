import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_ocr_gateway.constants import COMMANDS_DESTINATION, COMMANDS_QUEUE
from deps_ocr_gateway.domain.events import OCRImage

_logger = logging.getLogger(__name__)


def make_message_dispatcher(subscriber: IMessageConsumer, producer: IMessageProducer) -> IMessageConsumer:
    from deps_ocr_gateway.messaging.handlers import ocr_image_handler  # noqa: WPS433

    commands_handlers = (
        CommandHandlersBuilder.from_channel(COMMANDS_DESTINATION)
        .on_message(OCRImage, ocr_image_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    cd = CommandDispatcher(commands_handlers, subscriber, producer)
    cd.initialize()

    _logger.info("Start consuming...")

    return subscriber
