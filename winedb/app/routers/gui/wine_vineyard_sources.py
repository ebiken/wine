from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.templates import templates
import app.crud.wine_vineyard_source as crud

router = APIRouter(
    prefix="/ui/wine-vineyard-sources",
    tags=["UI - Wine vineyard sources"],
)


@router.get("", response_class=HTMLResponse)
async def list_page(request: Request, db: AsyncSession = Depends(get_db)):
    sort_by, sort_dir = "winery_name", "asc"
    items = await crud.get_wine_vineyard_sources(
        db, sort_by=sort_by, sort_dir=sort_dir, limit=500
    )
    return templates.TemplateResponse(
        request,
        "wine_vineyard_sources/list.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )


@router.get("/rows", response_class=HTMLResponse)
async def list_rows(
    request: Request,
    db: AsyncSession = Depends(get_db),
    label_search: str = "",
    winery_search: str = "",
    vineyard_search: str = "",
    sort_by: str = "winery_name",
    sort_dir: str = "asc",
):
    items = await crud.get_wine_vineyard_sources(
        db,
        label_search=label_search or None,
        winery_search=winery_search or None,
        vineyard_search=vineyard_search or None,
        sort_by=sort_by,
        sort_dir=sort_dir,
        limit=500,
    )
    return templates.TemplateResponse(
        request,
        "wine_vineyard_sources/_rows.html",
        {"items": items, "sort_by": sort_by, "sort_dir": sort_dir},
    )
