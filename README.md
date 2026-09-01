# Order Position Processing System

A Python-based order processing and position management system built with **FastAPI, Pydantic, HTTPX, Pytest, Docker, and GitHub Actions**.

The system reads order events from a CSV file, validates them, sends valid events to a Position Service through an HTTP API, and maintains the current position for each stock symbol.

The project follows a **microservice-style architecture** with automated unit testing, integration testing, Docker containerization, health checks, and CI.

---

## Features

- CSV-based order event processing
- BUY and SELL transaction support
- Input validation
- Positive integer quantity validation
- Duplicate event detection
- Thread-safe position updates
- REST API using FastAPI
- HTTP error handling
- Health check endpoint
- Unit testing
- Integration testing
- API validation testing
- Negative testing
- Edge-case testing
- Docker containerization
- Docker health checks
- Docker Compose service dependency
- GitHub Actions CI
- 99% test coverage

---

## Architecture

```text
                    CSV File
                       |
                       v
              +------------------+
              |  Order Service   |
              |                  |
              | - Read CSV       |
              | - Validate data  |
              | - Detect         |
              |   duplicates     |
              +--------+---------+
                       |
                       | HTTP POST /events
                       |
                       v
              +------------------+
              | Position Service |
              |                  |
              | - Validate event |
              | - Update         |
              |   positions      |
              | - Ignore         |
              |   duplicates     |
              +--------+---------+
                       |
                       | GET /position
                       |
                       v
                Current Positions