FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY position_service ./position_service

EXPOSE 8000

CMD ["uvicorn", "position_service.main:app", "--host", "0.0.0.0", "--port", "8000"]