from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.wine as crud
import app.crud.winery as winery_crud
import app.crud.ava as ava_crud
import app.crud.grape_variety as gv_crud
import app.crud.vineyard as vineyard_crud
from app.schemas.wine import WineCreate, WineUpdate

router = APIRouter(prefix="/ui/wines", tags=["UI - Wines"])


async def _get_form_options(db: AsyncSession) -> dict:
    wineries = await winery_crud.get_wineries(db, limit=500)
    all_avas = await ava_crud.get_avas(db, limit=500)
    grape_varieties = await gv_crud.get_grape_varieties(db, limit=500)
    vineyards = await vineyard_crud.get_vineyards(db, limit=500)
    return {
        "wineries": wineries,
        "all_avas": all_avas,
        "grape_varieties": grape_varieties,
        "vineyards": vineyards,
    }


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by = "vintage_year"
    sort_dir = "desc"
    items = await crud.get_wines(db, sort_by=sort_by, sort_dir=sort_dir, limit=500)
    opts = await _get_form_options(db)
    return templates.TemplateResponse(
        request, "wines/list.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir, **opts},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    label_name: str = "",
    winery_id: str = "",
    ava_id: str = "",
    vintage_year: str = "",
    grape_variety_id: str = "",
    sort_by: str = "vintage_year",
    sort_dir: str = "desc",
):
    items = await crud.get_wines(
        db,
        label_name=label_name or None,
        winery_id=int(winery_id) if winery_id else None,
        ava_id=int(ava_id) if ava_id else None,
        vintage_year=int(vintage_year) if vintage_year else None,
        grape_variety_id=int(grape_variety_id) if grape_variety_id else None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    opts = await _get_form_options(db)
    return templates.TemplateResponse(
        request, "wines/_table.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir, **opts},
    )


@router.get("/modal/new", response_class=HTMLResponse)
async def new_modal(request: Request, db: AsyncSession = Depends(get_db)):
    opts = await _get_form_options(db)
    return templates.TemplateResponse(
        request, "partials/form_wine.html",
        {"item": None, "errors": {}, **opts},
    )


@router.get("/vineyard-source-row", response_class=HTMLResponse)
async def vineyard_source_row(request: Request, db: AsyncSession = Depends(get_db)):
    vineyards = await vineyard_crud.get_vineyards(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/vineyard_source_row.html",
        {"source": None, "vineyards": vineyards},
    )


@router.get("/modal/{item_id}", response_class=HTMLResponse)
async def edit_modal(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    item = await crud.get_wine(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    opts = await _get_form_options(db)
    return templates.TemplateResponse(
        request, "partials/form_wine.html",
        {"item": item, "errors": {}, **opts},
    )


def _parse_sources(
    vineyard_ids: list[str],
    block_names: list[str],
    pct_blends: list[str],
) -> list[dict]:
    sources = []
    for vid, bname, pct in zip(vineyard_ids, block_names, pct_blends):
        if not vid:
            continue
        sources.append({
            "vineyard_id": int(vid),
            "block_name": bname or None,
            "pct_blend": float(pct) if pct else None,
        })
    return sources


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
    winery_id: str = Form(...),
    label_name: str = Form(...),
    vintage_year: str = Form(...),
    grape_variety_id: str = Form(""),
    ava_id: str = Form(""),
    alcohol_pct: str = Form(""),
    production_cases: str = Form(""),
    release_date: str = Form(""),
    tasting_notes: str = Form(""),
    winery_description: str = Form(""),
    description: str = Form(""),
    vineyard_id: Annotated[list[str], Form()] = [],
    block_name: Annotated[list[str], Form()] = [],
    pct_blend: Annotated[list[str], Form()] = [],
):
    opts = await _get_form_options(db)
    try:
        data = WineCreate(
            winery_id=int(winery_id),
            label_name=label_name,
            vintage_year=int(vintage_year),
            grape_variety_id=int(grape_variety_id) if grape_variety_id else None,
            ava_id=int(ava_id) if ava_id else None,
            alcohol_pct=float(alcohol_pct) if alcohol_pct else None,
            production_cases=int(production_cases) if production_cases else None,
            release_date=release_date or None,
            tasting_notes=tasting_notes or None,
            winery_description=winery_description or None,
            description=description or None,
        )
        item = await crud.create_wine(db, data)
        sources = _parse_sources(vineyard_id, block_name, pct_blend)
        if sources:
            await crud.replace_vineyard_sources(db, item.id, sources)
            item = await crud.get_wine(db, item.id)
        return templates.TemplateResponse(
            request, "partials/table_row_wine.html",
            {"item": item, **opts},
            headers={"HX-Trigger": "closeModal"},
        )
    except (ValidationError, ValueError) as e:
        errors = {}
        if isinstance(e, ValidationError):
            errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        else:
            errors = {"__all__": str(e)}
        return templates.TemplateResponse(
            request, "partials/form_wine.html",
            {"item": None, "errors": errors, **opts},
            status_code=422,
        )


@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def update(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    winery_id: str = Form(...),
    label_name: str = Form(...),
    vintage_year: str = Form(...),
    grape_variety_id: str = Form(""),
    ava_id: str = Form(""),
    alcohol_pct: str = Form(""),
    production_cases: str = Form(""),
    release_date: str = Form(""),
    tasting_notes: str = Form(""),
    winery_description: str = Form(""),
    description: str = Form(""),
    vineyard_id: Annotated[list[str], Form()] = [],
    block_name: Annotated[list[str], Form()] = [],
    pct_blend: Annotated[list[str], Form()] = [],
):
    item = await crud.get_wine(db, item_id)
    opts = await _get_form_options(db)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    try:
        data = WineUpdate(
            label_name=label_name,
            vintage_year=int(vintage_year),
            grape_variety_id=int(grape_variety_id) if grape_variety_id else None,
            ava_id=int(ava_id) if ava_id else None,
            alcohol_pct=float(alcohol_pct) if alcohol_pct else None,
            production_cases=int(production_cases) if production_cases else None,
            release_date=release_date or None,
            tasting_notes=tasting_notes or None,
            winery_description=winery_description or None,
            description=description or None,
        )
        item = await crud.update_wine(db, item_id, data)
        sources = _parse_sources(vineyard_id, block_name, pct_blend)
        await crud.replace_vineyard_sources(db, item_id, sources)
        item = await crud.get_wine(db, item_id)
        return templates.TemplateResponse(
            request, "partials/table_row_wine.html",
            {"item": item, **opts},
            headers={"HX-Trigger": "closeModal"},
        )
    except (ValidationError, ValueError) as e:
        errors = {}
        if isinstance(e, ValidationError):
            errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        else:
            errors = {"__all__": str(e)}
        return templates.TemplateResponse(
            request, "partials/form_wine.html",
            {"item": item, "errors": errors, **opts},
            status_code=422,
        )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_wine(db, item_id)
    return HTMLResponse("")
