import csv
import logging
import time
import argparse
import httpx


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def validate_event(row):
    event_id = row.get("event_id")
    symbol = row.get("symbol")
    transaction_type = row.get("transaction_type")
    quantity_text = row.get("quantity")

    if event_id is None or not event_id.strip():
        return None, "event_id must not be blank"

    if symbol is None or not symbol.strip():
        return None, "symbol must not be blank"

    if transaction_type not in ("BUY", "SELL"):
        return None, "transaction_type must be exactly BUY or SELL"

    if quantity_text is None or not quantity_text.strip():
        return None, "quantity must not be blank"

    try:
        quantity = int(quantity_text)
    except (ValueError, TypeError):
        return None, "quantity must be an integer"

    if quantity <= 0:
        return None, "quantity must be positive"

    event = {
        "event_id": event_id,
        "symbol": symbol,
        "transaction_type": transaction_type,
        "quantity": quantity,
    }

    return event, None

def process_csv(file_path, service_url, rate):
    seen_event_ids = set()

    delay = 1 / rate

    logger.info("Starting CSV processing: %s", file_path)

    with open(file_path, newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            event, error = validate_event(row)

            if error:
                logger.warning(
                    "Rejected row: %s",
                    error
                )
                continue

            event_id = event["event_id"]

            if event_id in seen_event_ids:
                logger.info(
                    "Duplicate event ignored: %s",
                    event_id
                )
                continue

            seen_event_ids.add(event_id)

            logger.info(
                "Accepted event: %s",
                event_id
            )

            try:
                response = httpx.post(
                    f"{service_url}/events",
                    json=event,
                    timeout=5
                )

                response.raise_for_status()

                logger.info(
                    "Successfully sent event: %s",
                    event_id
                )

            except httpx.HTTPError as error:
                logger.error(
                    "Failed to send event %s: %s",
                    event_id,
                    error
                )

            time.sleep(delay)

    logger.info("Input processing complete")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        required=True
    )

    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000"
    )

    parser.add_argument(
        "--rate",
        type=float,
        default=50
    )

    args = parser.parse_args()

    process_csv(
        args.file,
        args.url,
        args.rate
    )


if __name__ == "__main__":
    main()
