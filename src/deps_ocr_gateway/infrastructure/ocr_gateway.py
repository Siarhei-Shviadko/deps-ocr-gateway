import logging
from typing import Any

from aiohttp import FormData
from starlette.datastructures import UploadFile

from deps_ocr_gateway.api.constants import OCREngineEnum
from deps_ocr_gateway.api.requests import ParsedRequest
from deps_ocr_gateway.infrastructure.proxies import GenericRestClient

__all__ = ["OCRGateway"]


class OCRGateway:
    def __init__(
        self,
        proxies: dict[OCREngineEnum, GenericRestClient],
    ) -> None:
        self._proxies = proxies
        self._logger = logging.getLogger(self.__class__.__name__)

    async def proxy(self, request: ParsedRequest):
        return await (await self._get_client(request)).request(
            **await request.to_dict(),
        )

    async def proxy_form_data(self, request: ParsedRequest) -> dict[str, Any]:
        request_dict = await request.to_dict()
        request_dict["data"] = await self._prepare_form(await request.form)
        request_dict["headers"] = {
            "deps-token": request_dict["headers"]["deps-token"],
            "accept": "application/json",
        }

        return await (await self._get_client(request)).request(**request_dict)

    async def _prepare_form(self, form: dict[str, Any]) -> FormData:
        form_data = FormData()
        for k, v in form.items():
            if isinstance(v, UploadFile):
                form_data.add_field(
                    k,
                    await v.read(),
                    filename=v.filename,
                    content_type=v.content_type,
                )
            else:
                form_data.add_field(k, v)
        return form_data

    async def _get_client(self, request: ParsedRequest) -> GenericRestClient:
        if client := self._proxies.get(await request.engine):
            self._logger.debug(
                "Request will be proxied with client %s to the url: %s"
                % (
                    client.__class__.__name__,
                    client._client._client._base_url,
                ),
            )
            return client

        self._logger.error(
            "Can't find proxy for engine: %s. Available proxies: %s"
            % (await request.engine, [proxy.value for proxy in self._proxies]),
        )
        raise RuntimeError(
            f"Service with engine {await request.engine} is not in available proxies.",
        )
