# WineDB Design Document

## Overview

WineDB is a full-stack web application for managing wine industry data, focused on the United States market. It provides structured storage and retrieval of information about wines, wineries, vineyards, American Viticultural Areas (AVAs), grape varieties, and the people who produce them.

The application serves two audiences:
- **End users** via a browser-based HTML/HTMX UI
- **Developers/integrations** via a JSON REST API

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12+ |
| Web framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0+ (async) |
| Database (dev) | SQLite via aiosqlite |
| Database (prod) | PostgreSQL via asyncpg |
| Migrations | Alembic 1.13+ |
| Configuration | Pydantic Settings 2.0+ |
| CLI | Typer 0.12+ |
| Frontend | Jinja2 templates + HTMX 2.0.4 + Bootstrap 5.3.3 |
| Package manager | uv |
| Testing | pytest + pytest-asyncio + httpx |

---

## Directory Structure

```
winedb/
├── app/
│   ├── main.py              # FastAPI app initialization and router registration
│   ├── config.py            # Settings (DATABASE_URL via env var)
│   ├── database.py          # Async engine and session factory
│   ├── templates.py         # Jinja2 environment setup
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── ava.py
│   │   ├── vineyard.py
│   │   ├── winery.py
│   │   ├── wine.py
│   │   ├── person.py
│   │   ├── grape_variety.py
│   │   └── associations.py  # WineryStaff, VineyardOwner, WineVineyardSource,
│   │                        # WineGrapeVariety, VineyardGrapeVariety
│   ├── schemas/             # Pydantic request/response schemas
│   ├── crud/                # Async database access layer
│   │   ├── ava.py, vineyard.py, winery.py, wine.py, person.py, grape_variety.py
│   │   ├── winery_staff.py, vineyard_owner.py
│   │   └── wine_vineyard_source.py, wine_grape_variety.py
│   ├── routers/
│   │   ├── *.py             # JSON API endpoints
│   │   └── gui/             # HTML/HTMX UI endpoints
│   ├── static/              # CSS (app.css)
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── {entity}/list.html, _table.html, _rows.html
│   │   ├── ava/graph.html   # AVA hierarchy graph view
│   │   ├── partials/        # Reusable form/row fragments
│   │   └── {association}/list.html, _rows.html
│   └── cli/                 # Typer CLI (import command)
├── alembic/                 # Database migration scripts
├── data/
│   ├── seed/                # YAML seed data files
│   └── winedb.db            # SQLite dev database
├── plan/                    # Design and planning documents
├── scripts/                 # One-off utility scripts
├── tests/
├── pyproject.toml
└── uv.lock
```

---

## Data Model

### Entity Relationship Overview

```
person ─────────────┬──── winery_staff ────── winery ──── wine
                    │                           │            │
                    └──── vineyard_owner ─── vineyard ──────┘ (wine_vineyard_source)
                                               │
                                   vineyard_grape_variety
                                               │
                                         grape_variety ──── wine (primary)
                                                    └────── wine_grape_variety ── wine

                              ava ←─── ava (parent, self-ref)
                               │
                  winery ──────┤
                  vineyard ────┤
                  wine ────────┘
```

### Tables

#### `ava` — American Viticultural Areas

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| name | String (unique, not null) | Full official name |
| short_name | String (nullable) | |
| state | String (not null) | |
| county | String (nullable) | |
| parent_ava_id | FK → ava.id (nullable) | Self-referential hierarchy |
| ttb_approval_date | Date (nullable) | |
| total_acres | Integer (nullable) | |
| planted_acres | Integer (nullable) | |
| description | Text (nullable) | |

Relationships: `parent`, `children` (self-referential), `vineyards`, `wineries`, `wines`

#### `grape_variety` — Grape Cultivars

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| key | String (unique, not null) | Stable seed key, e.g. `pinot_noir` |
| name | String (unique, not null) | Display name, e.g. `Pinot Noir` |
| name_synonyms | String (nullable) | Comma-separated |
| color | String (nullable) | `red` or `white` |
| origin_region | String (nullable) | e.g. `Burgundy` |

Relationships: `wines` (primary variety), `wine_varieties` (WineGrapeVariety), `vineyard_grape_varieties` (VineyardGrapeVariety)

#### `person` — Growers, Winemakers, Owners

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| first_name | String (not null) | |
| last_name | String (not null) | |
| birth_year | Integer (nullable) | |
| nationality | String (nullable) | |
| biography | Text (nullable) | |

Relationships: `winery_staff`, `vineyard_ownerships`

#### `vineyard` — Named Vineyard Sites

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| name | String (not null) | |
| ava_id | FK → ava.id (not null) | |
| latitude | Float (nullable) | |
| longitude | Float (nullable) | |
| elevation_ft_low | Integer (nullable) | |
| elevation_ft_high | Integer (nullable) | |
| total_acres | Float (nullable) | |
| soil_type | String (nullable) | |
| established_year | Integer (nullable) | |
| description | Text (nullable) | |

Relationships: `ava`, `owners` (VineyardOwner), `wine_sources` (WineVineyardSource), `vineyard_grape_varieties` (VineyardGrapeVariety, ordered by sort_order)

#### `winery` — Wine Producers

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| name | String (unique, not null) | |
| established_year | Integer (nullable) | |
| location_city | String (nullable) | |
| location_state | String (nullable) | |
| ava_id | FK → ava.id (nullable) | |
| is_negociant | Boolean (default false) | True if purchases rather than grows grapes |
| website | String (nullable) | |
| description | Text (nullable) | |

Relationships: `ava`, `staff` (WineryStaff), `wines`

#### `wine` — Individual Wine Products

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| winery_id | FK → winery.id (not null) | |
| label_name | String (not null) | e.g. `Lucia Chardonnay Soberanes` |
| vintage_year | Integer (not null) | |
| grape_variety_id | FK → grape_variety.id (nullable) | Primary variety |
| ava_id | FK → ava.id (nullable) | Label AVA (may differ from vineyard AVA) |
| alcohol_pct | Float (nullable) | |
| production_cases | Integer (nullable) | |
| release_date | Date (nullable) | |
| tasting_notes | Text (nullable) | |
| winery_description | Text (nullable) | |
| description | Text (nullable) | |

Relationships: `winery`, `primary_variety` (GrapeVariety), `ava`, `vineyard_sources` (WineVineyardSource), `grape_varieties` (WineGrapeVariety)

#### `winery_staff` — Person Roles at Wineries (Association)

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| winery_id | FK → winery.id | |
| person_id | FK → person.id | |
| role | String (not null) | e.g. `winemaker`, `owner`, `vineyard_manager` |
| year_start | Integer (nullable) | |
| year_end | Integer (nullable) | null = currently active |
| notes | Text (nullable) | |

#### `vineyard_owner` — Vineyard Ownership History (Association)

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| vineyard_id | FK → vineyard.id | |
| person_id | FK → person.id | |
| ownership_role | String (nullable) | e.g. `owner`, `manager`, `co-owner` |
| year_start | Integer (nullable) | |
| year_end | Integer (nullable) | null = currently active |

#### `wine_vineyard_source` — Fruit Sourcing per Wine (Association)

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| wine_id | FK → wine.id | |
| vineyard_id | FK → vineyard.id | |
| block_name | String (nullable) | Sub-vineyard block |
| pct_blend | Float (nullable) | % of the wine's fruit |
| UNIQUE | (wine_id, vineyard_id, block_name) | |

#### `wine_grape_variety` — Blend Breakdown per Wine (Association)

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| wine_id | FK → wine.id | |
| grape_variety_id | FK → grape_variety.id | |
| pct_blend | Float (nullable) | % of the blend |
| UNIQUE | (wine_id, grape_variety_id) | |

#### `vineyard_grape_variety` — Varieties Grown at a Vineyard (Association)

| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| vineyard_id | FK → vineyard.id | |
| grape_variety_id | FK → grape_variety.id | |
| sort_order | Integer (not null, default 0) | Preserves seed data ordering |
| UNIQUE | (vineyard_id, grape_variety_id) | |

Relationships: `vineyard` (order_by sort_order), `grape_variety`

---

## API Design

### JSON REST API

Base path: `/`

All six primary resources follow standard CRUD:

| Method | Path | Description |
|---|---|---|
| GET | `/{resource}/` | List with filters |
| GET | `/{resource}/{id}` | Detail with nested relationships |
| POST | `/{resource}/` | Create |
| PATCH | `/{resource}/{id}` | Partial update |
| DELETE | `/{resource}/{id}` | Delete |

**Resources**: `ava`, `vineyards`, `wineries`, `wines`, `persons`, `grape-varieties`

**Query parameters (per resource):**

| Resource | Filter params |
|---|---|
| `ava` | `state`, `parent_ava_id` |
| `vineyards` | `ava_id`, `name` |
| `wineries` | `ava_id`, `is_negociant`, `name` |
| `wines` | `winery_id`, `ava_id`, `vintage_year`, `grape_variety_id`, `label_name`, `sort_by`, `sort_dir` |
| `persons` | `search` (ilike on first and last name) |
| `grape-varieties` | `color` |

All list endpoints support `skip` / `limit` (max 500). API docs auto-generated at `/docs` (Swagger UI).

### HTML/HTMX UI

Base path: `/ui`

#### Primary resources

Each of the six primary resources (`ava`, `vineyards`, `wineries`, `wines`, `persons`, `grape-varieties`) exposes:

| Method | Path | Description |
|---|---|---|
| GET | `/ui/{resource}` | Full list page (filter form + table) |
| GET | `/ui/{resource}/rows` | tbody rows partial (HTMX filter/sort target) |
| GET | `/ui/{resource}/modal/new` | Create form modal fragment |
| GET | `/ui/{resource}/modal/{id}` | Edit form modal fragment (pre-populated) |
| POST | `/ui/{resource}` | Create → returns updated row + `HX-Trigger: closeModal` |
| POST | `/ui/{resource}/{id}/edit` | Update → returns updated row + `HX-Trigger: closeModal` |
| DELETE | `/ui/{resource}/{id}` | Delete → empty response |

Wines additionally expose:

| Method | Path | Description |
|---|---|---|
| GET | `/ui/wines/vineyard-source-row` | Dynamic vineyard source row fragment (used in wine create/edit form) |

AVA additionally exposes:

| Method | Path | Description |
|---|---|---|
| GET | `/ui/ava/graph` | AVA hierarchy graph view |

#### Association views (read-only list + filter/sort)

| Resource | Path | Filter params |
|---|---|---|
| Winery staff | `/ui/winery-staff` | `winery_search`, `person_search`, `role_search`, `sort_by`, `sort_dir` |
| Vineyard owners | `/ui/vineyard-owners` | `vineyard_search`, `person_search`, `role_search`, `sort_by`, `sort_dir` |
| Wine grape varieties | `/ui/wine-grape-varieties` | `label_search`, `winery_search`, `grape_search`, `sort_by`, `sort_dir` |
| Wine vineyard sources | `/ui/wine-vineyard-sources` | `label_search`, `winery_search`, `vineyard_search`, `sort_by`, `sort_dir` |

Each association view has a `/rows` endpoint returning the tbody partial.

---

## Application Layers

### Layer Architecture

```
HTTP Request
     |
     v
Router (routers/ or routers/gui/)
     |  validates request, calls CRUD
     v
CRUD (crud/)
     |  async SQLAlchemy queries (contains_eager, ilike)
     v
SQLAlchemy Models (models/)
     |
     v
Database (SQLite / PostgreSQL)
```

### Pydantic Schema Pattern

| Schema | Purpose |
|---|---|
| `{Entity}Base` | Shared fields |
| `{Entity}Create` | Fields for POST (required + optional) |
| `{Entity}Update` | All fields optional (for PATCH) |
| `{Entity}Read` | Response with `id`, `from_attributes=True` |
| `{Entity}Detail` | Extended read with nested relationships |

Notable detail schemas:
- `WineDetail` — includes `vineyard_sources: List[VineyardSourceRead]`
- `WineryDetail` — includes `staff: List[WineryStaffRead]`
- `AVADetail` — includes `children: List[AVARead]`

---

## Frontend Architecture

### Template Structure

- **`base.html`**: Fixed sidebar + main content area (flexbox layout). Sidebar links: Grape Varieties, AVAs, Persons, Vineyards, Wineries, Wines; Associations section: Winery Staff, Vineyard Owners, Wine Sources, Wine Blends.
- **`{entity}/list.html`**: Full page extending base; filter form + table
- **`{entity}/_table.html`**: Table with header row; HTMX swap target
- **`{entity}/_rows.html`**: tbody rows only; returned by `/rows` endpoint
- **`ava/graph.html`**: AVA hierarchy graph view
- **`partials/form_{entity}.html`**: Create/edit modal form (field-level validation errors displayed inline)
- **`partials/table_row_{entity}.html`**: Single row returned after create/update
- **`partials/vineyard_source_row.html`**: Dynamic row in wine form for adding vineyard sources

### HTMX Interaction Pattern

1. **Live filtering**: Filter inputs trigger `GET /ui/{resource}/rows` via `hx-get` with 300ms delay; response swaps the tbody.
2. **Sortable columns**: Column header click toggles `sort_dir`; hidden `sort_by`/`sort_dir` inputs carry state through filter changes.
3. **Create modal**: "New" button triggers `GET /ui/{resource}/modal/new`; Bootstrap modal is injected and shown.
4. **Edit modal**: Row edit button triggers `GET /ui/{resource}/modal/{id}`; pre-filled modal is injected.
5. **Form submit**: Modal form POSTs; on success returns the new/updated row + `HX-Trigger: closeModal`; on 422 re-renders the form with errors.
6. **Delete**: Row delete button triggers `hx-delete` with `hx-confirm`; on success the row is removed.
7. **Dynamic vineyard sources**: In the wine form, adding a vineyard row calls `GET /ui/wines/vineyard-source-row` to append a new source input row.

---

## CLI

Entry point: `winedb` (defined in `pyproject.toml`)

### Commands

```
winedb import <seed_dir>
```

Imports YAML seed data from the specified directory in dependency order:

| Step | File | Notes |
|---|---|---|
| 1 | `ava.yaml` | Two-pass: insert without parent first, then resolve `parent_ava_id` |
| 2 | `grape_varieties.yaml` | Keyed by stable `key` field |
| 3 | `persons.yaml` | |
| 4 | `vineyards.yaml` | Also syncs `VineyardGrapeVariety` from `grape_varieties` array |
| 5 | `vineyard_owner.yaml` | |
| 6 | `wineries.yaml` | |
| 7 | `winery_staff.yaml` | |
| 8 | `wines.yaml` | References primary variety by `key` |
| 9 | `wine_vineyard_sources.yaml` | |
| 10 | `wine_grape_variety.yaml` | |

All imports are upserts by natural key (safe to re-run). Missing files are skipped with a warning. Unresolved foreign key references log a warning and are skipped.

---

## Scripts

One-off utility scripts in `scripts/`:

- **`extract_wine_vineyard_sources.py`**: Extracts nested `vineyard_sources` from `wines.yaml` into a separate `wine_vineyard_sources.yaml`. Updates `wines.yaml` in-place. Used once during seed data restructuring.
- **`generate_flagship_wines.py`**: Generates YAML blocks for flagship California wines from a hardcoded `FLAGSHIPS` dict (winery → label, variety, vintage, AVA). Output is intended for manual review before adding to seed data.

---

## Configuration

Environment variable: `DATABASE_URL`

| Environment | Value |
|---|---|
| Development (default) | `sqlite+aiosqlite:///./data/winedb.db` |
| Production | `postgresql+asyncpg://user:password@host/winedb` |

Supports `.env` file via Pydantic Settings.

---

## Database Migrations

Managed by Alembic. Single initial migration (`817101459347_initial_schema.py`) creates all tables.

```bash
# Apply migrations
uv run alembic upgrade head

# Create new migration after model changes
uv run alembic revision --autogenerate -m "description"
```

---

## Running the Application

```bash
# Install dependencies
uv sync

# Apply DB migrations
uv run alembic upgrade head

# Import seed data
uv run winedb import data/seed/

# Start development server
uv run uvicorn app.main:app --reload
```

- UI: `http://localhost:8000/ui`
- API: `http://localhost:8000/`
- API docs: `http://localhost:8000/docs`

---

## Design Notes

- **Single `person` table**: Unified table for growers, winemakers, and owners. Role is captured in the association tables (`winery_staff.role`, `vineyard_owner.ownership_role`).
- **`wine.ava_id` vs `vineyard.ava_id`**: Label AVA (legal designation on the bottle) is stored on `wine` separately from the vineyard's geographic AVA, because they can differ.
- **`grape_variety.key`**: Stable snake_case identifier (e.g. `pinot_noir`) used in YAML seed files for cross-references. Decoupled from the human-readable `name` field.
- **`vineyard_grape_variety.sort_order`**: Preserves the order of grape varieties as listed in the seed file for a vineyard.
- **Unique constraints on association tables**: Prevent duplicate entries across all join tables.
- **Eager loading**: CRUD functions use `contains_eager()` with explicit joins to avoid N+1 query problems on list pages.
- **No authentication**: Designed for personal/research use. The `/docs` Swagger UI is the primary interface for API exploration.
