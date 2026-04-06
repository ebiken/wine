# WineDb GUI: Filter & Sort

## Context

The wines list at `/ui/wines` shows all wines in a static table with no way to narrow results or change ordering. `get_wines()` already supports filtering by `winery_id`, `ava_id`, `vintage_year`, `grape_variety_id`, and `label_name`, but the UI route ignores those params. Sorting is hardcoded to `vintage_year DESC, label_name`.

## Approach

Use HTMX to reload only `<tbody id="wine-tbody">` when filters change or a column header is clicked. A new endpoint `GET /ui/wines/rows` returns the partial rows with filter+sort applied. The full page load (`GET /ui/wines`) continues to work as before.

## Changes

### 1. `app/crud/wine.py`

Add `sort_by: str = "vintage_year"` and `sort_dir: str = "desc"` params to `get_wines()`.

Supported sort columns: `vintage_year`, `label_name`, `alcohol_pct`, `production_cases`.

Replace hardcoded `.order_by(...)` with dynamic ordering:

```python
SORTABLE = {"vintage_year", "label_name", "alcohol_pct", "production_cases"}
col = getattr(Wine, sort_by if sort_by in SORTABLE else "vintage_year")
order = col.desc() if sort_dir == "desc" else col.asc()
q = q.order_by(order)
```

### 2. `app/routers/gui/wines.py`

Add `GET /ui/wines/rows` endpoint:

- Accepts query params: `label_name`, `winery_id`, `ava_id`, `vintage_year`, `grape_variety_id`, `sort_by`, `sort_dir`
- Calls `crud.get_wines()` with those params
- Returns template `wines/_rows.html` with `items` + form options

The existing `list_page` (`GET /ui/wines`) also passes `sort_by` and `sort_dir` to the template context for initial render.

### 3. New `app/templates/wines/_rows.html`

Extracted tbody partial:

```html
{% for item in items %}
  {% include "partials/table_row_wine.html" %}
{% endfor %}
{% if not items %}
<tr><td colspan="8" class="text-muted">No wines found.</td></tr>
{% endif %}
```

### 4. `app/templates/wines/list.html`

**Filter bar** (Bootstrap row above the table):

- Text input: `label_name`
- Select: `winery_id`
- Number input: `vintage_year`
- Select: `grape_variety_id`
- Select: `ava_id`
- "Clear" button

Form uses HTMX to reload `#wine-tbody` on input change. Hidden inputs `sort_by` / `sort_dir` carry current sort state through filter changes.

**Sortable column headers** for Label, Vintage, Alcohol:

- Clicking a header sends HTMX GET to `/ui/wines/rows` including filter values and toggled sort params
- Direction indicator (v/^) shown on the active sort column

**tbody** uses the new partial:

```html
<tbody id="wine-tbody">
  {% include "wines/_rows.html" %}
</tbody>
```

## Verification

1. `cd winedb && uv run fastapi dev app/main.py`
2. Open `http://localhost:8000/ui/wines`
3. Type in label filter -> table updates without page reload
4. Change winery dropdown -> rows update
5. Click "Vintage" header -> sorts ascending; click again -> descending (indicator flips)
6. Click "Clear" -> all filters reset, default sort restored
