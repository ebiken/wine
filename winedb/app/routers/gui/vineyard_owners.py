from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.vineyard_owner as crud

router = APIRouter(prefix="/ui/vineyard-owners", tags=["UI - Vineyard owners"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by, sort_dir = "vineyard_name", "asc"
    items = await crud.get_vineyard_owners(db, sort_by=sort_by, sort_dir=sort_dir, limit=500)
    return templates.TemplateResponse(
        request,
        "vineyard_owners/list.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    vineyard_search: str = "",
    person_search: str = "",
    role_search: str = "",
    sort_by: str = "vineyard_name",
    sort_dir: str = "asc",
):
    items = await crud.get_vineyard_owners(
        db,
        vineyard_search=vineyard_search or None,
        person_search=person_search or None,
        role_search=role_search or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    return templates.TemplateResponse(
        request,
        "vineyard_owners/_rows.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )
