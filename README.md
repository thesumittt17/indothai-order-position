\# Order Position Processing System



A Python-based order processing and position management system built with \*\*FastAPI\*\*, \*\*Pydantic\*\*, \*\*HTTPX\*\*, and \*\*Pytest\*\*.



The system reads order events from a CSV file, validates them, sends valid events to a Position Service through an HTTP API, and maintains the current position for each stock symbol.



\## Features



\* CSV-based order event processing

\* BUY and SELL transaction support

\* Input validation

\* Positive integer quantity validation

\* Duplicate event detection

\* Thread-safe position updates

\* REST API using FastAPI

\* HTTP error handling

\* Health check endpoint

\* Comprehensive automated testing

\* Integration testing

\* API validation and error testing



\## Architecture



```text

&#x20;               CSV File

&#x20;                  |

&#x20;                  v

&#x20;         +------------------+

&#x20;         |  Order Service   |

&#x20;         |                  |

&#x20;         | - Read CSV       |

&#x20;         | - Validate data  |

&#x20;         | - Detect         |

&#x20;         |   duplicates     |

&#x20;         +--------+---------+

&#x20;                  |

&#x20;                  | HTTP POST /events

&#x20;                  v

&#x20;         +------------------+

&#x20;         | Position Service |

&#x20;         |                  |

&#x20;         | - Validate event |

&#x20;         | - Update         |

&#x20;         |   positions      |

&#x20;         | - Ignore         |

&#x20;         |   duplicates     |

&#x20;         +--------+---------+

&#x20;                  |

&#x20;                  | GET /position

&#x20;                  v

&#x20;            Current Positions

```



\## Project Structure



```text

indothai-order-position/

│

├── order\_service/

│   ├── \_\_init\_\_.py

│   └── main.py

│

├── position\_service/

│   ├── \_\_init\_\_.py

│   └── main.py

│

├── tests/

│   ├── test\_order\_service.py

│   ├── test\_position\_service.py

│   └── test\_integration.py

│

├── data/

│   └── order\_updates.csv

│

├── conftest.py

├── pytest.ini

├── requirements.txt

├── .gitignore

└── README.md

```



\## Technologies



\* Python 3

\* FastAPI

\* Pydantic

\* Uvicorn

\* HTTPX

\* Pytest



\## Input Format



The CSV file contains:



```csv

event\_id,symbol,transaction\_type,quantity

evt-0001,RELIANCE,BUY,90

evt-0002,TCS,SELL,75

evt-0003,INFY,BUY,100

evt-0004,RELIANCE,SELL,40

evt-0005,TCS,BUY,25

```



\## Business Logic



For a BUY event:



```text

position = position + quantity

```



For a SELL event:



```text

position = position - quantity

```



For the sample input:



```text

RELIANCE = 90 - 40 = 50

TCS      = -75 + 25 = -50

INFY     = 100

```



Expected result:



```json

{

&#x20; "RELIANCE": 50,

&#x20; "TCS": -50,

&#x20; "INFY": 100

}

```



\## Running the Position Service



Activate the virtual environment:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



Start the FastAPI service:



```powershell

uvicorn position\_service.main:app --reload

```



The API will be available at:



```text

http://127.0.0.1:8000

```



Interactive API documentation:



```text

http://127.0.0.1:8000/docs

```



\## Running the Order Service



Keep the Position Service running in one terminal.



Open another terminal and activate the virtual environment:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



Run:



```powershell

python -m order\_service.main --file data\\order\_updates.csv --url http://127.0.0.1:8000 --rate 50

```



The Order Service will:



1\. Read the CSV file.

2\. Validate every row.

3\. Ignore invalid rows.

4\. Ignore duplicate event IDs.

5\. Send valid events to the Position Service.

6\. Continue processing if an HTTP request fails.



\## API Endpoints



\### POST `/events`



Receives an order event.



Example:



```json

{

&#x20; "event\_id": "evt-100",

&#x20; "symbol": "TCS",

&#x20; "transaction\_type": "BUY",

&#x20; "quantity": 100

}

```



Successful response:



```json

{

&#x20; "status": "accepted",

&#x20; "event\_id": "evt-100"

}

```



Duplicate response:



```json

{

&#x20; "status": "duplicate",

&#x20; "event\_id": "evt-100"

}

```



\### GET `/position`



Returns the current position for all symbols.



Example:



```json

{

&#x20; "RELIANCE": 50,

&#x20; "TCS": -50,

&#x20; "INFY": 100

}

```



\### GET `/health`



Returns the health status of the service.



\## Validation Rules



The Position Service rejects:



\* Missing event ID

\* Blank event ID

\* Whitespace-only event ID

\* Missing symbol

\* Blank symbol

\* Whitespace-only symbol

\* Missing transaction type

\* Invalid transaction type

\* Lowercase transaction type

\* Transaction type with extra spaces

\* Missing quantity

\* Null quantity

\* Decimal quantity

\* String quantity

\* Zero quantity

\* Negative quantity

\* Unexpected extra fields



Valid transaction types are:



```text

BUY

SELL

```



\## Duplicate Event Handling



Each event contains a unique `event\_id`.



If the same event ID is received again, the Position Service does not update the position a second time.



Example:



```text

First request:

evt-001 → BUY 100 TCS



Second request:

evt-001 → BUY 500 TCS

```



Only the first event affects the position.



Result:



```text

TCS = 100

```



\## Testing



Run the complete test suite:



```powershell

pytest -v

```



The project currently contains \*\*40 automated tests\*\* covering:



\* Order validation

\* Position calculations

\* BUY operations

\* SELL operations

\* Duplicate events

\* Invalid input

\* Missing fields

\* Extra fields

\* HTTP failures

\* Integration between services

\* Health check

\* HTTP 404 handling

\* HTTP 405 handling

\* HTTP 422 validation

\* Edge cases



Expected result:



```text

40 passed

```



\## Integration Test



The integration test verifies the complete flow:



```text

CSV

&#x20;↓

Order Service

&#x20;↓

HTTP POST /events

&#x20;↓

Position Service

&#x20;↓

GET /position

```



The expected final positions are:



```json

{

&#x20; "RELIANCE": 50,

&#x20; "TCS": -50,

&#x20; "INFY": 100

}

```



\## Purpose



This project demonstrates practical knowledge of:



\* REST APIs

\* Microservice-style architecture

\* Request validation

\* Exception handling

\* HTTP communication

\* CSV processing

\* Thread safety

\* Automated testing

\* Integration testing

\* API testing

\* Negative testing

\* Edge-case testing



It is designed as a practical backend and QA-oriented project demonstrating how a tester/engineer can validate both application behavior and service-to-service communication.



