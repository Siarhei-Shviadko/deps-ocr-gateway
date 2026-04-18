from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["SentrySettings"]


class SentrySettings(BaseSettings):
    enabled: bool = False
    trace_enabled: bool = False
    dsn: Optional[str] = None
    traces_sample_rate: Optional[float] = 0

    model_config = SettingsConfigDict(env_prefix="SENTRY_", frozen=True)
