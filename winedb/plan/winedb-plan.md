# Wine Database Application Plan

## Overview

A database-backed application to manage information about wines in the United States — vineyards, AVAs, wineries, winemakers, growers, and individual wines with vintage detail.

**Deployment targets:** macOS (local development), AWS or Azure (cloud production)

---

## 1. Tech Stack Recommendation

### Database: SQLite (local) → PostgreSQL (cloud)

The wine domain is fundamentally relational. Wines link to vineyards, vineyards link to AVAs, wineries link to people across vintage years. A relational model captures these relationships cleanly with proper referential integrity.

- **SQLite** for local macOS development — zero setup, single file, portable
- **PostgreSQL** for cloud deployment — AWS RDS or Azure Database for PostgreSQL
- SQLAlchemy ORM abstracts the difference; switching is a `DATABASE_URL` change

### Language and Framework: Python 3.12+

The project `.gitignore` uses the standard Python template (`__pycache__`, `.venv`, `uv.lock`, `mypy`, `ruff`, etc.), confirming Python as the intended language.

| Component | Choice | Reason |
|-----------|--------|--------|
| Web framework | **FastAPI** | Auto OpenAPI/Swagger docs, Pydantic validation, async-ready |
| ORM | **SQLAlchemy 2.x** | Database-agnostic, works with SQLite and PostgreSQL identically |
| Migrations | **Alembic** | Schema version control, auto-generates from ORM models |
| Data validation | **Pydantic v2** | Bundled with FastAPI; request/response schema enforcement |
| CLI | **Typer** | Data import commands (`winedb import`) |
| Package manager | **uv** | Confirmed by `.gitignore` tracking `uv.lock` |

**Key dependencies (`pyproject.toml`):**
```
fastapi[standard]
sqlalchemy[asyncio]
alembic
pydantic-settings
typer
asyncpg        # PostgreSQL async driver
aiosqlite      # SQLite async driver
httpx          # test client
pytest
pytest-asyncio
```

---

## 2. Data Model

### Core Entities

#### `ava` — American Viticultural Area

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `name` | text UNIQUE NOT NULL | e.g. "Santa Lucia Highlands" |
| `short_name` | text | e.g. "SLH" |
| `parent_ava_id` | integer FK -> ava.id | NULL for top-level |
| `state` | text NOT NULL | e.g. "CA" |
| `county` | text | e.g. "Monterey" |
| `ttb_approval_date` | date | Official TTB designation date |
| `total_acres` | integer | Total area in acres |
| `planted_acres` | integer | Planted vineyard acres |
| `description` | text | |

Self-referential `parent_ava_id` models the hierarchy:
`California > Central Coast > Monterey > Santa Lucia Highlands`

#### `vineyard` — A named growing site

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `name` | text NOT NULL | e.g. "Pisoni Vineyard" |
| `ava_id` | integer FK -> ava.id NOT NULL | |
| `latitude` | float | |
| `longitude` | float | |
| `elevation_ft_low` | integer | Elevation range (low) |
| `elevation_ft_high` | integer | Elevation range (high) |
| `total_acres` | integer | |
| `soil_type` | text | e.g. "granitic loam" |
| `established_year` | integer | Year first planted |
| `description` | text | |

#### `person` — Wine growers and winemakers (unified)

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `first_name` | text NOT NULL | |
| `last_name` | text NOT NULL | |
| `birth_year` | integer | |
| `nationality` | text | |
| `biography` | text | |

A single `person` table avoids duplication — the same person can be both a grower and a winemaker. Their role is captured in association tables.

#### `winery` — A wine production entity (label/brand)

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `name` | text UNIQUE NOT NULL | e.g. "Kosta Browne" |
| `established_year` | integer | |
| `location_city` | text | |
| `location_state` | text | |
| `ava_id` | integer FK -> ava.id | NULL if outside an AVA |
| `is_negociant` | boolean | True if winery buys fruit rather than growing it |
| `website` | text | |
| `description` | text | |

#### `grape_variety` — Cultivar reference table

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `name` | text UNIQUE NOT NULL | e.g. "Pinot Noir" |
| `name_synonyms` | text | Comma-separated alternate names |
| `color` | text | "red" or "white" |
| `origin_region` | text | e.g. "Burgundy" |

#### `wine` — A specific wine (label + vintage)

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `winery_id` | integer FK -> winery.id NOT NULL | |
| `label_name` | text NOT NULL | e.g. "Lucia Chardonnay Soberanes" |
| `vintage_year` | integer NOT NULL | |
| `grape_variety_id` | integer FK -> grape_variety.id | Primary variety |
| `ava_id` | integer FK -> ava.id | The AVA printed on the label |
| `alcohol_pct` | float | |
| `production_cases` | integer | Approximate case production |
| `release_date` | date | |
| `tasting_notes` | text | Aroma/flavor description |
| `winery_description` | text | Producer's own notes |
| `description` | text | General notes |

Note: `wine.ava_id` is kept separate from `vineyard.ava_id` because the label AVA (legal designation) can differ from the vineyard's AVA (e.g. a "Monterey County" label using fruit from an SLH-designated vineyard).

### Association / Junction Tables

#### `winery_staff` — Person's role at a winery over time

| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | |
| `winery_id` | integer FK -> winery.id | |
| `person_id` | integer FK -> person.id | |
| `role` | text | "winemaker", "vineyard_manager", "owner", "consultant" |
| `year_start` | integer | |
| `year_end` | integer | NULL if current |
| `notes` | text | |

#### `wine_vineyard_source` — Vineyards that contributed fruit to a wine

| Column | Type | Notes |
|--------|------|-------|
| `wine_id` | integer FK -> wine.id | |
| `vineyard_id` | integer FK -> vineyard.id | |
| `block_name` | text | e.g. "North Crest", "Block 4" |
| `pct_blend` | float | Percent of blend; NULL if unknown |

PK: `(wine_id, vineyard_id, block_name)`

#### `wine_grape_variety` — For blended wines

| Column | Type | Notes |
|--------|------|-------|
| `wine_id` | integer FK -> wine.id | |
| `grape_variety_id` | integer FK -> grape_variety.id | |
| `pct_blend` | float | |

PK: `(wine_id, grape_variety_id)`

#### `vineyard_owner` — Ownership/management history

| Column | Type | Notes |
|--------|------|-------|
| `vineyard_id` | integer FK -> vineyard.id | |
| `person_id` | integer FK -> person.id | |
| `ownership_role` | text | "owner", "manager", "co-owner" |
| `year_start` | integer | |
| `year_end` | integer | NULL if current |

### Optional Extension Entities

**`external_review`** — Critic reviews (one wine can have many reviews):
`wine_id`, `critic_name`, `publication`, `score` (0-100), `review_date`, `review_url`, `review_text`

**`winemaking_note`** — Technical production details per wine:
`wine_id`, `fermentation` (native yeast / inoculated), `vessel` (French oak / stainless), `new_oak_pct`, `aging_months`, `whole_cluster_pct`

**`vineyard_block`** — Sub-areas of a vineyard:
`vineyard_id`, `block_name`, `clone`, `row_orientation`, `planted_year`, `soil_sub_type`

### Entity Relationship Summary

```
ava (self-referential parent_ava_id)
 |
 +-- vineyard (ava_id)
 |    +-- vineyard_block
 |    +-- vineyard_owner (-> person)
 |
 +-- winery (ava_id, optional)
 |    +-- winery_staff (-> person, role, year range)
 |    +-- wine (winery_id, ava_id, vintage_year)
 |         +-- wine_vineyard_source (-> vineyard, block_name)
 |         +-- wine_grape_variety (-> grape_variety)
 |         +-- external_review
 |         +-- winemaking_note
 |
 +-- grape_variety (standalone reference)
person (standalone, referenced by winery_staff and vineyard_owner)
```

---

## 3. Application Architecture

### Local Development (macOS)

```
[Browser / curl]
      |
 FastAPI app  (uvicorn, http://localhost:8000)
      |
 SQLAlchemy ORM
      |
 SQLite  (winedb/data/winedb.db)
```

- Start with: `uv run uvicorn app.main:app --reload`
- FastAPI's built-in Swagger UI at `/docs` serves as the primary interface for browsing and editing data — no separate frontend needed for personal use
- Data import via CLI: `uv run winedb import data/seed/ava.yaml`

### Cloud Deployment

The only difference from local is the `DATABASE_URL` environment variable (SQLite path → PostgreSQL connection string) and the compute target. The same Docker image is used in both cases.

**AWS (recommended):**
```
[HTTPS]
   |
 ALB (Application Load Balancer)
   |
 ECS Fargate  (Docker: FastAPI + uvicorn)
   |
 RDS PostgreSQL  (db.t4g.micro for low cost)
   |
 Secrets Manager  (DATABASE_URL, etc.)
```

**Azure:**
```
[HTTPS]
   |
 Azure Container Apps
   |
 Azure Database for PostgreSQL  (Flexible Server, Burstable B1ms)
   |
 Azure Key Vault
```

No Kubernetes, no microservices — a single container is sufficient.

---

## 4. Project Directory Structure

```
wine/
+-- winedb/
    +-- plan/
    |   +-- wine-db-plan.md        # this document
    +-- README.md
    +-- pyproject.toml             # uv project config
    +-- uv.lock
    +-- .python-version            # pinned Python version
    +-- Dockerfile
    +-- docker-compose.yml         # optional: local Postgres alternative
    +-- .env.example               # sample env vars (never commit .env)
    +-- alembic.ini
    +-- alembic/
    |   +-- env.py
    |   +-- versions/
    |       +-- 0001_initial_schema.py
    +-- app/
    |   +-- __init__.py
    |   +-- main.py                # FastAPI app factory, router registration
    |   +-- config.py              # pydantic-settings; reads DATABASE_URL etc.
    |   +-- database.py            # SQLAlchemy engine + session factory
    |   +-- models/                # SQLAlchemy ORM models
    |   |   +-- __init__.py
    |   |   +-- ava.py
    |   |   +-- vineyard.py
    |   |   +-- person.py
    |   |   +-- winery.py
    |   |   +-- grape_variety.py
    |   |   +-- wine.py
    |   |   +-- associations.py    # junction tables
    |   +-- schemas/               # Pydantic request/response schemas
    |   |   +-- (one per entity)
    |   +-- routers/               # FastAPI routers
    |   |   +-- (one per entity)
    |   +-- crud/                  # Database access functions
    |   |   +-- base.py            # generic CRUD mixin
    |   |   +-- (one per entity)
    |   +-- cli/
    |       +-- main.py            # `winedb` CLI entry point (Typer)
    |       +-- import_cmd.py      # `winedb import <file>`
    +-- data/
    |   +-- winedb.db              # SQLite dev database (gitignored)
    |   +-- seed/
    |       +-- ava.yaml
    |       +-- grape_varieties.yaml
    |       +-- wineries.yaml
    |       +-- vineyards.yaml
    |       +-- wines.yaml
    +-- tests/
        +-- conftest.py
        +-- test_wines.py
        +-- test_wineries.py
        +-- test_vineyards.py
```

---

## 5. Implementation Phases

### Phase 1: Foundation — schema and migrations

**Goal:** SQLite database with the full schema. No API yet.

1. Initialize uv project: `uv init --app` in `winedb/`
2. Add dependencies
3. Write SQLAlchemy ORM models in `app/models/`
4. Configure Alembic; generate initial migration: `alembic revision --autogenerate -m "initial_schema"`
5. Run migration: `alembic upgrade head`
6. Verify schema: `sqlite3 data/winedb.db .schema`

**Deliverable:** `data/winedb.db` with correct empty schema.

### Phase 2: Seed data from the web

**Goal:** Populate the database with real California wine data.

Sources to fetch:
- **TTB AVA registry** (ttb.gov) — official AVA list with parent regions, approval dates, acreage
- **Wine Institute** — California winery and vineyard directory
- **Wine Spectator / Wine Enthusiast** — wine reviews, scores, tasting notes
- **Winery websites** — production details, winemaker bios, vineyard sourcing

Steps:
1. Write YAML seed files under `data/seed/` using web-fetched data
2. Implement `winedb import` CLI (Typer) that reads YAML and upserts records via SQLAlchemy
3. Run import and verify with SQLite queries

**Deliverable:** Database populated with real wine data; CLI import working.

### Phase 3: REST API

**Goal:** Full CRUD API accessible via browser (Swagger UI).

Key endpoints:
- `GET /ava/` — list/filter AVAs by state, parent
- `GET /ava/{id}` — AVA with child AVAs and vineyards
- `GET /vineyards/` — filter by ava_id, name
- `GET /vineyards/{id}` — with wines sourced from this vineyard
- `GET /wineries/` — filter by ava_id
- `GET /wineries/{id}` — with staff history and wines
- `GET /wines/` — filter by vintage_year, winery_id, ava_id, grape_variety
- `GET /wines/{id}` — with vineyard sources, reviews
- `GET /persons/` — filter by role
- `POST/PUT/DELETE` for all entities

**Deliverable:** Running local API at `localhost:8000/docs`.

### Phase 4: Docker and cloud readiness

**Goal:** Single Docker image deployable to AWS or Azure.

1. Write `Dockerfile` (multi-stage build with `uv sync --frozen --no-dev`)
2. Write `docker-compose.yml` (app + postgres services)
3. Make `DATABASE_URL` the single config point via `pydantic-settings`
4. Test: `docker compose up`, run Alembic against Postgres, verify API
5. Document deployment steps in `winedb/plan/deploy_en.adoc`

**Deliverable:** Docker image running against PostgreSQL; deployment guide.

### Phase 5: Enhancements (ongoing)

- Full-text search on tasting notes (PostgreSQL `tsvector`, SQLite FTS5)
- Add `external_review` and `winemaking_note` entities
- Expand beyond California (Oregon Pinot, Washington Cabernet, etc.)
- Simple HTML frontend with Jinja2 templates if Swagger UI becomes limiting
- API key authentication if deployed publicly

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Single `person` table vs. separate grower/winemaker tables | Single `person` + role in `winery_staff` | Same person can be both; avoids duplicates |
| SQLite vs Postgres locally | SQLite | Zero setup; same ORM code works for both |
| FastAPI vs Flask | FastAPI | Auto docs, built-in validation, async support |
| ORM vs raw SQL | SQLAlchemy ORM | Schema changes in Python; Alembic handles migrations |
| No frontend | Swagger UI `/docs` | Personal research tool; YAGNI |
| `wine.ava_id` separate from `vineyard.ava_id` | Keep both | Label AVA (legal) can differ from vineyard AVA |
| YAML seed files | YAML | Human-readable; easy to edit when adding new data |
