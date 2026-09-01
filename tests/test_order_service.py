import csv
import httpx
from unittest.mock import patch

from order_service.main import validate_event, process_csv


def test_valid_row():
    row = {
        "event_id": "evt-001",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": "100",
    }

    event, error = validate_event(row)

    assert error is None
    assert event == {
        "event_id": "evt-001",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": 100,
    }


def test_invalid_transaction_type():
    row = {
        "event_id": "evt-002",
        "symbol": "TCS",
        "transaction_type": "INVALID",
        "quantity": "100",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "transaction_type must be exactly BUY or SELL"


def test_zero_quantity():
    row = {
        "event_id": "evt-003",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": "0",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "quantity must be positive"


def test_negative_quantity():
    row = {
        "event_id": "evt-004",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": "-10",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "quantity must be positive"


def test_blank_event_id():
    row = {
        "event_id": "",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": "100",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "event_id must not be blank"


def test_blank_symbol():
    row = {
        "event_id": "evt-005",
        "symbol": "",
        "transaction_type": "BUY",
        "quantity": "100",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "symbol must not be blank"


def test_blank_quantity():
    row = {
        "event_id": "evt-006",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": "",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "quantity must not be blank"


def test_non_integer_quantity():
    row = {
        "event_id": "evt-007",
        "symbol": "TCS",
        "transaction_type": "BUY",
        "quantity": "abc",
    }

    event, error = validate_event(row)

    assert event is None
    assert error == "quantity must be an integer"


    import csv
from unittest.mock import patch

from order_service.main import process_csv


def test_invalid_row_does_not_stop_processing(tmp_path):
    csv_file = tmp_path / "orders.csv"

    rows = [
        {
            "event_id": "evt-001",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": "100",
        },
        {
            "event_id": "evt-002",
            "symbol": "INFY",
            "transaction_type": "INVALID",
            "quantity": "200",
        },
        {
            "event_id": "evt-003",
            "symbol": "RELIANCE",
            "transaction_type": "BUY",
            "quantity": "50",
        },
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "event_id",
                "symbol",
                "transaction_type",
                "quantity",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    sent_events = []

    class MockResponse:
        def raise_for_status(self):
            pass

    def mock_post(url, json, timeout):
        sent_events.append(json)
        return MockResponse()

    with patch("order_service.main.httpx.post", side_effect=mock_post):
        process_csv(
            str(csv_file),
            "http://127.0.0.1:8000",
            rate=1000,
        )

    assert len(sent_events) == 2

    assert sent_events[0]["event_id"] == "evt-001"
    assert sent_events[1]["event_id"] == "evt-003"


def test_http_failure_does_not_stop_processing(tmp_path):
    csv_file = tmp_path / "orders.csv"

    rows = [
        {
            "event_id": "evt-001",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": "100",
        },
        {
            "event_id": "evt-002",
            "symbol": "INFY",
            "transaction_type": "BUY",
            "quantity": "200",
        },
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "event_id",
                "symbol",
                "transaction_type",
                "quantity",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    sent_events = []

    def mock_post(url, json, timeout):
        sent_events.append(json)

        raise httpx.ConnectError(
            "Position service unavailable"
        )

    with patch(
        "order_service.main.httpx.post",
        side_effect=mock_post,
    ):
        process_csv(
            str(csv_file),
            "http://127.0.0.1:8000",
            rate=1000,
        )

    assert len(sent_events) == 2
