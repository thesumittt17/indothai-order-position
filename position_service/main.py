from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, StrictInt, field_validator
from threading import Lock


app = FastAPI(title="Position Maintaining Service")

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


class OrderEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    symbol: str
    transaction_type: str
    quantity: StrictInt

    @field_validator("event_id", "symbol")
    @classmethod
    def validate_non_empty(cls, value):
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("transaction_type")
    @classmethod
    def validate_transaction_type(cls, value):
        if value not in ("BUY", "SELL"):
            raise ValueError("must be exactly BUY or SELL")
        return value

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, value):
        if value <= 0:
            raise ValueError("must be a positive integer")
        return value


positions = {}
seen_event_ids = set()

lock = Lock()


@app.post("/events")
def receive_event(event: OrderEvent):

    with lock:

        if event.event_id in seen_event_ids:
            return {
                "status": "duplicate",
                "event_id": event.event_id
            }

        seen_event_ids.add(event.event_id)

        if event.transaction_type == "BUY":
            positions[event.symbol] = (
                positions.get(event.symbol, 0) + event.quantity
            )

        else:
            positions[event.symbol] = (
                positions.get(event.symbol, 0) - event.quantity
            )

        return {
            "status": "accepted",
            "event_id": event.event_id
        }


@app.get("/position")
def get_positions():

    with lock:
        return positions.copy()