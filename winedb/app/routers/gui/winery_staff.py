from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.winery_staff as crud

router = APIRouter(prefix="/ui/winery-staff", tags=["UI - Winery staff"])


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by, sort_dir = "winery_name", "asc"
    items = await crud.get_winery_staff(db, sort_by=sort_by, sort_dir=sort_dir, limit=500)
    return templates.TemplateResponse(
        request,
        "winery_staff/list.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    winery_search: str = "",
    person_search: str = "",
    role_search: str = "",
    sort_by: str = "winery_name",
    sort_dir: str = "asc",
):
    items = await crud.get_winery_staff(
        db,
        winery_search=winery_search or None,
        person_search=person_search or None,
        role_search=role_search or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    return templates.TemplateResponse(
        request,
        "winery_staff/_rows.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )
