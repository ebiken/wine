from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.person as crud
from app.schemas.person import PersonCreate, PersonUpdate

router = APIRouter(prefix="/ui/persons", tags=["UI - Persons"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    items = await crud.get_persons(db, limit=500)
    return templates.TemplateResponse(
        request, "persons/list.html", {"items": items}
    )


@router.get("/modal/new", response_class=HTMLResponse)
async def new_modal(request: Request):
    return templates.TemplateResponse(
        request, "partials/form_person.html",
        {"item": None, "errors": {}},
    )


@router.get("/modal/{item_id}", response_class=HTMLResponse)
async def edit_modal(item_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    item = await crud.get_person(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    return templates.TemplateResponse(
        request, "partials/form_person.html",
        {"item": item, "errors": {}},
    )


@router.post("", response_class=HTMLResponse)
async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    birth_year: str = Form(""),
    nationality: str = Form(""),
    biography: str = Form(""),
):
    try:
        data = PersonCreate(
            first_name=first_name,
            last_name=last_name,
            birth_year=int(birth_year) if birth_year else None,
            nationality=nationality or None,
            biography=biography or None,
        )
        item = await crud.create_person(db, data)
        return templates.TemplateResponse(
            request, "partials/table_row_person.html",
            {"item": item},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_person.html",
            {"item": None, "errors": errors},
            status_code=422,
        )


@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def update(
    item_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    first_name: str = Form(...),
    last_name: str = Form(...),
    birth_year: str = Form(""),
    nationality: str = Form(""),
    biography: str = Form(""),
):
    item = await crud.get_person(db, item_id)
    if item is None:
        return HTMLResponse("Not found", status_code=404)
    try:
        data = PersonUpdate(
            first_name=first_name,
            last_name=last_name,
            birth_year=int(birth_year) if birth_year else None,
            nationality=nationality or None,
            biography=biography or None,
        )
        item = await crud.update_person(db, item_id, data)
        return templates.TemplateResponse(
            request, "partials/table_row_person.html",
            {"item": item},
            headers={"HX-Trigger": "closeModal"},
        )
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return templates.TemplateResponse(
            request, "partials/form_person.html",
            {"item": item, "errors": errors},
            status_code=422,
        )


@router.delete("/{item_id}", response_class=HTMLResponse)
async def delete(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_person(db, item_id)
    return HTMLResponse("")
