from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.grape_variety as crud
from app.schemas.grape_variety import GrapeVarietyCreate, GrapeVarietyUpdate

router = APIRouter(prefix="/ui/grape-varieties", tags=["UI - Grape Varieties"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by, sort_dir = "name", "asc"
    items = await crud.get_grape_varieties(db, sort_by=sort_by, sort_dir=sort_dir, limit=500)
    return templates.TemplateResponse(
        request, "grape_varieties/list.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = "",
    color: str = "",
    origin_region: str = "",
    sort_by: str = "name",
    sort_dir: str = "asc",
):
    items = await crud.get_grape_varieties(
        db,
        name=name or None,
        color=color or None,
        origin_region=origin_region or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    return templates.TemplateResponse(
        request, "grape_varieties/_table.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/modal/new", response_class=HTMLResponse)
async def new_modal(request: Request):
    return templates.TemplateResponse(
        request, "partials/form_grape_variety.html",
        {"item": None, "errors": {}},
    )


@router.get("/modal/{item_id}", response_class=HTMLResponse)
async def edit_modal(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    item = await crud.get_grape_variety(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse(
        request, "partials/form_grape_variety.html",
        {"item": item, "errors": {}},
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
    key: str = Form(...),
    name: str = Form(...),
    color: str = Form(""),
    origin_region: str = Form(""),
    name_synonyms: str = Form(""),
):
    try:
        data = GrapeVarietyCreate(
            key=key.strip(),
            name=name,
            color=color or None,
            origin_region=origin_region or None,
            name_synonyms=name_synonyms or None,
        )
        item = await crud.create_grape_variety(db, data)
        return templates.TemplateResponse(
            request, "partials/table_row_grape_variety.html",
            {"item": item},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_grape_variety.html",
            {"item": None, "errors": errors},
            status_code=422,
        )
    except IntegrityError:
        return templates.TemplateResponse(
            request, "partials/form_grape_variety.html",
            {"item": None, "errors": {"__all__": "A grape variety with that key or name already exists."}},
            status_code=422,
        )


@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def update(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    color: str = Form(""),
    origin_region: str = Form(""),
    name_synonyms: str = Form(""),
):
    item = await crud.get_grape_variety(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    try:
        data = GrapeVarietyUpdate(
            name=name,
            color=color or None,
            origin_region=origin_region or None,
            name_synonyms=name_synonyms or None,
        )
        item = await crud.update_grape_variety(db, item_id, data)
        return templates.TemplateResponse(
            request, "partials/table_row_grape_variety.html",
            {"item": item},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_grape_variety.html",
            {"item": item, "errors": errors},
            status_code=422,
        )
    except IntegrityError:
        return templates.TemplateResponse(
            request, "partials/form_grape_variety.html",
            {"item": item, "errors": {"__all__": "A grape variety with that key or name already exists."}},
            status_code=422,
        )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_grape_variety(db, item_id)
    return HTMLResponse("")
