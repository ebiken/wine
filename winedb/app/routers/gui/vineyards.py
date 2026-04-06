from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.vineyard as crud
import app.crud.ava as ava_crud
from app.schemas.vineyard import VineyardCreate, VineyardUpdate

router = APIRouter(prefix="/ui/vineyards", tags=["UI - Vineyards"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by, sort_dir = "name", "asc"
    items = await crud.get_vineyards(db, sort_by=sort_by, sort_dir=sort_dir, limit=500)
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "vineyards/list.html",
        {"items": items, "all_avas": all_avas, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = "",
    ava_id: str = "",
    established_year: str = "",
    soil_type: str = "",
    sort_by: str = "name",
    sort_dir: str = "asc",
):
    items = await crud.get_vineyards(
        db,
        name=name or None,
        ava_id=int(ava_id) if ava_id else None,
        established_year=int(established_year) if established_year else None,
        soil_type=soil_type or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "vineyards/_table.html",
        {"items": items, "all_avas": all_avas, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/modal/new", response_class=HTMLResponse)
async def new_modal(request: Request, db: AsyncSession = Depends(get_db)):
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/form_vineyard.html",
        {"item": None, "errors": {}, "all_avas": all_avas},
    )


@router.get("/modal/{item_id}", response_class=HTMLResponse)
async def edit_modal(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    item = await crud.get_vineyard(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    all_avas = await ava_crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/form_vineyard.html",
        {"item": item, "errors": {}, "all_avas": all_avas},
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    ava_id: str = Form(...),
    latitude: str = Form(""),
    longitude: str = Form(""),
    elevation_ft_low: str = Form(""),
    elevation_ft_high: str = Form(""),
    total_acres: str = Form(""),
    soil_type: str = Form(""),
    established_year: str = Form(""),
    description: str = Form(""),
):
    all_avas = await ava_crud.get_avas(db, limit=500)
    try:
        data = VineyardCreate(
            name=name,
            ava_id=int(ava_id),
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            elevation_ft_low=int(elevation_ft_low) if elevation_ft_low else None,
            elevation_ft_high=int(elevation_ft_high) if elevation_ft_high else None,
            total_acres=int(total_acres) if total_acres else None,
            soil_type=soil_type or None,
            established_year=int(established_year) if established_year else None,
            description=description or None,
        )
        item = await crud.create_vineyard(db, data)
        return templates.TemplateResponse(
            request, "partials/table_row_vineyard.html",
            {"item": item, "all_avas": all_avas},
            headers={"HX-Trigger": "closeModal"},
        )
    except (ValidationError, ValueError) as e:
        errors = {}
        if isinstance(e, ValidationError):
            errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        else:
            errors = {"__all__": str(e)}
        return templates.TemplateResponse(
            request, "partials/form_vineyard.html",
            {"item": None, "errors": errors, "all_avas": all_avas},
            status_code=422,
        )


@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def update(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    ava_id: str = Form(...),
    latitude: str = Form(""),
    longitude: str = Form(""),
    elevation_ft_low: str = Form(""),
    elevation_ft_high: str = Form(""),
    total_acres: str = Form(""),
    soil_type: str = Form(""),
    established_year: str = Form(""),
    description: str = Form(""),
):
    item = await crud.get_vineyard(db, item_id)
    all_avas = await ava_crud.get_avas(db, limit=500)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    try:
        data = VineyardUpdate(
            name=name,
            ava_id=int(ava_id),
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            elevation_ft_low=int(elevation_ft_low) if elevation_ft_low else None,
            elevation_ft_high=int(elevation_ft_high) if elevation_ft_high else None,
            total_acres=int(total_acres) if total_acres else None,
            soil_type=soil_type or None,
            established_year=int(established_year) if established_year else None,
            description=description or None,
        )
        item = await crud.update_vineyard(db, item_id, data)
        return templates.TemplateResponse(
            request, "partials/table_row_vineyard.html",
            {"item": item, "all_avas": all_avas},
            headers={"HX-Trigger": "closeModal"},
        )
    except (ValidationError, ValueError) as e:
        errors = {}
        if isinstance(e, ValidationError):
            errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        else:
            errors = {"__all__": str(e)}
        return templates.TemplateResponse(
            request, "partials/form_vineyard.html",
            {"item": item, "errors": errors, "all_avas": all_avas},
            status_code=422,
        )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_vineyard(db, item_id)
    return HTMLResponse("")
