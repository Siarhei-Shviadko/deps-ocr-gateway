import os
from http import HTTPStatus

from deps_ocr_gateway.extras import (
    AbstractRESTClient,
    DEPSTokenAuth,
    FileStorageRequestError,
)
from deps_ocr_gateway.infrastructure import user

__all__ = ["FileStorageProxy"]


class FileStorageProxy(AbstractRESTClient):
    def download_content(self, file_path: str) -> bytes:
        response = self._session.get(
            self._get_url(file_path),
            timeout=60,
            verify=False,
        )
        if response.status_code != HTTPStatus.OK:
            raise FileStorageRequestError(response.content)

        return response.content

    def download_raw_metadata(self, file_path: str) -> bytes:
        metadata_path = self._get_metadata_path(file_path)

        try:
            metadata = self.download_content(metadata_path)
        except FileStorageRequestError:
            metadata = b"{}"  # noqa: P103

        return metadata

    def _get_url(self, file_path: str) -> str:
        return "/".join((self._base_url, file_path)).rstrip("/")

    @staticmethod
    def _get_metadata_path(file_path: str) -> str:
        dir_path, filename = os.path.split(file_path)
        filename, _ = os.path.splitext(filename)
        metadata_filename = "metadata_{0}.json".format(filename)

        return os.path.join(dir_path, metadata_filename)

    def _set_authentication(self) -> None:
        self._session.auth = DEPSTokenAuth(user)
