# WineDb GUI Plan

## Overview

Add a browser-based web GUI with full CRUD for all 6 entities, integrated directly into the existing FastAPI application using Jinja2 templates and HTMX for dynamic interactions. No separate frontend server, no npm, no build step.

## Tech Stack

- **Templates**: Jinja2 (already bundled with `fastapi[standard]`)
- **Interactivity**: HTMX 2.x (via CDN) — partial page updates, modal forms, delete with confirmation
- **Styling**: Bootstrap 5.3 (via CDN) — responsive layout, tables, modal dialogs
- **Form parsing**: `python-multipart` (required for FastAPI `Form()`)

## Architecture

### URL namespace
All GUI routes use `/ui/` prefix to avoid conflicts with existing JSON API:

| GUI route | API route (unchanged) |
|---|---|
| `GET /ui/grape-varieties` | `GET /grape-varieties/` |
| `GET /ui/ava` | `GET /ava/` |
| ... | ... |

### Shared Jinja2 environment
New file `app/templates.py`:
```python
from pathlib import Path
from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
```

### `app/main.py` modifications
- Mount `app/static/` at `/static`
- Import and register all 6 GUI routers

## Directory Structure (new files)

```
winedb/app/
├── templates.py                          # shared Jinja2Templates instance
├── static/app.css                        # minimal CSS overrides
├── templates/
│   ├── base.html                         # Bootstrap 5 layout, sidebar nav, HTMX script
│   ├── partials/                         # HTMX fragment templates
│   │   ├── flash.html
│   │   ├── table_row_grape_variety.html
│   │   ├── table_row_ava.html
│   │   ├── table_row_person.html
│   │   ├── table_row_vineyard.html
│   │   ├── table_row_winery.html
│   │   ├── table_row_wine.html
│   │   ├── form_grape_variety.html
│   │   ├── form_ava.html
│   │   ├── form_person.html
│   │   ├── form_vineyard.html
│   │   ├── form_winery.html
│   │   ├── form_wine.html
│   │   └── vineyard_source_row.html
│   ├── grape_varieties/list.html
│   ├── ava/list.html
│   ├── persons/list.html
│   ├── vineyards/list.html
│   ├── wineries/list.html
│   └── wines/list.html
└── routers/gui/
    ├── __init__.py
    ├── grape_varieties.py
    ├── ava.py
    ├── persons.py
    ├── vineyards.py
    ├── wineries.py
    └── wines.py
```

## HTMX Interaction Patterns

### Modal create/edit
1. "New" / "Edit" buttons fire `hx-get="/ui/<entity>/modal/new"` -> server returns modal HTML -> injected into `#modal-container` div
2. Form submits via `hx-post` -> server returns updated table row partial on success, or re-renders form with errors on 422
3. On success, server sets `HX-Trigger: closeModal` response header -> JS listener clears `#modal-container`

### Delete with confirmation
```html
hx-delete="/ui/grape-varieties/{{ gv.id }}"
hx-target="#gv-row-{{ gv.id }}"
hx-swap="outerHTML"
hx-confirm="Delete '{{ gv.name }}'?"
```
Server returns `HTMLResponse("")` -> HTMX replaces row outerHTML with empty string.

### Form POST for updates (no PATCH needed)
- Create: `POST /ui/<entity>`
- Update: `POST /ui/<entity>/{id}/edit`
- Delete: HTMX `DELETE /ui/<entity>/{id}`

### Wine: dynamic vineyard source rows
"Add Vineyard Source" button fires `hx-get="/ui/wines/vineyard-source-row"` -> appends a new row with `vineyard_id[]`, `block_name[]`, `pct_blend[]` inputs. On save, handler does a replace-all: delete existing `WineVineyardSource` rows for that wine, re-insert from submitted lists.

### AVA/Winery/GrapeVariety selects in forms
For entities with bounded counts (AVAs < 1000), pass full list in template context (no autocomplete needed).

## GUI Router Pattern (per entity)

```python
router = APIRouter(prefix="/ui/grape-varieties", tags=["UI - Grape Varieties"])

GET  ""                    -> list page (full HTML)
GET  "/modal/new"          -> create modal fragment
GET  "/modal/{id}"         -> edit modal fragment (pre-populated)
POST ""                    -> create -> returns new table row partial
POST "/{id}/edit"          -> update -> returns updated row partial
DELETE "/{id}"             -> delete -> returns empty 200 (row removed by HTMX)
```

All routes reuse existing `app/crud/<entity>.py` functions directly.

## Error Handling

- **Validation (422)**: Catch `pydantic.ValidationError`, build `errors: dict[str, str]`, re-render form partial with `status_code=422`
- **Integrity errors**: Catch `sqlalchemy.exc.IntegrityError`, render form with `errors["__all__"] = "..."` message
- **404**: Return 404 response for missing records

## Files to Modify

| File | Change |
|---|---|
| `winedb/pyproject.toml` | Add `python-multipart` dependency if not present |
| `winedb/app/main.py` | Mount `/static`, register 6 GUI routers |
| `winedb/app/crud/wine.py` | Add `replace_vineyard_sources(session, wine_id, sources)` helper |

## Implementation Order

1. **Infrastructure**: `templates.py`, `static/app.css`, `base.html`, `routers/gui/__init__.py`, update `main.py`
2. **GrapeVariety** (no FKs -- establishes pattern for all other entities)
3. **AVA** (self-referential FK)
4. **Person** (no FKs)
5. **Vineyard** (depends on AVA)
6. **Winery** (depends on AVA)
7. **Wine** (most complex: 3 FKs + dynamic vineyard source rows)

## Verification

```bash
cd winedb
uv add python-multipart
uv run alembic upgrade head
uv run winedb import data/seed/
uv run uvicorn app.main:app --reload

# Visit in browser:
# http://localhost:8000/ui/grape-varieties  -> list page
# http://localhost:8000/ui/wines            -> wine list
# Test: create, edit, delete each entity
# Test: wine with multiple vineyard sources
# Verify JSON API unchanged: http://localhost:8000/docs
```
