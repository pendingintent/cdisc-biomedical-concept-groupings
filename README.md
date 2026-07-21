# Biomedical Concept Grouping API

A FastAPI + OpenAPI service that provides full CRUD access to `bc_grouping.db`, a SQLite database of CDISC Biomedical Concepts (BCs) and the classification schemes used to group and filter them (e.g. Therapeutic Area, Collection Method, Concept Group, COA Type, Age Category, Implementation Domain Code).

See `bc-classification-grouping.md` / `.puml` for the ER diagram this schema is based on.

## Schema

- **`biomedical_concept`** — a BC (`bc_id`, `short_name`, `ncit_code`)
- **`bc_classification_scheme`** — a classification scheme (e.g. "Therapeutic Area"), with its purpose/intended use
- **`bc_classification_value`** — an allowed value within a scheme (e.g. "Oncology" under Therapeutic Area)
- **`bc_classification_assignment`** — links a BC to one classification value

## Requirements

- Python (a `.venv` is expected at the project root — create one with `python3 -m venv .venv` if it doesn't exist yet)
- Dependencies in `requirements.txt`: FastAPI, Uvicorn, SQLAlchemy, Pydantic, pytest, httpx

## Setup

```bash
cd Groupings
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

All runtime configuration lives in `config.ini` at the project root:

```ini
[server]
host = 127.0.0.1
port = 8900

[database]
; relative paths are resolved against this project's root directory
path = bc_grouping.db
```

| Section    | Key    | Description                                                                 |
|------------|--------|------------------------------------------------------------------------------|
| `server`   | `host` | Interface the API server binds to                                            |
| `server`   | `port` | TCP port the API server listens on                                           |
| `database` | `path` | Path to the SQLite `.db` file. Relative paths resolve against the project root |

Edit `config.ini` and restart the server to change the port, host, or database file — no code changes needed. `app/config.py` reads this file (with built-in fallbacks of `127.0.0.1:8000` and `bc_grouping.db` if a value is missing).

**Note:** running `uvicorn app.main:app` directly (instead of `python run.py`) bypasses `config.ini` and uses uvicorn's own defaults — pass `--port` explicitly if you do this and a non-default port is configured.

## Running the server

```bash
source .venv/bin/activate
python run.py
```

This starts the API on the host/port from `config.ini`, with auto-reload enabled. Once running, open:

- **Swagger UI:** `http://<host>:<port>/docs`
- **OpenAPI schema:** `http://<host>:<port>/openapi.json`
- **Health check:** `http://<host>:<port>/health`

## API overview

| Resource                    | Base path                     |
|------------------------------|--------------------------------|
| Biomedical Concepts          | `/biomedical-concepts`         |
| Classification Schemes       | `/classification-schemes`       |
| Classification Values        | `/classification-values`        |
| Classification Assignments   | `/classification-assignments`   |

Each resource supports `GET` (list, with pagination/filtering), `GET /{id}`, `POST`, `PUT /{id}`, and `DELETE /{id}`. Two composite/joined views are also available:

- `GET /biomedical-concepts/{bc_id}/classifications` — a BC's classifications, grouped by scheme
- `GET /classification-values/{value_id}/biomedical-concepts` — all BCs tagged with a given classification value

Writes that would violate a foreign-key or uniqueness constraint (e.g. deleting a BC that still has classification assignments) return `409 Conflict` rather than a raw database error.

## Tests

```bash
source .venv/bin/activate
pytest
```

Tests run against a disposable temporary copy of `bc_grouping.db` for each test — the real database file is never modified.

## Project layout

```
Groupings/
  config.ini              # server host/port and database path
  run.py                  # entrypoint: starts uvicorn using config.ini
  requirements.txt
  bc_grouping.db           # SQLite database (not tracked in git — see .gitignore)
  app/
    main.py                # FastAPI app assembly
    config.py              # reads config.ini
    database.py             # SQLAlchemy engine/session
    models.py               # SQLAlchemy ORM models
    schemas.py               # Pydantic request/response schemas
    crud.py                   # database access helpers
    routers/                  # one router per resource
  tests/                       # pytest suite
```
