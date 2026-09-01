FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY order_service ./order_service
COPY data ./data

CMD ["python", "-m", "order_service.main"]