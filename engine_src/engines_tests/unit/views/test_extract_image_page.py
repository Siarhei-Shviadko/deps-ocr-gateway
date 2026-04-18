import pytest

ENDPOINT = "/api/ocr/v2/extract-image-page"


@pytest.mark.extract_image_page
def test_extract_image_page__valid_body__return_200(client, application_mock):
    application_mock.extract_image_page.return_value = []
    response = client.post(
        ENDPOINT,
        json={"blobName": "test.png", "language": "deu"},
    )

    assert response.status_code == 200
    assert response.json() == {"textLines": []}
