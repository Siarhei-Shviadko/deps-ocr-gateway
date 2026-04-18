import pytest


def test_get__debug_page_for_sentry__return_ValueError(client):
    with pytest.raises(ValueError):
        client.get("/api/ocr/debug/500")


def test_healthcheck(client):
    response = client.get("/api/ocr/healthcheck")

    assert response.status_code == 200
