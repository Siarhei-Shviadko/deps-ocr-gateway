import os


class TestServiceInfo:
    endpoint = "/api/ocr/service-info"

    def test_version(self, client):
        response = client.get(f"{self.endpoint}/version")
        data = response.json()

        assert response.status_code == 200
        assert data["buildTag"] == os.getenv("SERVICE_INFO_TAG")
        assert data["buildDate"] == os.getenv("SERVICE_INFO_DATE")
        assert data["commitHash"] == os.getenv("SERVICE_INFO_HASH")
