from fastapi.testclient import TestClient

from position_service.main import app


client = TestClient(app)


def reset_state():
    from position_service.main import positions
    from position_service.main import seen_event_ids

    positions.clear()
    seen_event_ids.clear()


def test_buy_order():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-buy-1",
            "symbol": "RELIANCE",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 200

    response = client.get("/position")

    assert response.json() == {
        "RELIANCE": 100
    }


def test_sell_order():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-sell-1",
            "symbol": "TCS",
            "transaction_type": "SELL",
            "quantity": 75
        }
    )

    assert response.status_code == 200

    response = client.get("/position")

    assert response.json() == {
        "TCS": -75
    }


def test_multiple_symbols():
    reset_state()

    client.post(
        "/events",
        json={
            "event_id": "evt-1",
            "symbol": "RELIANCE",
            "transaction_type": "BUY",
            "quantity": 90
        }
    )

    client.post(
        "/events",
        json={
            "event_id": "evt-2",
            "symbol": "TCS",
            "transaction_type": "SELL",
            "quantity": 75
        }
    )

    client.post(
        "/events",
        json={
            "event_id": "evt-3",
            "symbol": "INFY",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    response = client.get("/position")

    assert response.json() == {
        "RELIANCE": 90,
        "TCS": -75,
        "INFY": 100
    }


def test_duplicate_event_is_ignored():
    reset_state()

    first = client.post(
        "/events",
        json={
            "event_id": "evt-duplicate",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert first.json()["status"] == "accepted"

    second = client.post(
        "/events",
        json={
            "event_id": "evt-duplicate",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 500
        }
    )

    assert second.json()["status"] == "duplicate"

    response = client.get("/position")

    assert response.json() == {
        "TCS": 100
    }


def test_zero_position():
    reset_state()

    client.post(
        "/events",
        json={
            "event_id": "evt-buy",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    client.post(
        "/events",
        json={
            "event_id": "evt-sell",
            "symbol": "TCS",
            "transaction_type": "SELL",
            "quantity": 100
        }
    )

    response = client.get("/position")

    assert response.json() == {
        "TCS": 0
    }


def test_negative_position():
    reset_state()

    client.post(
        "/events",
        json={
            "event_id": "evt-negative",
            "symbol": "TCS",
            "transaction_type": "SELL",
            "quantity": 200
        }
    )

    response = client.get("/position")

    assert response.json() == {
        "TCS": -200
    }


def test_invalid_transaction_type():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-invalid-type",
            "symbol": "TCS",
            "transaction_type": "INVALID",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_zero_quantity():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-zero",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 0
        }
    )

    assert response.status_code == 422


def test_negative_quantity():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-negative-quantity",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": -10
        }
    )

    assert response.status_code == 422


def test_non_integer_quantity():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-string-quantity",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": "100"
        }
    )

    assert response.status_code == 422


def test_blank_quantity():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-blank-quantity",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": ""
        }
    )

    assert response.status_code == 422


def test_blank_event_id():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_blank_symbol():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-blank-symbol",
            "symbol": "",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 422






def test_missing_event_id():
    reset_state()

    response = client.post(
        "/events",
        json={
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_missing_symbol():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-missing-symbol",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_missing_transaction_type():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-missing-type",
            "symbol": "TCS",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_missing_quantity():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-missing-quantity",
            "symbol": "TCS",
            "transaction_type": "BUY"
        }
    )

    assert response.status_code == 422


def test_extra_field_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-extra-field",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100,
            "price": 2500
        }
    )

    assert response.status_code == 422


def test_decimal_quantity_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-decimal",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 10.5
        }
    )

    assert response.status_code == 422


def test_null_quantity_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-null",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": None
        }
    )

    assert response.status_code == 422


def test_lowercase_transaction_type_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-lowercase",
            "symbol": "TCS",
            "transaction_type": "buy",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_transaction_type_with_space_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-space",
            "symbol": "TCS",
            "transaction_type": "BUY ",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_whitespace_event_id_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "   ",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_whitespace_symbol_is_rejected():
    reset_state()

    response = client.post(
        "/events",
        json={
            "event_id": "evt-whitespace-symbol",
            "symbol": "   ",
            "transaction_type": "BUY",
            "quantity": 100
        }
    )

    assert response.status_code == 422


def test_get_position_returns_200():
    reset_state()

    response = client.get("/position")

    assert response.status_code == 200
    assert response.json() == {}


def test_unknown_endpoint_returns_404():
    response = client.get("/does-not-exist")

    assert response.status_code == 404


def test_wrong_method_returns_405():
    response = client.put("/position")

    assert response.status_code == 405


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }

    def test_duplicate_event_with_different_quantity_is_ignored():
     reset_state()

    first = client.post(
        "/events",
        json={
            "event_id": "evt-idempotent-1",
            "symbol": "RELIANCE",
            "transaction_type": "BUY",
            "quantity": 100,
        },
    )

    assert first.status_code == 200
    assert first.json()["status"] == "accepted"

    second = client.post(
        "/events",
        json={
            "event_id": "evt-idempotent-1",
            "symbol": "RELIANCE",
            "transaction_type": "BUY",
            "quantity": 500,
        },
    )

    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"

    response = client.get("/position")

    assert response.json() == {
        "RELIANCE": 100
    }


def test_duplicate_event_with_different_symbol_is_ignored():
    reset_state()

    first = client.post(
        "/events",
        json={
            "event_id": "evt-idempotent-2",
            "symbol": "TCS",
            "transaction_type": "BUY",
            "quantity": 100,
        },
    )

    assert first.status_code == 200

    second = client.post(
        "/events",
        json={
            "event_id": "evt-idempotent-2",
            "symbol": "INFY",
            "transaction_type": "BUY",
            "quantity": 200,
        },
    )

    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"

    response = client.get("/position")

    assert response.json() == {
        "TCS": 100
    }