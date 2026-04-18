from typing import Tuple

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_ocr_engines.domain.constants import (
    API_PREFIX,
    OCR_DEFAULT_LANGUAGE,
    PROJECT_DESCRIPTION,
    PROJECT_NAME,
    SWAGGER_DOC_URL,
    OCREngineEnum,
)
from deps_ocr_engines.extras import (
    AuthenticationSettings,
    SentrySettings,
    ServiceInfoSettings,
)


class GunicornSettings(BaseSettings):
    bind: str = "0.0.0.0:8000"
    workers: int = Field(..., validation_alias="WORKERS")
    reload: bool = Field(False, validation_alias="RELOAD")
    log_level: str = Field("info", validation_alias="LOG_LEVEL")
    capture_output: bool = Field(True, validation_alias="CAPTURE_OUTPUT")
    worker_class: str = "uvicorn.workers.UvicornWorker"
    max_requests: int = Field(..., validation_alias="MAX_REQUESTS")
    timeout: int = Field(..., validation_alias="TIMEOUT")


class EngineSettings(BaseSettings):
    ocr_engine: OCREngineEnum = Field(OCREngineEnum.TESSERACT)
    paid_engines_restriction_enabled: bool = Field(True)
    preinit: bool = Field(True, validation_alias="OCR_ENGINES_PREINIT")
    enable_gpu: bool = Field(False, validation_alias="OCR_ENABLE_CUDA_GPU")
    default_language: str = OCR_DEFAULT_LANGUAGE
    gcp_vision_auth_key: str = Field("", validation_alias="GCP_VISION_AUTH_KEY")
    aws_region_name: str = Field("", validation_alias="AWS_REGION_NAME")
    aws_access_key_id: str = Field("", validation_alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field("", validation_alias="AWS_SECRET_ACCESS_KEY")
    azure_form_recognizer_api_url: str = Field("", validation_alias="AZURE_FORM_RECOGNIZER_API_URL")
    azure_form_recognizer_api_key: str = Field("", validation_alias="AZURE_FORM_RECOGNIZER_API_KEY")


class StorageSettings(BaseSettings):
    file_storage_url: str
    verify_ssl: bool = True

    model_config = SettingsConfigDict(case_sensitive=False)


class CORSSettings(BaseSettings):
    allow_origins: Tuple[str] = ("*",)
    allow_headers: Tuple[str] = ("*",)
    allow_methods: Tuple[str] = ("*",)

    model_config = SettingsConfigDict(env_prefix="CORS_")


class Settings(BaseSettings):
    env: str = "local"
    project_name: str = PROJECT_NAME
    description: str = PROJECT_DESCRIPTION
    version: str = Field(..., validation_alias="PROJECT_VERSION")
    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")
    api_prefix: str = API_PREFIX
    debug: bool = Field(False, validation_alias="DEBUG")
    swagger_doc_url: str = SWAGGER_DOC_URL
    engine: EngineSettings = EngineSettings()
    gunicorn: GunicornSettings = GunicornSettings()
    sentry: SentrySettings = SentrySettings()
    storage: StorageSettings = StorageSettings()
    cors: CORSSettings = CORSSettings()
    info: ServiceInfoSettings = ServiceInfoSettings()
    authentication: AuthenticationSettings = AuthenticationSettings()
    documentation_enabled: bool = True

    model_config = SettingsConfigDict(use_enum_values=True)
