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

Load seed data (AVAs, grape varieties, vineyards, wineries, wines, and relationships):

```sh
uv run winedb import data/seed/
```

## Running the application

```sh
uv run uvicorn app.main:app --reload
```

- **UI**: http://localhost:8000/ui — browser-based interface for browsing and editing all data
- **API**: http://localhost:8000 — JSON REST API
- **API docs**: http://localhost:8000/docs — interactive Swagger UI

## GUI

The browser UI is available at http://localhost:8000/ui after starting the application.

### Navigation

The sidebar provides access to all resources:

| Section | Pages |
|---------|-------|
| **Primary** | Grape Varieties, AVAs, Persons, Vineyards, Wineries, Wines |
| **Associations** | Winery Staff, Vineyard Owners, Wine Sources, Wine Blends |

### Features

**Filtering**: Each list page has a filter form above the table. Inputs update the table live (300ms delay) without a full page reload.

**Sorting**: Click any column header to sort by that column. Click again to reverse direction. Sort state is preserved when filters change.

**Create / Edit**: Click the **New** button or a row's edit icon to open a modal form. Validation errors are shown inline without losing form state.

**Delete**: Each row has a delete button with a confirmation prompt.

**AVA hierarchy graph**: The AVAs page includes a graph view (`/ui/ava/graph`) showing the parent–child relationships between viticultural areas.

**Wine form**: When creating or editing a wine, vineyard source rows can be added dynamically to record which vineyards contributed fruit and at what blend percentage.

### UI pages

| Path | Description |
|------|-------------|
| `/ui/grape-varieties` | Grape cultivars |
| `/ui/ava` | American Viticultural Areas |
| `/ui/ava/graph` | AVA hierarchy graph |
| `/ui/persons` | Growers, winemakers, and owners |
| `/ui/vineyards` | Named vineyard sites |
| `/ui/wineries` | Wine producers |
| `/ui/wines` | Individual wines |
| `/ui/winery-staff` | Person roles at wineries over time |
| `/ui/vineyard-owners` | Vineyard ownership history |
| `/ui/wine-vineyard-sources` | Fruit sourcing per wine |
| `/ui/wine-grape-varieties` | Blend breakdown per wine |

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

List all sub-AVAs under Monterey:

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

## Seed data

Seed files are YAML and live in `data/seed/`. Edit or add records and re-run:

```sh
uv run winedb import data/seed/
```

The import command upserts records — running it multiple times is safe.

Files are processed in dependency order:

| File | Contents |
|------|----------|
| `ava.yaml` | American Viticultural Areas and their hierarchy |
| `grape_varieties.yaml` | Grape cultivars (keyed by stable `key` field, e.g. `pinot_noir`) |
| `persons.yaml` | Growers, winemakers, and owners |
| `vineyards.yaml` | Named vineyard sites (includes `grape_varieties` array for varieties grown) |
| `vineyard_owner.yaml` | Vineyard ownership and management history |
| `wineries.yaml` | Wine producers |
| `winery_staff.yaml` | People and roles at wineries over time |
| `wines.yaml` | Individual wines (label, vintage, primary variety, etc.) |
| `wine_vineyard_sources.yaml` | Fruit sourcing: which vineyards contribute to each wine |
| `wine_grape_variety.yaml` | Blend breakdown (multiple varieties per wine) |

## Schema changes

When the ORM models change, generate and apply a new Alembic migration:

```sh
# Generate migration from model diff
uv run alembic revision --autogenerate -m "short description of change"

# Review the generated file in alembic/versions/ before applying
uv run alembic upgrade head
```

To check current migration state:

```sh
uv run alembic current
uv run alembic history
```

To roll back the last migration:

```sh
uv run alembic downgrade -1
```

## Scripts

One-off utility scripts in `scripts/`. These are not part of the application and are run manually when needed.

### `scripts/generate_flagship_wines.py`

Generates YAML blocks for flagship and notable wines from a hardcoded `FLAGSHIPS` dict (winery name → label, primary variety, vintage, optional AVA override). Output is printed to stdout for review and manual addition to `data/seed/wines.yaml`.

```sh
uv run python scripts/generate_flagship_wines.py >> data/seed/wines.yaml
```

Edit the output before committing — the script fills in placeholder descriptions from winery records and leaves `tasting_notes`, `alcohol_pct`, and `production_cases` as null.

### `scripts/extract_wine_vineyard_sources.py`

One-off transform: extracts nested `vineyard_sources` entries from `wines.yaml` into a separate `wine_vineyard_sources.yaml`, and removes the keys from `wines.yaml` in-place. Run once when restructuring seed data; not needed in normal operation.

```sh
uv run python scripts/extract_wine_vineyard_sources.py
```

## Project structure

```
winedb/
├── app/
│   ├── main.py          # FastAPI app, router registration
│   ├── config.py        # Settings (DATABASE_URL env var)
│   ├── database.py      # Async SQLAlchemy engine and session
│   ├── models/          # ORM models (ava, vineyard, winery, wine, person,
│   │                    #   grape_variety, associations)
│   ├── schemas/         # Pydantic request/response schemas
│   ├── crud/            # Async database access functions
│   ├── routers/         # FastAPI route handlers
│   │   └── gui/         # HTML/HTMX UI route handlers
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # Static assets (CSS)
│   └── cli/             # winedb CLI (import command)
├── alembic/             # Database migrations
├── data/
│   ├── seed/            # YAML seed data files
│   └── winedb.db        # SQLite database (local dev)
├── scripts/             # One-off utility scripts
├── plan/                # Design and architecture documents
└── tests/
```

See [DESIGN.md](DESIGN.md) for full architecture documentation.

## Cloud deployment

Set the `DATABASE_URL` environment variable to a PostgreSQL connection string before starting the app:

```sh
export DATABASE_URL="postgresql+asyncpg://user:password@host/winedb"
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
