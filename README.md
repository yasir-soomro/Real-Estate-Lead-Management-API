# Real Estate Lead Management API

A small FastAPI service for managing real-estate leads. Lead data is stored in memory and is available only while the application process is running.

## Features

- Health check at `GET /health`
- Create, list, retrieve, partially update, and delete leads
- Case-insensitive city filtering and bounded list limits
- Pydantic request validation and duplicate-phone detection
- App-scoped in-memory storage with no database dependency

## Technology

- Python 3.13 or newer
- FastAPI and Pydantic
- Uvicorn, included through `fastapi[standard]`
- `uv` for dependency and project management
- Python `unittest` and FastAPI's test client

## Setup and Run

Install [uv](https://docs.astral.sh/uv/) and Python 3.13+, then run:

```shell
uv sync
uv run real-estate-lead-api
```

By default, the API listens at `http://127.0.0.1:8000`.

## Configuration

Settings are read from environment variables:

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `Real Estate Lead API` | FastAPI application title |
| `DEBUG` | `false` | Enables FastAPI debug mode and Uvicorn reload for `1`, `true`, `yes`, or `on` (case-insensitive) |
| `HOST` | `127.0.0.1` | Uvicorn bind address |
| `PORT` | `8000` | Uvicorn port; must be an integer |

For example, in PowerShell:

```powershell
$env:HOST = "0.0.0.0"
$env:PORT = "8080"
uv run real-estate-lead-api
```

## API

All lead request and response bodies are JSON. Lead records have an auto-generated integer `id`, required non-empty `name`, `phone`, and `city`, a positive integer `budget` in PKR, and a `status` of `new`, `contacted`, or `qualified` (`new` by default). Unknown request fields are rejected.

| Method and path | Behavior | Success |
|---|---|---|
| `GET /health` | Check that the API is running | `200`, `{"status":"ok"}` |
| `POST /leads/` | Create a lead | `201`, created lead |
| `GET /leads/` | List leads; optional `city` filter is case-insensitive; `limit` is 1–100 and defaults to 10 | `200`, lead array |
| `GET /leads/{lead_id}` | Retrieve a lead by integer ID | `200`, lead |
| `PATCH /leads/{lead_id}` | Partially update a lead; empty updates and `null` field values are invalid | `200`, updated lead |
| `DELETE /leads/{lead_id}` | Delete a lead | `204`, empty body |

Validation errors return `422`. Unknown lead IDs return `404`. A phone value that duplicates another lead's phone after surrounding whitespace is trimmed returns `409` on create or update.

Create a lead:

```shell
curl -X POST http://127.0.0.1:8000/leads/ \
	-H "Content-Type: application/json" \
	-d '{"name":"Amina Khan","phone":"+923001234567","city":"Karachi","budget":15000000}'
```

Filter leads by city and limit the result:

```shell
curl "http://127.0.0.1:8000/leads/?city=karachi&limit=10"
```

## Tests

Run the test suite with:

```shell
uv run python -m unittest discover -s tests -v
```

The tests cover settings, health behavior, lead schemas, in-memory repository and service behavior, dependencies, and lead API responses.

## Architecture and Storage

Routes handle HTTP details, Pydantic schemas validate API data, services coordinate lead operations, and the repository stores records in memory. Data survives requests handled by the same application process, but is lost when that process stops and is not shared between processes. This project does not currently use a database, authentication, or deployment configuration.
