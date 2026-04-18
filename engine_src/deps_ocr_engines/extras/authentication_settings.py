from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings

__all__ = ["AuthenticationSettings"]


class AuthenticationSettings(BaseSettings):
    enabled: bool = Field(False, validation_alias="AUTH_ENABLED")
    verify_ssl: bool = Field(True, validation_alias="AUTH_VERIFY_SSL")
    certs_endpoint: Optional[str] = Field(None, validation_alias="AUTH_CERTS_ENDPOINT")
    encryption_algorithm: str = Field("RS256", validation_alias="AUTH_ENCRYPTION_ALGORITHM")
    api_key: Optional[str] = Field(None, validation_alias="API_KEY")

    @model_validator(mode="after")
    def validate_certs_endpoint_and_key(self) -> "AuthenticationSettings":
        if self.enabled and (self.certs_endpoint is None and self.api_key is None):
            raise ValueError(
                "Please provide OAUTH certificates endpoint via `AUTH_CERTS_ENDPOINT` or provide auth key via `API_KEY`"
            )
        return self
