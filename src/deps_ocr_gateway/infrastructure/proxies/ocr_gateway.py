from http import HTTPStatus

from deps_ocr_gateway.api.serializers.extract_text import TextLineModel
from deps_ocr_gateway.constants import API_PREFIX
from deps_ocr_gateway.domain.entities_v2 import TextLineEntity
from deps_ocr_gateway.extras import AbstractRESTClient, DEPSTokenAuth
from deps_ocr_gateway.infrastructure import user

from .exceptions import OcrGatewayRequestError

__all__ = ["OcrGatewayProxy"]


class OcrGatewayProxy(AbstractRESTClient):
    def extract_text(
        self,
        file: bytes,
        metadata: bytes,
        engine: str,
        language: str,
    ) -> list[TextLineEntity]:
        response = self._session.post(
            url=f"{self._base_url}{API_PREFIX}/v2/extract-text",
            data={"engine": engine, "language": language},
            files={"file": file, "metadata": metadata},
            timeout=60,
            verify=False,
        )
        if response.status_code != HTTPStatus.OK:
            raise OcrGatewayRequestError(response.content)

        return [TextLineModel(**text_line).to_domain() for text_line in response.json()]

    def _set_authentication(self) -> None:
        self._session.auth = DEPSTokenAuth(user)
