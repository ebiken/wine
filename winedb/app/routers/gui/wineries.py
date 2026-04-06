from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.winery as crud
import app.crud.ava as ava_crud
from app.schemas.winery import WineryCreate, WineryUpdate

router = APIRouter(prefix="/ui/wineries", tags=["UI - Wineries"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by, sort_dir = "name", "asc"
    items = await crud.get_wineries(db, sort_by=sort_by, sort_dir=sort_dir, limit=500)
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "wineries/list.html",
        {"items": items, "all_avas": all_avas, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = "",
    ava_id: str = "",
    location: str = "",
    established_year: str = "",
    is_negociant: str = "",
    sort_by: str = "name",
    sort_dir: str = "asc",
):
    items = await crud.get_wineries(
        db,
        name=name or None,
        ava_id=int(ava_id) if ava_id else None,
        location=location or None,
        established_year=int(established_year) if established_year else None,
        is_negociant={"true": True, "false": False}.get(is_negociant),
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "wineries/_table.html",
        {"items": items, "all_avas": all_avas, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/modal/new", response_class=HTMLResponse)
async def new_modal(request: Request, db: AsyncSession = Depends(get_db)):
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/form_winery.html",
        {"item": None, "errors": {}, "all_avas": all_avas},
    )


@router.get("/modal/{item_id}", response_class=HTMLResponse)
async def edit_modal(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    item = await crud.get_winery(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/form_winery.html",
        {"item": item, "errors": {}, "all_avas": all_avas},
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    established_year: str = Form(""),
    location_city: str = Form(""),
    location_state: str = Form(""),
    ava_id: str = Form(""),
    is_negociant: str = Form(""),
    website: str = Form(""),
    description: str = Form(""),
):
    all_avas = await ava_crud.get_avas(db, limit=500)
    try:
        data = WineryCreate(
            name=name,
            established_year=int(established_year) if established_year else None,
            location_city=location_city or None,
            location_state=location_state or None,
            ava_id=int(ava_id) if ava_id else None,
            is_negociant=is_negociant == "true",
            website=website or None,
            description=description or None,
        )
        item = await crud.create_winery(db, data)
        return templates.TemplateResponse(
            request, "partials/table_row_winery.html",
            {"item": item, "all_avas": all_avas},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_winery.html",
            {"item": None, "errors": errors, "all_avas": all_avas},
            status_code=422,
        )
    except IntegrityError:
        return templates.TemplateResponse(
            request, "partials/form_winery.html",
            {"item": None, "errors": {"__all__": "A winery with that name already exists."}, "all_avas": all_avas},
            status_code=422,
        )


@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def update(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    established_year: str = Form(""),
    location_city: str = Form(""),
    location_state: str = Form(""),
    ava_id: str = Form(""),
    is_negociant: str = Form(""),
    website: str = Form(""),
    description: str = Form(""),
):
    item = await crud.get_winery(db, item_id)
    all_avas = await ava_crud.get_avas(db, limit=500)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    try:
        data = WineryUpdate(
            name=name,
            established_year=int(established_year) if established_year else None,
            location_city=location_city or None,
            location_state=location_state or None,
            ava_id=int(ava_id) if ava_id else None,
            is_negociant=is_negociant == "true",
            website=website or None,
            description=description or None,
        )
        item = await crud.update_winery(db, item_id, data)
        return templates.TemplateResponse(
            request, "partials/table_row_winery.html",
            {"item": item, "all_avas": all_avas},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_winery.html",
            {"item": item, "errors": errors, "all_avas": all_avas},
            status_code=422,
        )
    except IntegrityError:
        return templates.TemplateResponse(
            request, "partials/form_winery.html",
            {"item": item, "errors": {"__all__": "A winery with that name already exists."}, "all_avas": all_avas},
            status_code=422,
        )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_winery(db, item_id)
    return HTMLResponse("")
