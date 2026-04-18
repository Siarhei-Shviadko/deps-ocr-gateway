from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_ocr_gateway.api.constants import OCREngineEnum
from deps_ocr_gateway.constants import ASB_SUBSCRIPTION_NAME
from deps_ocr_gateway.infrastructure import (
    AWSTextractProxy,
    AzureFormRecognizerProxy,
    FileStorageProxy,
    GCPVisionProxy,
    OCRGateway,
    OcrGatewayProxy,
    TesseractProxy,
)
from deps_ocr_gateway.messaging.dispatcher import make_message_dispatcher

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=ASB_SUBSCRIPTION_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class DomainEventPublishers(containers.DeclarativeContainer):
    messaging = providers.DependenciesContainer()

    publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )


class ExternalServices(containers.DeclarativeContainer):
    config = providers.Configuration()
    tesseract_proxy: providers.Singleton[TesseractProxy] = providers.Singleton(
        TesseractProxy,
        base_url=config.engines_settings.tesseract_url,
        timeout=config.engines_settings.tesseract_timeout,
        verify_ssl=config.engines_settings.verify_ssl,
    )
    aws_textract_proxy: providers.Singleton[AWSTextractProxy] = providers.Singleton(
        AWSTextractProxy,
        base_url=config.engines_settings.aws_textract_url,
        timeout=config.engines_settings.aws_textract_timeout,
        verify_ssl=config.engines_settings.verify_ssl,
    )
    gcp_vision_proxy: providers.Singleton[GCPVisionProxy] = providers.Singleton(
        GCPVisionProxy,
        base_url=config.engines_settings.gcp_vision_url,
        timeout=config.engines_settings.gcp_vision_timeout,
        verify_ssl=config.engines_settings.verify_ssl,
    )
    azure_proxy: providers.Singleton[AzureFormRecognizerProxy] = providers.Singleton(
        AzureFormRecognizerProxy,
        base_url=config.engines_settings.azure_form_recognizer_url,
        timeout=config.engines_settings.azure_form_recognizer_timeout,
        verify_ssl=config.engines_settings.verify_ssl,
    )
    storage_proxy: providers.Provider[FileStorageProxy] = providers.Singleton(
        FileStorageProxy,
        base_url=config.file_storage_url,
    )
    ocr_gateway_proxy: providers.Provider[OcrGatewayProxy] = providers.Singleton(
        OcrGatewayProxy,
        base_url=config.ocr_gateway_url,
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.info.tag,
            "build_date": config.info.date,
            "commit_hash": config.info.hash,
        },
    )


class Containers(containers.DeclarativeContainer):
    config = providers.Configuration()
    core: providers.Container[Core] = providers.Container(Core, config=config)
    messaging_driver_settings = providers.Dependency(instance_of=object)
    external_services: providers.Container[ExternalServices] = providers.Container(
        ExternalServices,
        config=config,
    )
    ocr_gateway: providers.Provider[OCRGateway] = providers.Factory(
        OCRGateway,
        proxies=providers.Dict(
            {
                OCREngineEnum.TESSERACT: external_services.tesseract_proxy,
                OCREngineEnum.AWS_TEXTRACT: external_services.aws_textract_proxy,
                OCREngineEnum.GCP_VISION: external_services.gcp_vision_proxy,
                OCREngineEnum.AZURE_FORM_RECOGNIZER: external_services.azure_proxy,
            },
        ),
    )
    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )
    messaging: providers.Container[Messaging] = providers.Container(
        Messaging,
        config=config,
        message_brokers=message_brokers,
    )
    dispatcher: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_message_dispatcher,
        messaging.consumer,
        messaging.producer,
    )
    domain_event_publishers: providers.Container[DomainEventPublishers] = providers.Container(
        DomainEventPublishers,
        messaging=messaging,
    )
