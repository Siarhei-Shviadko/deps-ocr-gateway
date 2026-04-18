from typing import Any, List

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_ocr_gateway.api.constants import OCREngineEnum
from deps_ocr_gateway.extras import ServiceInfoSettings

from .constants import API_PREFIX, PROJECT_DESCRIPTION, PROJECT_NAME, SWAGGER_DOC_URL

DEFAULT_PROXY_TIMEOUT: int = 60


class EnginesSettings(BaseSettings):
    tesseract_enabled: bool = False
    tesseract_url: str
    tesseract_timeout: int = DEFAULT_PROXY_TIMEOUT

    gcp_vision_enabled: bool = False
    gcp_vision_url: str
    gcp_vision_timeout: int = DEFAULT_PROXY_TIMEOUT

    aws_textract_enabled: bool = False
    aws_textract_url: str
    aws_textract_timeout: int = DEFAULT_PROXY_TIMEOUT

    azure_form_recognizer_enabled: bool = False
    azure_form_recognizer_url: str
    azure_form_recognizer_timeout: int = DEFAULT_PROXY_TIMEOUT

    enabled_engines: List[OCREngineEnum]
    verify_ssl: bool = True

    @model_validator(mode="before")
    @classmethod
    def gather_enabled_engines_list(cls, values: dict) -> dict:  # noqa: N805
        enabled_engines = []
        for field, value in values.items():
            if field.endswith("_enabled") and value == "true":
                enabled_engines.append(OCREngineEnum(field.replace("_enabled", "").upper()))

        values["enabled_engines"] = enabled_engines

        return values


class Settings(BaseSettings):
    env: str = "local"
    project_name: str = PROJECT_NAME
    description: str = PROJECT_DESCRIPTION
    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    version: str = Field(..., validation_alias="PROJECT_VERSION")
    api_prefix: str = API_PREFIX
    debug: bool = Field(False, validation_alias="DEBUG")
    swagger_doc_url: str = SWAGGER_DOC_URL
    info: ServiceInfoSettings = ServiceInfoSettings()
    documentation_enabled: bool = True
    messaging_driver: MessagingDriverEnum = Field(
        MessagingDriverEnum.RABBITMQ,
        validation_alias="MESSAGING_DRIVER",
    )
    messaging_driver_settings: Any = Field(
        None,
        validation_alias="MESSAGING_DRIVER_SETTINGS",
    )
    message_broker_connection_string: str
    engines_settings: EnginesSettings = EnginesSettings()
    paid_engines_restriction_enabled: bool = Field(True)
    privileged_group: str = Field("deps-admins")

    file_storage_url: str
    ocr_gateway_url: str

    model_config = SettingsConfigDict(use_enum_values=True)

    @field_validator("messaging_driver_settings")
    @classmethod
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
