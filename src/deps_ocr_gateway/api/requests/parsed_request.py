import json
from typing import Any

from async_rest_client import Methods
from fastapi import Request
from starlette.datastructures import Headers

__all__ = ["ParsedRequest", "BodyParsedRequest", "FormParsedRequest", "FormParsedRequestV1"]


class ParsedRequest:
    def __init__(self, request: Request) -> None:
        self._request = request
        self.url = request.url.path

    @property
    def method(self) -> Methods:
        return Methods(self._request.method)

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: str) -> None:
        self._url = url

    @property
    def headers(self) -> Headers:
        return self._request.headers

    def change_url(self, current_prefix: str, new_prefix: str) -> "ParsedRequest":
        self.url = self.url.replace(current_prefix, new_prefix)
        return self

    async def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "query": self._request.url.query,
            "headers": self._request.headers,
        }


class BodyParsedRequest(ParsedRequest):
    @property
    async def json_data(self) -> dict[str, Any]:
        return json.loads(await self._request.body())

    @property
    async def engine(self) -> str:
        return (await self.json_data)["engine"]

    async def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "url": self.url,
            "query": self._request.url.query,
            "headers": self._request.headers,
            "data": await self._request.body(),
        }


class FormParsedRequest(ParsedRequest):
    @property
    async def form(self) -> dict[str, Any]:
        form_data = await self._request.form()
        return dict(form_data.items())

    @property
    async def engine(self) -> str:
        return (await self.form)["engine"]


class FormParsedRequestV1(FormParsedRequest):
    @property
    async def engine(self) -> str:
        query_params = dict(param.split("=") for param in self._request.url.query.split("&"))
        return query_params["engine"]
