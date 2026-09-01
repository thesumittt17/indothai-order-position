import httpx

from order_service.main import process_csv


def test_csv_to_position_service_integration():
    process_csv(
        "data/order_updates.csv",
        "http://127.0.0.1:8000",
        rate=1000,
    )

    response = httpx.get(
        "http://127.0.0.1:8000/position",
        timeout=5,
    )

    assert response.status_code == 200

    assert response.json() == {
        "RELIANCE": 50,
        "TCS": -50,
        "INFY": 100,
    }