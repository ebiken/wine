# Wine Database

A database-backed application to manage information about wines in the United States — AVAs, vineyards, wineries, people, and individual wines.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

Install uv if not already available:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Setup

```sh
cd winedb
uv sync
```

## Database

Initialize the database (creates `data/winedb.db`):

```sh
uv run alembic upgrade head
```

Load seed data (AVAs, grape varieties, vineyards, wineries, wines):

```sh
uv run winedb data/seed/
```

## Running the API

```sh
uv run uvicorn app.main:app --reload
```

The API is now available at http://localhost:8000

Open the interactive Swagger UI at http://localhost:8000/docs to browse and query all data.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/ava/` | List AVAs (filter by `state`, `parent_ava_id`) |
| GET | `/ava/{id}` | AVA detail with child sub-AVAs |
| GET | `/vineyards/` | List vineyards (filter by `ava_id`, `name`) |
| GET | `/vineyards/{id}` | Vineyard detail |
| GET | `/wineries/` | List wineries (filter by `ava_id`, `is_negociant`, `name`) |
| GET | `/wineries/{id}` | Winery detail with staff history |
| GET | `/wines/` | List wines (filter by `winery_id`, `ava_id`, `vintage_year`, `grape_variety_id`, `label_name`) |
| GET | `/wines/{id}` | Wine detail with vineyard sources and blend percentages |
| GET | `/persons/` | List people (filter by `search` for name) |
| GET | `/persons/{id}` | Person detail |
| GET | `/grape-varieties/` | List grape varieties (filter by `color`) |
| GET | `/grape-varieties/{id}` | Grape variety detail |

All endpoints also support `POST` (create), `PATCH` (update), and `DELETE`.

### Example queries

List all AVAs under Monterey:

```sh
curl "http://localhost:8000/ava/?parent_ava_id=2"
```

Find all 2021 Pinot Noirs:

```sh
curl "http://localhost:8000/wines/?vintage_year=2021&grape_variety_id=1"
```

Search for a person by name:

```sh
curl "http://localhost:8000/persons/?search=Pisoni"
```

Get wine detail with vineyard sources:

```sh
curl "http://localhost:8000/wines/1"
```

## Importing additional seed data

Seed files are YAML and live in `data/seed/`. Edit or add records and re-run:

```sh
uv run winedb data/seed/
```

The import command upserts records — running it multiple times is safe.

Supported files (processed in this order):

| File | Contents |
|------|----------|
| `ava.yaml` | American Viticultural Areas and their hierarchy |
| `grape_varieties.yaml` | Grape cultivars |
| `persons.yaml` | Growers, winemakers, and owners |
| `vineyards.yaml` | Named vineyard sites |
| `wineries.yaml` | Wine producers |
| `wines.yaml` | Individual wines with vineyard sources |

## Project structure

```
winedb/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings (DATABASE_URL)
│   ├── database.py      # SQLAlchemy engine and session
│   ├── models/          # ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── routers/         # FastAPI route handlers
│   ├── crud/            # Database access functions
│   └── cli/             # winedb CLI (import command)
├── alembic/             # Database migrations
├── data/
│   ├── seed/            # YAML seed data files
│   └── winedb.db        # SQLite database (local dev)
└── plan/
    └── wine-db-plan.md  # Architecture and implementation plan
```

## Cloud deployment

Set the `DATABASE_URL` environment variable to a PostgreSQL connection string before starting the app:

```sh
export DATABASE_URL="postgresql+asyncpg://user:password@host/winedb"
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

See [plan/wine-db-plan.md](plan/wine-db-plan.md) for AWS and Azure deployment options.
