import logging
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.publisher import DomainEventPublisher

from deps_ocr_gateway.api import check_permission
from deps_ocr_gateway.constants import DESTINATION
from deps_ocr_gateway.containers import Containers
from deps_ocr_gateway.domain.entities_v2 import TextLineEntity
from deps_ocr_gateway.domain.events import OCRCompleted, OCRImage
from deps_ocr_gateway.domain.utils import map_textlines_to_ocr_data
from deps_ocr_gateway.infrastructure import FileStorageProxy, OcrGatewayProxy

logger = logging.getLogger(__name__)


def complete_ocr(
    command_message: CommandMessage[OCRImage],
    response_textlines: list[TextLineEntity],
    publisher: DomainEventPublisher = Provide[Containers.domain_event_publishers.publisher],
) -> None:
    ocr_result = map_textlines_to_ocr_data(response_textlines, command_message.command.source_id)
    publisher.publish(
        DESTINATION,
        str(command_message.command.document_id),
        [
            OCRCompleted(
                document_id=command_message.command.document_id,
                source_id=command_message.command.source_id,
                file_path=command_message.command.file_path,
                extraction_params=command_message.command.extraction_params,
                ocr_data=ocr_result,
                document_type=command_message.command.document_type,
                identify_document=command_message.command.identify_document,
                extract_data=command_message.command.extract_data,
            ),
        ],
        headers={"ID": uuid4().hex},
    )


@inject
def ocr_image_handler(
    command_message: CommandMessage[OCRImage],
    file_storage: FileStorageProxy = Provide[Containers.external_services.storage_proxy],
    ocr_gateway: OcrGatewayProxy = Provide[Containers.external_services.ocr_gateway_proxy],
    enabled_engines: str = Provide[Containers.config.engines_settings.enabled_engines],
) -> None:
    extraction_params = command_message.command.extraction_params
    engine = extraction_params["ocr_engine"]
    if engine in enabled_engines:
        check_permission(engine)
        file = file_storage.download_content(file_path=command_message.command.file_path)
        raw_meta = file_storage.download_raw_metadata(file_path=command_message.command.file_path)

        textlines = ocr_gateway.extract_text(
            file=file,
            metadata=raw_meta,
            engine=engine,
            language=extraction_params["language"],
        )
        complete_ocr(command_message, textlines)
    else:
        logger.error(f"Engine {engine} is not enabled")
