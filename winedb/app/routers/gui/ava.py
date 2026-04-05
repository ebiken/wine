from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.ava as crud
from app.schemas.ava import AVACreate, AVAUpdate

router = APIRouter(prefix="/ui/ava", tags=["UI - AVA"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    items = await crud.get_avas(db, limit=500)
    all_avas = items  # reuse for parent select
    return templates.TemplateResponse(
        request, "ava/list.html", {"items": items, "all_avas": all_avas}
    )


@router.get("/modal/new", response_class=HTMLResponse)
async def new_modal(request: Request, db: AsyncSession = Depends(get_db)):
    all_avas = await crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/form_ava.html",
        {"item": None, "errors": {}, "all_avas": all_avas},
    )


@router.get("/modal/{item_id}", response_class=HTMLResponse)
async def edit_modal(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    item = await crud.get_ava(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    all_avas = await crud.get_avas(db, limit=500)
    return templates.TemplateResponse(
        request, "partials/form_ava.html",
        {"item": item, "errors": {}, "all_avas": all_avas},
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    state: str = Form(...),
    short_name: str = Form(""),
    parent_ava_id: str = Form(""),
    county: str = Form(""),
    ttb_approval_date: str = Form(""),
    total_acres: str = Form(""),
    planted_acres: str = Form(""),
    description: str = Form(""),
):
    all_avas = await crud.get_avas(db, limit=500)
    try:
        data = AVACreate(
            name=name,
            state=state,
            short_name=short_name or None,
            parent_ava_id=int(parent_ava_id) if parent_ava_id else None,
            county=county or None,
            ttb_approval_date=ttb_approval_date or None,
            total_acres=int(total_acres) if total_acres else None,
            planted_acres=int(planted_acres) if planted_acres else None,
            description=description or None,
        )
        item = await crud.create_ava(db, data)
        return templates.TemplateResponse(
            request, "partials/table_row_ava.html",
            {"item": item, "all_avas": all_avas},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_ava.html",
            {"item": None, "errors": errors, "all_avas": all_avas},
            status_code=422,
        )
    except IntegrityError:
        return templates.TemplateResponse(
            request, "partials/form_ava.html",
            {"item": None, "errors": {"__all__": "An AVA with that name already exists."}, "all_avas": all_avas},
            status_code=422,
        )


@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def update(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    name: str = Form(...),
    state: str = Form(...),
    short_name: str = Form(""),
    parent_ava_id: str = Form(""),
    county: str = Form(""),
    ttb_approval_date: str = Form(""),
    total_acres: str = Form(""),
    planted_acres: str = Form(""),
    description: str = Form(""),
):
    item = await crud.get_ava(db, item_id)
    all_avas = await crud.get_avas(db, limit=500)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    try:
        data = AVAUpdate(
            name=name,
            state=state,
            short_name=short_name or None,
            parent_ava_id=int(parent_ava_id) if parent_ava_id else None,
            county=county or None,
            ttb_approval_date=ttb_approval_date or None,
            total_acres=int(total_acres) if total_acres else None,
            planted_acres=int(planted_acres) if planted_acres else None,
            description=description or None,
        )
        item = await crud.update_ava(db, item_id, data)
        return templates.TemplateResponse(
            request, "partials/table_row_ava.html",
            {"item": item, "all_avas": all_avas},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_ava.html",
            {"item": item, "errors": errors, "all_avas": all_avas},
            status_code=422,
        )
    except IntegrityError:
        return templates.TemplateResponse(
            request, "partials/form_ava.html",
            {"item": item, "errors": {"__all__": "An AVA with that name already exists."}, "all_avas": all_avas},
            status_code=422,
        )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_ava(db, item_id)
    return HTMLResponse("")
