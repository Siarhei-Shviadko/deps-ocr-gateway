import pytest

from deps_ocr_gateway.constants import DESTINATION
from deps_ocr_gateway.domain.events import OCRCompleted
from deps_ocr_gateway.extras import FileStorageRequestError
from deps_ocr_gateway.infrastructure import OcrGatewayRequestError
from deps_ocr_gateway.messaging.handlers import ocr_image_handler

OCR_RESPONSE = [
    {
        "id": 1,
        "wordBoxes": [
            {
                "bbox": {
                    "h": 0.011918951132300357,
                    "w": 0.06885521885521892,
                    "x": 0.6893602693602694,
                    "y": 0.01910607866507744,
                },
                "confidence": 1.0,
                "content": "Radisson",
            },
            {
                "bbox": {
                    "h": 0.011918951132300357,
                    "w": 0.026094276094276093,
                    "x": 0.7629292929292929,
                    "y": 0.01910607866507744,
                },
                "confidence": 1.0,
                "content": "Blu",
            },
        ],
    },
    {
        "id": 2,
        "wordBoxes": [
            {
                "bbox": {
                    "h": 0.011918951132300357,
                    "w": 0.04461279461279461,
                    "x": 0.6893602693602694,
                    "y": 0.035363528009535114,
                },
                "confidence": 1.0,
                "content": "Hotel",
            },
            {
                "bbox": {
                    "h": 0.011918951132300357,
                    "w": 0.09511784511784512,
                    "x": 0.7386868686868687,
                    "y": 0.035363528009535114,
                },
                "confidence": 1.0,
                "content": "Amsterdam",
            },
            {
                "bbox": {
                    "h": 0.011918951132300357,
                    "w": 0.05942760942760945,
                    "x": 0.8385185185185184,
                    "y": 0.035363528009535114,
                },
                "confidence": 1.0,
                "content": "Airport",
            },
        ],
    },
]

EXPECTED_OCR_DATA = [
    {
        "id": 1,
        "wordBoxes": [
            {
                "confidence": 1.0,
                "coordinates": {
                    "h": 0.011918951132300357,
                    "w": 0.06885521885521892,
                    "x": 0.6893602693602694,
                    "y": 0.01910607866507744,
                },
                "sourceId": "ae205e40bf5f495f93b601fecb203673",
                "value": "Radisson",
            },
            {
                "confidence": 1.0,
                "coordinates": {
                    "h": 0.011918951132300357,
                    "w": 0.026094276094276093,
                    "x": 0.7629292929292929,
                    "y": 0.01910607866507744,
                },
                "sourceId": "ae205e40bf5f495f93b601fecb203673",
                "value": "Blu",
            },
        ],
    },
    {
        "id": 2,
        "wordBoxes": [
            {
                "confidence": 1.0,
                "coordinates": {
                    "h": 0.011918951132300357,
                    "w": 0.04461279461279461,
                    "x": 0.6893602693602694,
                    "y": 0.035363528009535114,
                },
                "sourceId": "ae205e40bf5f495f93b601fecb203673",
                "value": "Hotel",
            },
            {
                "confidence": 1.0,
                "coordinates": {
                    "h": 0.011918951132300357,
                    "w": 0.09511784511784512,
                    "x": 0.7386868686868687,
                    "y": 0.035363528009535114,
                },
                "sourceId": "ae205e40bf5f495f93b601fecb203673",
                "value": "Amsterdam",
            },
            {
                "confidence": 1.0,
                "coordinates": {
                    "h": 0.011918951132300357,
                    "w": 0.05942760942760945,
                    "x": 0.8385185185185184,
                    "y": 0.035363528009535114,
                },
                "sourceId": "ae205e40bf5f495f93b601fecb203673",
                "value": "Airport",
            },
        ],
    },
]


def test_handler__success(ocr_image_command, success_requests_mock, fake_domain_event_publisher):
    ocr_image_handler(ocr_image_command)

    incoming_command = ocr_image_command.command

    res = fake_domain_event_publisher.last_published
    events = res.events
    outgoing_event = events[0]

    assert res.aggregate_type == DESTINATION
    assert len(events) == 1
    assert isinstance(outgoing_event, OCRCompleted)
    assert outgoing_event.document_id == incoming_command.document_id
    assert outgoing_event.source_id == incoming_command.source_id
    assert outgoing_event.file_path == incoming_command.file_path
    assert outgoing_event.extraction_params == incoming_command.extraction_params
    assert outgoing_event.identify_document == incoming_command.identify_document
    assert outgoing_event.extract_data == incoming_command.extract_data
    assert outgoing_event.document_type == incoming_command.document_type
    assert outgoing_event.ocr_data == EXPECTED_OCR_DATA


def test_handler__no_metadata__success(ocr_image_command, fake_domain_event_publisher, metadata_failure_requests_mock):
    ocr_image_handler(ocr_image_command)

    res = fake_domain_event_publisher.last_published
    events = res.events
    outgoing_event = events[0]

    assert len(events) == 1
    assert isinstance(outgoing_event, OCRCompleted)


def test_handler__ocr_gateway_failure__error(ocr_image_command, ocr_gateway_failure_requests_mock):
    with pytest.raises(OcrGatewayRequestError):
        ocr_image_handler(ocr_image_command)


def test_handler__file_storage_failure__error(ocr_image_command, file_storage_failure_requests_mock):
    with pytest.raises(FileStorageRequestError):
        ocr_image_handler(ocr_image_command)


def test_handler__all_engines_disabled__no_error(ocr_image_command, disable_all_engines, fake_domain_event_publisher):
    ocr_image_handler(ocr_image_command)

    assert fake_domain_event_publisher.last_published is None
