from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["ServiceInfoSettings"]


class ServiceInfoSettings(BaseSettings):
    tag: str = ""
    date: str = ""
    hash: str = ""

    model_config = SettingsConfigDict(env_prefix="SERVICE_INFO_")
